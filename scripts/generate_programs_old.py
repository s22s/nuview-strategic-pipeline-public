import hashlib
import json
import logging
import sys
from pathlib import Path

# --- CONFIGURATION ---
sys.path.append(str(Path(__file__).parent.parent))
try:
    from config.keywords import IMPLIED_DEMAND, NEGATIVE_FILTERS, PILLARS
    from config.keywords_multilingual import ALL_GLOBAL_TRIGGERS
    from scripts.utils.currency import to_usd
except ImportError:
    # Fallback defaults if config is missing
    PILLARS = {"DaaS": ["lidar"]}
    IMPLIED_DEMAND = []
    NEGATIVE_FILTERS = []
    ALL_GLOBAL_TRIGGERS = []
    def to_usd(val, curr): return 0

# --- LOGIC ---
def generate_id(url): return hashlib.md5(str(url).encode()).hexdigest()

def calculate_score(text):
    text = text.lower()
    if any(bad in text for bad in NEGATIVE_FILTERS):
        return 0
    score = 0
    if any(x in text for x in ["geiger", "single photon", "spl", "8ppm"]):
        score += 40
    if any(x in text for x in ["lidar", "3dep", "constellation"]):
        score += 25
    if any(x in text for x in ALL_GLOBAL_TRIGGERS):
        score += 20
    if any(x in text for x in IMPLIED_DEMAND):
        score += 15
    if any(x in text for x in ["mapping", "survey"]):
        score += 10
    return min(100, score)


def determine_segment(text):
    text = text.lower()
    if any(k in text for k in PILLARS.get("Space Systems", [])):
        return "Space Systems"
    if any(k in text for k in PILLARS.get("Spatial Intelligence", [])):
        return "Spatial Intelligence"
    return "DaaS"


def determine_fiscal_status(title, description):
    text = (title + " " + description).lower()
    # Forecast triggers: Money that is coming LATER
    forecast_triggers = [
        "sources sought", "rfi", "request for information",
        "pre-solicitation", "forecast", "future", "planning"
    ]
    if any(x in text for x in forecast_triggers):
        return "Forecast"
    # Active triggers: Money that is here NOW
    return "Active Budget"

# --- EXECUTION ---
raw_path = Path("data/raw/all_opportunities.json")
out_path = Path("data/processed/opportunities.json")
funding_path = Path("data/processed/funding_flow.json")

if not raw_path.exists():
    print("No raw data.")
    exit(0)

with open(raw_path) as f:
    raw = json.load(f)

processed = []
seen_ids = set()

# For Sankey / Funding Calculation
flows = {
    "regions": {},
    "countries": {},
    "agencies": {},
    "segments": {"Space Systems": 0, "Spatial Intelligence": 0, "DaaS": 0}
}
stats = {"total_forecast": 0, "total_active": 0, "by_country": {}}

for item in raw:
    full_text = (str(item.get('title','')) + " " + str(item.get('description',''))).lower()
    score = calculate_score(full_text)

    if score > 0:
        # 1. Currency Normalization
        val_raw = item.get('value', 0)
        currency = item.get('currency', 'USD')
        try:
            val = to_usd(val_raw, currency)
        except Exception as e:
            if isinstance(e, (KeyboardInterrupt, SystemExit)):
                raise
            logging.exception("Failed currency conversion for item: %s", e)
            val = 0

        # 2. Deduplication
        key = f"{item['title'][:20]}-{val}"
        if key in seen_ids:
            continue
        seen_ids.add(key)

        # 3. Classifications
        segment = determine_segment(full_text)
        status = determine_fiscal_status(item.get('title', ''), item.get('description', ''))
        country = item.get('country', 'Global')
        agency = item.get('agency', 'Unknown Agency')

        # 4. Funding Aggregation (The "Money Flow")
        if country not in stats["by_country"]:
            stats["by_country"][country] = {"forecast": 0, "active": 0}

        if status == "Forecast":
            stats["total_forecast"] += val
            stats["by_country"][country]["forecast"] += val
        else:
            stats["total_active"] += val
            stats["by_country"][country]["active"] += val

        # Build Flow Hierarchy for Sankey: Country -> Agency -> Segment
        if country not in flows["countries"]:
            flows["countries"][country] = 0
        flows["countries"][country] += val

        agency_key = f"{country}::{agency}"  # Unique agency per country
        if agency_key not in flows["agencies"]:
            flows["agencies"][agency_key] = {
                "val": 0, "parent": country, "segment_split": {}
            }
        flows["agencies"][agency_key]["val"] += val

        if segment not in flows["agencies"][agency_key]["segment_split"]:
            flows["agencies"][agency_key]["segment_split"][segment] = 0
        flows["agencies"][agency_key]["segment_split"][segment] += val

        processed.append({
            "id": generate_id(item.get('url')),
            "title": item.get('title'),
            "agency": agency,
            "country": country,
            "value": val,
            "value_fmt": f"${val:,.0f}",
            "status": status, # New field for dashboard
            "close_date": item.get('close_date', ''),
            "url": item.get('url'),
            "dna_score": score,
            "segment": segment,
            "category": item.get('category', segment),
            "urgency": 50
        })

