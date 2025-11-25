# Global Sources Integration Guide

This document explains how the new `config/global_sources.py` integrates with the NUVIEW Strategic Pipeline backend and workflows.

## Overview

The global sources configuration provides a curated, sourceable list of **19 countries** with **26 agencies** and **39 verified data sources** for:
- **Current Opportunities** (procurement/tenders/grants)
- **Budgets** (historical budget documents)  
- **Forecasts** (future planning documents)

All sources are **public/free** and directly relevant to LiDAR, topographic, digital twin, and resilience opportunities.

## Architecture

### Data Flow

```
global_sources.py (config)
    ↓
scraper implementations
    ↓
data/raw/all_opportunities.json
    ↓
scripts/generate_programs.py
    ↓
data/processed/opportunities.json (Current Opps)
data/forecast.json (Forecast)
data/static/budget_hierarchy.json (Budgets)
    ↓
dashboard/index.html
```

### Three Data Categories

1. **Opportunities** (Current Opps)
   - SAM.gov, Grants.gov, CanadaBuys, AusTender, TED, etc.
   - Scrape frequency: Daily or Weekly
   - Output: `data/processed/opportunities.json`

2. **Budgets** (Historical & Current)
   - Agency budget justifications, annual reports
   - Scrape frequency: Yearly
   - Output: `data/static/budget_hierarchy.json`

3. **Forecasts** (Future Planning)
   - Programme announcements, multi-year plans
   - Scrape frequency: Quarterly
   - Output: `data/forecast.json`

## Integration Steps

### 1. Update Scraper Base Class

The existing `scripts/scrapers/base_scraper.py` already supports:
- ✅ Multi-country scrapers
- ✅ Source provenance tracking
- ✅ Free/public API validation

No changes needed to base class.

### 2. Create Country-Specific Scrapers

For each country/source in `global_sources.py`, create or update scrapers:

#### Example: US SAM.gov Scraper

```python
# scripts/scrapers/us_procurement.py
from base_scraper import BaseScraper
from config.global_sources import get_sources_by_country

class SAMgovScraper(BaseScraper):
    def __init__(self):
        super().__init__("SAM.gov Federal", "Federal", "United States")
        self.sources = get_sources_by_country("United States")
        
    def scrape(self):
        # Use source configuration from global_sources
        sam_source = next(
            s for agency in self.sources.get("agencies", [])
            for s in agency.get("sources", [])
            if "SAM.gov" in s.get("name")
        )
        
        keywords = sam_source.get("keywords", [])
        naics_codes = sam_source.get("naics_codes", [])
        
        # Implement actual SAM.gov API scraping here
        opportunities = self._fetch_sam_opportunities(keywords, naics_codes)
        self.opportunities.extend(opportunities)
        return opportunities
```

#### Example: UK Procurement Scraper

```python
# scripts/scrapers/uk_procurement.py
from base_scraper import BaseScraper
from config.global_sources import get_sources_by_country

class UKTendersScraper(BaseScraper):
    def __init__(self):
        super().__init__("UK Find a Tender", "International", "United Kingdom")
        self.sources = get_sources_by_country("United Kingdom")
        
    def scrape(self):
        # Get source config
        tender_source = next(
            s for agency in self.sources.get("agencies", [])
            for s in agency.get("sources", [])
            if "Find a Tender" in s.get("name")
        )
        
        keywords = tender_source.get("keywords", [])
        
        # Implement actual Find a Tender API scraping
        opportunities = self._fetch_uk_tenders(keywords)
        self.opportunities.extend(opportunities)
        return opportunities
```

### 3. Update Scrape Orchestration

Modify `scripts/scrapers/scrape_all.py` to use the global sources schedule:

```python
# Add to scrape_all.py
from config.global_sources import get_scrape_schedule, get_all_procurement_sources

def run_scheduled_scrapes(frequency="daily"):
    """
    Run scrapers based on schedule frequency.
    
    Args:
        frequency: One of 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    """
    schedule = get_scrape_schedule()
    sources_to_scrape = schedule.get(frequency, [])
    
    print(f"Running {len(sources_to_scrape)} {frequency} scrapers...")
    
    for source_config in sources_to_scrape:
        country = source_config["country"]
        source_name = source_config["source"]
        data_type = source_config["data_type"]
        
        # Map to appropriate scraper class
        scraper = get_scraper_for_source(country, source_name)
        if scraper:
            opportunities = scraper.scrape()
            print(f"  ✓ {country} - {source_name}: {len(opportunities)} items")
```

### 4. Add to GitHub Actions Workflows

Update `.github/workflows/auto-deploy.yml` or create dedicated workflow for global scraping:

