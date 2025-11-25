#!/usr/bin/env python3
"""
NUVIEW War Room – Competitor Tracker (2025)
Uses USASpending.gov API – no key needed
Tracks who wins cloud/data-accessibility contracts
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

import requests

COMPETITORS = [
    "WOOLPERT", "DEWBERRY", "NV5", "FUGRO", "SANBORN",
    "PLANET LABS", "MAXAR", "BLACKSKY", "CAPELLA SPACE"
]

NAICS = ["541370", "541360"]  # Surveying & Geophysical
HISTORY_FILE = Path("data/history/competitor_trends.json")
OUTPUT_FILE = Path("data/processed/competitors.json")

def fetch_competitor_data():
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    results = {}
    for name in COMPETITORS:
        payload = {
            "filters": {
                "time_period": [{"start_date": start_date, "end_date": end_date}],
                "recipient_search_text": [name],
                "naics_codes": {"include": NAICS}
            },
            "limit": 100,
            "fields": ["Award Amount", "Awarding Agency", "Description", "Award ID"]
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            data = resp.json()
            total = sum(a.get("Award Amount", 0) or 0 for a in data.get("results", []))
            threats = [
                a for a in data.get("results", [])
                if any(kw in (a.get("Description") or "").lower() for kw in
                       ["cloud", "hosting", "portal", "daas", "data access", "cog", "copc", "stac"])
            ]
            results[name] = {
                "total_12m": round(total / 1_000_000, 2),
                "threat_deals": len(threats),
                "last_updated": datetime.now().isoformat()[:10]
            }
        except Exception as e:
            if isinstance(e, (KeyboardInterrupt, SystemExit)):
                raise
            logging.exception("Failed processing competitor %s: %s", name, e)
            results[name] = {"total_12m": 0, "threat_deals": 0, "error": True}

    # Save current snapshot
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # Update history
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            history = json.load(f)
    else:
        history = {}

    today = datetime.now().strftime("%Y-%m-%d")
    for comp, data in results.items():
        if comp not in history:
            history[comp] = []
        history[comp].append({"date": today, "total_m": data["total_12m"]})
        if len(history[comp]) > 52:  # 1 year
            history[comp] = history[comp][-52:]

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

    print(f"War Room updated: {len(results)} competitors tracked")

if __name__ == "__main__":
    fetch_competitor_data()