# --- BUILD SANKEY JSON ---
# Nodes: Index list of all entities
# Links: Source Index -> Target Index -> Value
label_list = []
source_list = []
target_list = []
value_list = []
color_list = []

# 1. Add Segments (Right side)
seg_map = {}
for i, seg in enumerate(["Space Systems", "Spatial Intelligence", "DaaS"]):
    label_list.append(seg)
    seg_map[seg] = i
    if seg == "Space Systems":
        color_list.append("#dc2626")
    elif seg == "Spatial Intelligence":
        color_list.append("#2563eb")
    else:
        color_list.append("#16a34a")

# 2. Add Countries (Left Side)
country_map = {}
for country, val in flows["countries"].items():
    if val > 0:
        label_list.append(country)
        country_map[country] = len(label_list) - 1
        color_list.append("#475569") # Slate grey for countries

# 3. Add Agencies (Middle) & Build Links
for a_key, data in flows["agencies"].items():
    if data["val"] > 0:
        agency_name = a_key.split("::")[1]
        # Add Agency Node
        label_list.append(agency_name)
        a_idx = len(label_list) - 1
        color_list.append("#64748b") # Lighter grey

        # Link: Country -> Agency
        c_idx = country_map[data["parent"]]
        source_list.append(c_idx)
        target_list.append(a_idx)
        value_list.append(data["val"])

        # Link: Agency -> Segments
        for seg, s_val in data["segment_split"].items():
            if s_val > 0:
                s_idx = seg_map[seg]
                source_list.append(a_idx)
                target_list.append(s_idx)
                value_list.append(s_val)

sankey_payload = {
    "nodes": {"label": label_list, "color": color_list},
    "links": {"source": source_list, "target": target_list, "value": value_list},
    "stats": stats
}

# Save
processed.sort(key=lambda x: x['dna_score'], reverse=True)
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(processed, f, indent=2)
with open(funding_path, 'w') as f:
    json.dump(sankey_payload, f, indent=2)

# --- BUILD PROGRAMS.JSON GROUPED BY CATEGORY ---
programs_path = Path("data/processed/programs.json")
programs_by_category = {
    "funding": [],
    "lidar": [],
    "spaceSystems": [],
    "platform": []
}

# Group opportunities by category (lowercased)
for opp in processed:
    # Add priorityScore field (map from dna_score)
    opp['priorityScore'] = opp.get('dna_score', 0)

    category = opp.get('category', opp.get('segment', 'other'))
    # Create lowercase/camelCase mapping for expected categories
    if category == "Space Systems":
        category_key = "spaceSystems"
    elif category == "DaaS":
        category_key = "platform"
    elif category == "Spatial Intelligence":
        category_key = "platform"
    elif "lidar" in category.lower():
        category_key = "lidar"
    elif "funding" in category.lower():
        category_key = "funding"
    else:
        category_key = "platform"  # Default to platform

    if category_key not in programs_by_category:
        programs_by_category[category_key] = []

    programs_by_category[category_key].append(opp)

# Build final programs structure with meta information
programs_data = {
    "meta": {
        "timestamp": sankey_payload["stats"].get("timestamp", ""),
        "total_opportunities": len(processed),
        "total_active_budget": stats["total_active"],
        "total_forecast": stats["total_forecast"],
        "source": "generate_programs_old.py"
    },
    "programs": programs_by_category
}

with open(programs_path, 'w') as f:
    json.dump(programs_data, f, indent=2)

print("SUCCESS: Generated Intelligence.")
print(f"   ► Opportunities: {len(processed)}")
print(f"   ► Programs File: {programs_path}")
print(f"   ► Global Budget: ${stats['total_active']:,.0f}")
print(f"   ► Forecast Pipeline: ${stats['total_forecast']:,.0f}")
