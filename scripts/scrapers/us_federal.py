import os
from datetime import datetime, timedelta

import requests

from scripts.schemas.opportunity import Opportunity


def fetch_sam_opportunities(api_key):
    """Hits the official SAM.gov API for live solicitations."""
    print("   ► ACCESSING: SAM.gov Official API (Authorized)...")

    url = "https://api.sam.gov/opportunities/v2/search"
    today = datetime.now()
    date_str = (today - timedelta(days=30)).strftime('%m/%d/%Y')

    params = {
        "api_key": api_key,
        "postedFrom": date_str,
        "postedTo": today.strftime('%m/%d/%Y'),
        "limit": 50,
        "ptype": "p,o,k,r", # Presolicitation, Combined, Special Notice, Sources Sought
        "q": "lidar space satellite mapping geospatial" # Your keywords
    }

    try:
        # Note: requests.get is standard for SAM, but verify docs if they require params in URL vs params dict
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        opps = []
        for item in data.get('opportunitiesData', []):
            # SAM API structure is deep, simplified mapping here:
            opps.append(Opportunity(
                title=item.get('title', 'Untitled Opportunity'),
                agency=item.get('department', {}).get('name', 'US Federal'),
                description=item.get('description', '')[:5000],
                value=0.0, # SAM often hides value in Forecasts, defaults to 0
                close_date=item.get('responseDeadLine'),
                url=item.get('uiLink', 'https://sam.gov'),
                source="SAM.gov (Live)",
                country="USA",
                segment="DaaS" # Default, Brain will re-sort
            ).dict())
        print(f"     ✅ SAM.gov: Authorized access successful. {len(opps)} opportunities found.")
        return opps
    except Exception as e:
        print(f"     ⚠️ SAM API Error: {e}")
        return []

def fetch_usa_spending():
    """Fallback: Hits USASpending for historical awards if SAM key is missing."""
    print("   ► ACCESSING: USASpending (Public/No-Key)...")
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    today = datetime.now()
    start_date = (today - timedelta(days=60)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    payload = {
        "filters": {
            "time_period": [{"start_date": start_date, "end_date": end_date}],
            "award_type_codes": ["A", "B", "C", "D"],
            "description": "lidar"
        },
        "fields": ["Award ID", "Description", "Award Amount", "Awarding Agency"],
        "limit": 30
    }
    try:
        resp = requests.post(url, json=payload, timeout=20)
        return [Opportunity(
            title=f"AWARD: {r.get('Description')}",
            agency=r.get('Awarding Agency', 'US Govt'),
            description=r.get('Description', ''),
            value=float(r.get('Award Amount', 0) or 0),
            url=f"https://www.usaspending.gov/award/{r.get('Award ID')}",
            source="USASpending",
            country="USA"
        ).dict() for r in resp.json().get('results', [])]
    except Exception as e:
        print(f"     ⚠️ USASpending Error: {e}")
        return []

def fetch():
    # 1. Check for Secret Key in Environment
    api_key = os.environ.get("SAM_API_KEY")

    if api_key:
        # High Value: Get Future Opportunities
        return fetch_sam_opportunities(api_key)
    else:
        # Fallback: Get Past Awards (What you have now)
        return fetch_usa_spending()