```yaml
name: Global Data Collection

on:
  schedule:
    # Daily scrapes at 6 AM UTC
    - cron: '0 6 * * *'
  workflow_dispatch:
    inputs:
      frequency:
        description: 'Scrape frequency'
        required: true
        default: 'daily'
        type: choice
        options:
          - daily
          - weekly
          - monthly
          - quarterly
          - yearly

jobs:
  scrape-global:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run scheduled scrapers
        run: |
          FREQUENCY=${{ github.event.inputs.frequency || 'daily' }}
          python scripts/run_scheduled_scrapes.py --frequency $FREQUENCY
      
      - name: Commit and push data updates
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add data/
          git commit -m "🌍 Global data update: ${FREQUENCY}" || echo "No changes"
          git push
```

### 5. Data Output Structure

Each data type has its own output schema:

#### Opportunities (Current Opps)
```json
{
  "meta": {
    "updated": "2025-11-24T18:00:00Z",
    "totalCount": 150,
    "scrapers_run": 29
  },
  "opportunities": [
    {
      "id": "sam-gov-123",
      "title": "USGS 3DEP LiDAR Acquisition",
      "agency": "USGS",
      "pillar": "Federal",
      "country": "United States",
      "category": "DaaS",
      "forecast_value": "$2,500,000",
      "link": "https://sam.gov/opp/...",
      "budgetSourceLink": "https://www.usgs.gov/publications/...",
      "agencyLink": "https://www.usgs.gov/3d-elevation-program",
      "deadline": "2025-12-31",
      "provenance": {
        "scraper": "SAM.gov Federal",
        "source_type": "Federal",
        "country": "United States",
        "cost_free": true,
        "scraped_at": "2025-11-24T18:00:00Z"
      }
    }
  ]
}
```

#### Budgets
```json
{
  "meta": {
    "updated": "2025-11-24T18:00:00Z",
    "totalCountries": 19
  },
  "budgets": [
    {
      "country": "United States",
      "agency": "USGS",
      "fiscal_year": 2026,
      "program": "3D Elevation Program",
      "amount_usd": 45000000,
      "source_link": "https://www.usgs.gov/...",
      "scraped_at": "2025-11-24T18:00:00Z"
    }
  ]
}
```

#### Forecasts
```json
{
  "meta": {
    "updated": "2025-11-24T18:00:00Z",
    "totalForecasts": 25
  },
  "forecasts": [
    {
      "country": "France",
      "agency": "IGN",
      "program": "LiDAR HD Programme",
      "timeframe": "2025-2030",
      "estimated_value_usd": 150000000,
      "description": "National LiDAR coverage at 1pt/m² density",
      "source_link": "https://www.actuia.com/...",
      "keywords": ["lidar hd", "programme", "cartographie"],
      "scraped_at": "2025-11-24T18:00:00Z"
    }
  ]
}
```

## Dashboard Integration

The dashboard already displays opportunities by pillar. To show country-specific data:

### Add Country Filter
```javascript
// dashboard/assets/js/app.js
function filterByCountry(country) {
  return opportunities.filter(opp => opp.country === country);
}

// Add country dropdown to dashboard
const countries = [...new Set(opportunities.map(o => o.country))].sort();
```

### Add Budget View
```javascript
// Display budget data in separate dashboard section
fetch('data/static/budget_hierarchy.json')
  .then(r => r.json())
  .then(budgets => {
    renderBudgetChart(budgets);
  });
```

### Add Forecast Timeline
```javascript
// Display forecast data in timeline view
fetch('data/forecast.json')
  .then(r => r.json())
  .then(forecasts => {
    renderForecastTimeline(forecasts);
  });
```

## Maintenance

### Adding New Countries

1. Add country to `config/global_sources.py`:
```python
"New Country": {
    "country_code": "XX",
    "agencies": [...]
}
```

2. Create scraper: `scripts/scrapers/new_country_scraper.py`

3. Add to `scrape_all.py` imports and scraper list

4. Test: `python scripts/scrapers/scrape_all.py`

### Verifying Links

All links in `global_sources.py` are verified and point to:
- Official government procurement portals
- Agency budget/annual report pages
- Programme-specific pages with downloadable data

Run verification script:
```bash
python scripts/verify_global_links.py
```

## Benefits

✅ **Sourceable**: Every opportunity links to original source  
✅ **Actionable**: Direct links to procurement portals and budget docs  
✅ **Verified**: All 39 sources manually verified as public/free  
✅ **Scalable**: Easy to add new countries/agencies  
✅ **Automated**: Scheduled scraping via GitHub Actions  
✅ **Comprehensive**: 19 countries, 26 agencies, 3 data types  

## Next Steps

1. ✅ Create `config/global_sources.py` with all 19 countries
2. ⬜ Implement scrapers for top 5 countries (US, UK, CA, FR, DE)
3. ⬜ Create `scripts/run_scheduled_scrapes.py`
4. ⬜ Add budget scraping to generate `data/static/budget_hierarchy.json`
5. ⬜ Add forecast scraping to update `data/forecast.json`
6. ⬜ Update dashboard to show country filter and budget/forecast views
7. ⬜ Create GitHub Actions workflow for scheduled global scraping
8. ⬜ Add link verification script

## Questions?

See existing scrapers in `scripts/scrapers/` for implementation examples.
All existing scrapers follow the pattern and can be adapted for new countries.
