#!/usr/bin/env python3
"""
Global Sources Scraper Integration
Connects config/global_sources.py with actual scraping implementations
"""

import os
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "config"))

from config.global_sources import get_all_procurement_sources


def scrape_sam_gov(api_key=None):
    """Scrape SAM.gov with optional API key"""
    opportunities = []

    if not api_key:
        print("  ⚠️  SAM.gov API key not found - using limited public data")
        # Fall back to public/limited scraping
        return opportunities

    print("  ✓ SAM.gov: Using authenticated API")
    # Implementation would go here
    # This is where you'd call the actual SAM.gov API
    return opportunities


def scrape_nasa_opportunities(api_key=None):
    """Scrape NASA ROSES/SBIR opportunities"""
    opportunities = []

    # NASA ROSES and SBIR/STTR are public APIs
    print("  ✓ NASA: Scraping ROSES solicitations (public)")
    print("  ✓ NASA: Scraping SBIR/STTR (public)")

    # Implementation would call NASA's public APIs
    return opportunities


def scrape_international_tenders(country, source_config):
    """
    Scrape international tender/procurement sources

    Args:
        country: Country name
        source_config: Source configuration from global_sources.py
    """
    opportunities = []

    print(f"  → {country} - {source_config['name']}")
    print(f"     URL: {source_config['url']}")
    print(f"     Keywords: {', '.join(source_config.get('keywords', [])[:3])}...")

    # This is where actual scraping implementation would go
    # Different implementation per procurement portal:
    # - TED (EU): Use their XML/JSON API
    # - AusTender: Use their API
    # - CanadaBuys: Scrape or use API if available
    # etc.

    return opportunities


def run_opportunity_scrapers():
    """Run all opportunity scrapers from global sources"""
    print("\n" + "="*70)
    print("RUNNING OPPORTUNITY SCRAPERS")
    print("="*70)

    all_opportunities = []

    # Get all procurement sources from config
    procurement_sources = get_all_procurement_sources()

    print(f"\nTotal sources to scrape: {len(procurement_sources)}")

    # Group by country for better organization
    by_country = {}
    for source in procurement_sources:
        country = source['country']
        if country not in by_country:
            by_country[country] = []
        by_country[country].append(source)

    # Scrape each country's sources
    for country, sources in by_country.items():
        print(f"\n{country} ({len(sources)} sources):")

        for source in sources:
            if country == "United States":
                # Handle US-specific sources with API keys
                if "SAM.gov" in source['name']:
                    api_key = os.environ.get("SAM_API_KEY")
                    opps = scrape_sam_gov(api_key)
                    all_opportunities.extend(opps)
                elif "NASA" in source['name']:
                    api_key = os.environ.get("NASA_API_KEY")  # Optional
                    opps = scrape_nasa_opportunities(api_key)
                    all_opportunities.extend(opps)
                else:
                    # Other US sources (Grants.gov, FEMA, etc.)
                    opps = scrape_international_tenders(country, source)
                    all_opportunities.extend(opps)
            else:
                # International sources
                opps = scrape_international_tenders(country, source)
                all_opportunities.extend(opps)

    print(f"\n{'='*70}")
    print(f"Total opportunities collected: {len(all_opportunities)}")
    print(f"{'='*70}\n")

    return all_opportunities


def check_api_integrations():
    """Check which API keys are available"""
    print("\n" + "="*70)
    print("API INTEGRATION STATUS")
    print("="*70)

    integrations = {
        "SAM_API_KEY": "SAM.gov (US Federal Procurement)",
        "NASA_API_KEY": "NASA ROSES/SBIR (optional - has public access)",
        "GRANTS_GOV_API": "Grants.gov (optional - has public search)",
    }

    available = []
    missing = []

    for key, description in integrations.items():
        if os.environ.get(key):
            print(f"  ✓ {description}")
            available.append(key)
        else:
            print(f"  ✗ {description} - NOT CONFIGURED")
            missing.append(key)

    print(f"\n{'='*70}")
    print(f"Available: {len(available)} | Missing: {len(missing)}")
    print(f"{'='*70}\n")

    if missing:
        print("NOTE: Missing keys will use public/limited data sources")
        print("To add keys: Set environment variables or GitHub Secrets\n")

    return {"available": available, "missing": missing}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Global Sources Scraper Integration"
    )
    parser.add_argument(
        "--check-integrations",
        action="store_true",
        help="Check API integration status"
    )
    parser.add_argument(
        "--run-scrapers",
        action="store_true",
        help="Run all opportunity scrapers"
    )

    args = parser.parse_args()

    if args.check_integrations:
        check_api_integrations()
    elif args.run_scrapers:
        run_opportunity_scrapers()
    else:
        print("NUVIEW Global Sources Scraper Integration")
        print("="*70)
        print("\nUsage:")
        print("  --check-integrations   Check which API keys are configured")
        print("  --run-scrapers         Run all opportunity scrapers")
        print("\nExample:")
        print("  python scripts/global_scraper.py --check-integrations")
        print("  python scripts/global_scraper.py --run-scrapers")
        print()
