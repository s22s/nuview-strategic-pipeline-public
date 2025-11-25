# How It Works: NUVIEW Strategic Pipeline

## Overview

The NUVIEW Strategic Pipeline is a fully automated business intelligence platform that continuously monitors, analyzes, and prioritizes global opportunities in topographic mapping, geospatial analytics, and data services. This document explains how the system operates, from data collection to visualization.

---

## System Architecture

### 1. Data Scraping Layer

The pipeline uses **34 specialized scrapers** that continuously monitor various data sources:

- **Federal Sources**: SAM.gov contracts, USGS projects, NASA opportunities
- **International Sources**: World Bank Open Data, government portals from 34+ countries
- **Research & Commercial**: Academic partnerships, industry RFPs, private sector opportunities

**Key Features:**
- All scrapers use **100% free/public APIs** with no billing
- Built-in cost guardrails prevent any paid API usage
- Automatic retry logic with exponential backoff
- Rate limiting to respect API quotas
- Data provenance tracking (every record shows its source)

### 2. Data Validation & Quality Control

Every scraped record goes through multi-stage validation:

1. **Schema Validation**: Ensures all required fields are present
2. **Data Type Checking**: Validates field types (dates, URLs, amounts)
3. **Duplicate Detection**: Removes redundant entries
4. **Quality Score**: Assigns confidence scores (0-100) based on data completeness
5. **100% QC Pass Requirement**: Only fully validated records make it to the dashboard

### 3. Intelligence Scoring Engine

Each opportunity is scored across multiple dimensions:

**Scoring Criteria:**
- **Strategic Fit** (0-40 points): Alignment with NUVIEW's core business pillars
  - Space Systems (satellite imaging, remote sensing)
  - Spatial Intelligence (AI/ML for geospatial data)
  - DaaS - Data as a Service (topographic mapping)
  
- **Market Size** (0-30 points): Contract value and market opportunity
  - Small: <$500K (10 points)
  - Medium: $500K-$5M (20 points)
  - Large: >$5M (30 points)
  
- **Urgency** (0-20 points): Time sensitivity and competition level
  - Deadline proximity
  - Number of bidders
  - Pre-RFP indicators
  
- **Data Quality** (0-10 points): Completeness and reliability of information

**Final Score**: 0-100 points → categorized as High (70+), Medium (40-69), or Low (<40) priority

### 4. Output Generation

The pipeline generates multiple output formats:

#### JSON Datasets
- `opportunities_space.json`: Space systems opportunities
- `opportunities_spatial.json`: Spatial intelligence projects
- `opportunities_daas.json`: Mapping and DaaS contracts
- `opportunities_funding.json`: Global funding opportunities
- `pipeline_matrix.json`: Complete strategic matrix

#### Dashboard Assets
- Real-time KPI metrics (updated every 30-60 seconds)
- Interactive data tables with search/filter
- Geographic heatmaps showing opportunity distribution
- Time-series charts tracking trends
- Live "Go Now" feed highlighting critical actions

#### API Endpoints
All data is accessible via GitHub Pages at:
```
https://[username].github.io/nuview-strategic-pipeline/data/
```

---

## Running the Pipeline Locally

### Prerequisites

```bash
# Python 3.9 or higher
python --version

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/{username}/{repository}.git
   cd {repository}
   ```

2. **Configure API keys** (optional - all free):
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env with your API keys (all free APIs)
   ```

3. **Run the setup script**:
   ```bash
   chmod +x setup_and_run.sh
   ./setup_and_run.sh
   ```

### Manual Execution

#### Run All Scrapers
```bash
# Execute the complete pipeline
python scripts/run_scrapers.py --all

# Run specific scraper
python scripts/run_scrapers.py --scraper sam_gov

# Dry-run mode (no writes)
python scripts/run_scrapers.py --all --dry-run
```

#### Run Validation
```bash
# Validate all scraped data
python scripts/validate_data.py

# Generate quality control report
python scripts/qc_audit.py
```

#### Generate Outputs
```bash
# Build dashboard JSON files
python scripts/generate_dashboard_data.py

# Build pipeline matrix
python scripts/build_matrix.py
```

#### Local Dashboard Preview
```bash
# Start a local HTTP server
python -m http.server 8000

# Open browser to http://localhost:8000/dashboard/
```

---

## Continuous Integration

### Automated Daily Operations

The pipeline runs automatically via **GitHub Actions**:

- **Daily Sweep**: Runs at 06:00 UTC daily (`daily_ops.yml`)
  1. Execute all scrapers
  2. Validate and score data
  3. Generate dashboard outputs
  4. Deploy to GitHub Pages
  5. Send alerts for critical opportunities

- **On-Demand Trigger**: Click "Live Scrape" button in dashboard
  - Triggers workflow via GitHub Actions API
  - Completes in 3-5 minutes
  - Dashboard auto-refreshes with new data

### Deployment Pipeline

```
Scrapers → Validation → Scoring → Output Generation → GitHub Pages Deployment
   ↓           ↓           ↓              ↓                    ↓
 Raw Data   QC Check   Priorities    JSON/HTML         Live Dashboard
```

**Deployment Frequency**: 
- Scheduled: Once daily (06:00 UTC)
- Manual: On-demand via dashboard button
- PR Merges: Automatic preview deployments

---

## Data Provenance & Transparency

Every opportunity record includes:

```json
{
  "id": "unique-identifier",
  "source": "SAM.gov",
  "scraper": "sam_gov_v2",
  "scraped_at": "2025-11-24T19:30:00Z",
  "api_endpoint": "https://api.sam.gov/opportunities/v2/search",
  "data_quality_score": 95,
  "strategic_score": 78,
  "category": "Space Systems",
  "cost_flag": "FREE_API"
}
```

This ensures:
- **Full audit trail** for compliance
- **Reproducible results** for verification
- **API transparency** showing exact data source
- **Quality metrics** for decision confidence

---

## Cost Guardrails

**NUVIEW Strategic Pipeline operates with ZERO costs:**

✅ All scrapers use only free/public government APIs  
✅ No billing accounts or payment methods connected  
✅ Cost assertions built into every scraper  
✅ GitHub Actions runs on free tier (2,000 minutes/month)  
✅ GitHub Pages hosting is free for public repositories  

**Missing API Indicators:**
- Dashboard displays alerts when optional APIs are not configured
- System continues to operate with available free APIs
- No functionality requires paid services

---

## Support & Troubleshooting

### Common Issues

**1. Scraper fails with rate limit error**
- Solution: Wait 60 seconds and retry (automatic retry logic included)

**2. Dashboard shows missing data**
- Check `data/` directory for JSON files
- Run `python scripts/validate_data.py` to check data integrity
- Review GitHub Actions logs for scraper errors

**3. API key errors**
- All APIs are free and optional
- Missing keys are non-blocking (system uses available sources)
- See `API_SECRETS_GUIDE.md` for setup instructions

### Getting Help

- **Documentation**: See `docs/` directory for detailed guides
- **Issue Tracker**: GitHub Issues for bug reports
- **Build Logs**: GitHub Actions tab for execution details

---

## Next Steps

1. **Explore the Dashboard**: https://{username}.github.io/{repository}/
2. **Review Source Code**: `scripts/` directory for scraper implementations
3. **Customize Scrapers**: Add new sources or modify scoring logic
4. **Integrate APIs**: Configure optional API keys for enhanced data
5. **Automate Reports**: Set up email notifications for high-priority opportunities

---

*Last Updated: November 2025*  
*System Version: 3.0*  
*Maintained by: NUVIEW Strategic Intelligence Team*
