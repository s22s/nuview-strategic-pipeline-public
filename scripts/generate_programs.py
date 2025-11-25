#!/usr/bin/env python3
"""
NUVIEW Strategic Pipeline - Dashboard Data Generator (FIXED)
Processes live scraper output and generates dashboard-ready data

CRITICAL FIX: Now reads from data/opportunities.json (live scraper output)
              instead of data/raw/all_opportunities.json (old static data)
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ANSI colors
COLOR_GREEN = '\033[92m'
COLOR_BLUE = '\033[94m'
COLOR_RESET = '\033[0m'


def log_info(msg):
    print(f"{COLOR_BLUE}ℹ️  {msg}{COLOR_RESET}")


def log_success(msg):
    print(f"{COLOR_GREEN}✅ {msg}{COLOR_RESET}")


# --- Configuration ---
try:
    from config.keywords import IMPLIED_DEMAND, NEGATIVE_FILTERS, PILLARS
    from config.keywords_multilingual import ALL_GLOBAL_TRIGGERS
except ImportError:
    PILLARS = {"DaaS": ["lidar", "3dep"]}
    IMPLIED_DEMAND = ["mapping", "elevation", "terrain"]
    NEGATIVE_FILTERS = []
    ALL_GLOBAL_TRIGGERS = []


def generate_id(url):
    """Generate unique ID from URL"""
    return hashlib.md5(str(url).encode()).hexdigest()[:12]


def calculate_priority_score(opp):
    """
    Calculate priority score for opportunity (0-100)
    Based on: urgency (30pts) + value_tier (30pts) + category (15pts) + source_verified (10pts) + keywords (15pts)
    """
    score = 0

    # Urgency scoring (30 points max)
    urgency = opp.get('timeline', {}).get('urgency', 'future')
    urgency_scores = {'urgent': 30, 'near': 20, 'future': 10}
    score += urgency_scores.get(urgency, 10)

    # Value tier scoring (30 points max)
    amount = opp.get('funding', {}).get('amountUSD', 0)
    if amount >= 10000000:  # $10M+
        score += 30
    elif amount >= 1000000:  # $1M+
        score += 20
    elif amount > 0:
        score += 10

    # Category scoring (15 points max)
    category = opp.get('category', 'R&D')
    category_scores = {'DaaS': 15, 'Platform': 10, 'R&D': 5}
    score += category_scores.get(category, 5)

    # Source verified (10 points)
    if opp.get('provenance', {}).get('source'):
        score += 10

    # Keyword relevance (15 points max)
    text = (str(opp.get('title', '')) + " " + str(opp.get('description', ''))).lower()
    keyword_score = 0
    if any(k in text for k in ['lidar', '3dep', 'elevation']):
        keyword_score += 15
    elif any(k in text for k in ['mapping', 'geospatial', 'topographic']):
        keyword_score += 10
    elif any(k in text for k in ['survey', 'terrain', 'digital elevation']):
        keyword_score += 5
    score += min(keyword_score, 15)

    return min(score, 100)


def classify_opportunity_type(opp):
    """
    Classify opportunity as Active Budget or Forecast
    Active = Money available now (contracts, awards, active solicitations)
    Forecast = Future opportunities (sources sought, RFI, pre-solicitation)
    """
    title = str(opp.get('title', '')).lower()
    desc = str(opp.get('description', '')).lower()
    text = title + " " + desc

    # Forecast indicators - money coming LATER
    forecast_keywords = [
        'sources sought', 'rfi', 'request for information',
        'pre-solicitation', 'forecast', 'intent to',
        'market research', 'industry day', 'draft rfp',
        'planning', 'upcoming', 'future opportunity'
    ]

    # Active indicators - money available NOW
    active_keywords = [
        'award', 'contract', 'funded', 'active',
        'solicitation', 'rfp', 'request for proposal',
        'bid', 'procurement', 'grant', 'program'
    ]

    # Check forecast first (more specific)
    if any(kw in text for kw in forecast_keywords):
        return 'Forecast'

    # Check active
    if any(kw in text for kw in active_keywords):
        return 'Active'

    # Default: if has budget and near deadline, probably active
    if opp.get('funding', {}).get('amountUSD', 0) > 0:
        urgency = opp.get('timeline', {}).get('urgency')
        if urgency in ['urgent', 'near']:
            return 'Active'

    # Default to forecast if uncertain
    return 'Forecast'


def determine_segment(text):
    """Determine business segment"""
    text = text.lower()
    if any(k in text for k in ['space', 'satellite', 'orbital', 'constellation']):
        return 'Space Systems'
    if any(k in text for k in ['ai', 'analytics', 'intelligence', 'fusion']):
        return 'Spatial Intelligence'
    return 'DaaS'


def main():
    """Main execution"""
    log_info("Starting dashboard data generation...")

    # --- CONFIGURATION ---
    # FIXED: Now reads from live scraper output
    input_path = Path("data/opportunities.json")
    output_path = Path("data/processed/programs.json")
    funding_path = Path("data/processed/funding_flow.json")
    priority_matrix_path = Path("data/processed/priority_matrix.csv")

    if not input_path.exists():
        log_info("No scraper data found. Run scrapers first.")
        # Create empty output for dashboard
        output_path.parent.mkdir(parents=True, exist_ok=True)
        empty_data = {
            "meta": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "total_opportunities": 0,
                "source": "No data"
            },
            "programs": {
                "funding": [],
                "lidar": [],
                "spaceSystems": [],
                "platform": []
            }
        }
        with open(output_path, 'w') as f:
            json.dump(empty_data, f, indent=2)
        return

    # --- LOAD SCRAPER OUTPUT ---
    with open(input_path) as f:
        scraper_data = json.load(f)

    # Handle both formats: {"opportunities": [...]} or [...]
    if isinstance(scraper_data, dict):
        raw_opportunities = scraper_data.get('opportunities', [])
        metadata = scraper_data.get('meta', {})
    else:
        raw_opportunities = scraper_data
        metadata = {}

    log_info(f"Loaded {len(raw_opportunities)} opportunities from scrapers")

    # --- PROCESS OPPORTUNITIES ---
    processed = []
    seen_ids = set()

    # Statistics
    stats = {
        'total_forecast': 0,
        'total_active': 0,
        'by_country': {},
        'by_category': {'DaaS': 0, 'Platform': 0, 'R&D': 0},
        'by_pillar': {}
    }

    # Flow data for Sankey diagram
    flows = {
        'countries': {},
        'agencies': {},
        'segments': {'Space Systems': 0, 'Spatial Intelligence': 0, 'DaaS': 0}
    }

    for opp in raw_opportunities:
        # Extract data
        opp_id = opp.get('id', generate_id(opp.get('link', str(opp))))
        title = opp.get('title', 'Untitled')
        agency = opp.get('agency', 'Unknown')
        country = opp.get('country', 'Global')
        category = opp.get('category', 'R&D')
        pillar = opp.get('pillar', 'Unknown')

        # Get budget value
        funding = opp.get('funding', {})
        value_usd = funding.get('amountUSD', 0)

        # Skip if seen (deduplication)
        dedup_key = f"{title[:30]}-{value_usd}"
        if dedup_key in seen_ids:
            continue
        seen_ids.add(dedup_key)

        # Classify type (Active vs Forecast)
        fiscal_status = classify_opportunity_type(opp)

        # Calculate priority score
        priority_score = calculate_priority_score(opp)

        # Determine segment
        full_text = f"{title} {opp.get('description', '')}"
        segment = determine_segment(full_text)

        # Build processed opportunity
        processed_opp = {
            'id': opp_id,
            'title': title,
            'agency': agency,
            'country': country,
            'pillar': pillar,
            'category': category,
            'segment': segment,
            'value': value_usd,
            'value_fmt': f"${value_usd:,.0f}",
            'fiscal_status': fiscal_status,
            'urgency': opp.get('timeline', {}).get('urgency', 'future'),
            'days_until': opp.get('timeline', {}).get('daysUntil', 999),
            'deadline': opp.get('deadline', ''),
            'url': opp.get('link', ''),
            'priority_score': priority_score,
            'priorityScore': priority_score,  # Add camelCase version for test compatibility
            'source_verified': bool(opp.get('provenance', {}).get('source'))
        }

        processed.append(processed_opp)

        # Update statistics
        if fiscal_status == 'Forecast':
            stats['total_forecast'] += value_usd
        else:
            stats['total_active'] += value_usd

        # Country stats
        if country not in stats['by_country']:
            stats['by_country'][country] = {'forecast': 0, 'active': 0}
        stats['by_country'][country][fiscal_status.lower()] += value_usd

        # Category stats
        if category in stats['by_category']:
            stats['by_category'][category] += value_usd

        # Pillar stats
        if pillar not in stats['by_pillar']:
            stats['by_pillar'][pillar] = 0
        stats['by_pillar'][pillar] += value_usd

        # Flow data
        if country not in flows['countries']:
            flows['countries'][country] = 0
        flows['countries'][country] += value_usd

        agency_key = f"{country}::{agency}"
        if agency_key not in flows['agencies']:
            flows['agencies'][agency_key] = {'val': 0, 'parent': country, 'segment_split': {}}
        flows['agencies'][agency_key]['val'] += value_usd

        if segment not in flows['agencies'][agency_key]['segment_split']:
            flows['agencies'][agency_key]['segment_split'][segment] = 0
        flows['agencies'][agency_key]['segment_split'][segment] += value_usd

        if segment in flows['segments']:
            flows['segments'][segment] += value_usd

    # Sort by priority score
    processed.sort(key=lambda x: x['priority_score'], reverse=True)

    log_success(f"Processed {len(processed)} opportunities")
    log_info(f"  Active Budget: ${stats['total_active']:,.0f}")
    log_info(f"  Forecast: ${stats['total_forecast']:,.0f}")

    # --- GENERATE PROGRAMS OUTPUT ---
    # Map categories to test-expected keys: funding, lidar, spaceSystems, platform
    programs_by_category = {
        'funding': [],
        'lidar': [],
        'spaceSystems': [],
        'platform': []
    }

    for opp in processed:
        category = opp.get('category', 'Platform')
        # Map to test-expected category keys
        if category == 'DaaS':
            category_key = 'platform'
        elif category == 'Platform':
            category_key = 'platform'
        elif category == 'R&D':
            category_key = 'platform'
        elif 'lidar' in category.lower():
            category_key = 'lidar'
        elif 'space' in category.lower() or 'Space Systems' in category:
            category_key = 'spaceSystems'
        elif 'funding' in category.lower():
            category_key = 'funding'
        else:
            category_key = 'platform'  # Default

        if category_key in programs_by_category:
            programs_by_category[category_key].append(opp)

    programs_output = {
        'meta': {
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'total_opportunities': len(processed),
            'total_active_budget': stats['total_active'],
            'total_forecast': stats['total_forecast'],
            'source': 'live_scrapers',
            'scraper_metadata': metadata
        },
        'programs': {
            'funding': programs_by_category['funding'],
            'lidar': programs_by_category['lidar'],
            'spaceSystems': programs_by_category['spaceSystems'],
            'platform': programs_by_category['platform']
        },
        'statistics': stats
    }

    # --- GENERATE SANKEY DATA ---
    sankey_data = build_sankey_diagram(flows, stats)

    # --- SAVE OUTPUTS ---
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Backwards-compatibility: promote common consumer keys at top-level for legacy code/tests
    programs_output_compat = dict(programs_output)  # shallow copy
    platform_list = programs_output.get('programs', {}).get('platform', [])
    programs_output_compat.setdefault('Platform', platform_list)
    programs_output_compat.setdefault('DaaS', platform_list)
    programs_output_compat.setdefault('Space Systems', programs_output.get('programs', {}).get('spaceSystems', []))

    with open(output_path, 'w') as f:
        json.dump(programs_output_compat, f, indent=2, sort_keys=True)
    log_success(f"Generated: {output_path}")

    with open(funding_path, 'w') as f:
        json.dump(sankey_data, f, indent=2, sort_keys=True)
    log_success(f"Generated: {funding_path}")

    # --- GENERATE PRIORITY MATRIX CSV ---
    import csv
    with open(priority_matrix_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'rank', 'priority_score', 'title', 'agency', 'pillar', 'category',
            'value_usd', 'fiscal_status', 'urgency', 'days_until', 'url'
        ])
        writer.writeheader()
        for rank, opp in enumerate(processed, 1):
            writer.writerow({
                'rank': rank,
                'priority_score': opp['priority_score'],
                'title': opp['title'],
                'agency': opp['agency'],
                'pillar': opp['pillar'],
                'category': opp['category'],
                'value_usd': opp['value'],
                'fiscal_status': opp['fiscal_status'],
                'urgency': opp['urgency'],
                'days_until': opp['days_until'],
                'url': opp['url']
            })
    log_success(f"Generated: {priority_matrix_path}")

    log_success("\n🎯 Dashboard data generation complete!")
    log_info(f"   Opportunities: {len(processed)}")
    log_info(f"   Active Budget: ${stats['total_active']:,.0f}")
    log_info(f"   Forecast: ${stats['total_forecast']:,.0f}")


def build_sankey_diagram(flows, stats):
    """Build Sankey diagram data structure"""
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
        colors = {"Space Systems": "#dc2626", "Spatial Intelligence": "#2563eb", "DaaS": "#16a34a"}
        color_list.append(colors[seg])

    # 2. Add Countries (Left Side)
    country_map = {}
    for country, val in sorted(flows['countries'].items(), key=lambda x: x[1], reverse=True)[:20]:
        if val > 0:
            label_list.append(country)
            country_map[country] = len(label_list) - 1
            color_list.append("#475569")

    # 3. Add Agencies (Middle) & Build Links
    for a_key, data in flows['agencies'].items():
        if data['val'] > 0:
            agency_name = a_key.split("::")[1]
            if data['parent'] not in country_map:
                continue

            label_list.append(agency_name[:30])  # Truncate long names
            a_idx = len(label_list) - 1
            color_list.append("#64748b")

            # Link: Country -> Agency
            c_idx = country_map[data['parent']]
            source_list.append(c_idx)
            target_list.append(a_idx)
            value_list.append(data['val'])

            # Link: Agency -> Segments
            for seg, s_val in data['segment_split'].items():
                if s_val > 0 and seg in seg_map:
                    s_idx = seg_map[seg]
                    source_list.append(a_idx)
                    target_list.append(s_idx)
                    value_list.append(s_val)

    return {
        'nodes': {'label': label_list, 'color': color_list},
        'links': {'source': source_list, 'target': target_list, 'value': value_list},
        'stats': stats
    }


if __name__ == "__main__":
    main()
