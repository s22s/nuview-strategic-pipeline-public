# API Secrets Configuration Guide

## Overview

Your NUVIEW Strategic Pipeline uses two API keys for enhanced data collection:

1. **SAM_API_KEY** - For SAM.gov (USA Federal Contracts)
2. **NASA_TECHPORT** - For NASA TechPort (Space Technology Projects)

## Current Status

❌ **Not Configured** - These secrets are not currently set in your GitHub repository.

### Impact
- Scrapers will still run and collect data from other sources (68 scrapers total)
- SAM.gov scraper will skip opportunities requiring API key
- NASA TechPort data won't be enriched with detailed project information
- You're still getting 128 opportunities from other free/public sources

## How to Configure (GitHub Actions)

### Step 1: Obtain API Keys

#### SAM.gov API Key
1. Visit: https://sam.gov/data-services/
2. Register for a free API key
3. Navigate to "Account Details" → "API Key Management"
4. Generate a new API key (free tier available)

#### NASA TechPort (Optional)
1. Visit: https://api.nasa.gov/
2. Sign up for a free NASA API key
3. The key works across all NASA APIs including TechPort

### Step 2: Add to GitHub Secrets

1. Go to your repository: `https://github.com/s22s/nuview-strategic-pipeline`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:

**Secret 1: SAM_API_KEY**
- Name: `SAM_API_KEY`
- Value: `[your SAM.gov API key]`

**Secret 2: NASA_TECHPORT**  
- Name: `NASA_TECHPORT`
- Value: `[your NASA API key]`

### Step 3: Verify

After adding secrets, your GitHub Actions workflows will automatically use them:
- `.github/workflows/daily_ops.yml` - Daily scraping
- `.github/workflows/auto-deploy.yml` - Auto deployment

## Where Secrets Are Used

### SAM.gov API (`SAM_API_KEY`)
- **File**: `scripts/scrapers/us_federal.py`
- **Usage**: Fetches active federal contracts and awards
- **Value**: Real-time contract data with actual budgets
- **Without it**: Scraper skips this source

### NASA TechPort (`NASA_TECHPORT`)
- **File**: Would be used in enhanced NASA scraper
- **Usage**: Detailed space technology project information
- **Value**: Budget details, timelines, technology readiness levels
- **Without it**: Falls back to basic NASA data

## Verification Script

Run this to check if secrets are configured:

```bash
# In GitHub Actions, this will show if secrets are set
cd scripts
python -c "import os; print('SAM_API_KEY:', 'SET' if os.environ.get('SAM_API_KEY') else 'NOT SET'); print('NASA_TECHPORT:', 'SET' if os.environ.get('NASA_TECHPORT') else 'NOT SET')"
```

## Local Development

For local testing:

```bash
# Set environment variables (temporary)
export SAM_API_KEY="your-sam-key-here"
export NASA_TECHPORT="your-nasa-key-here"

# Or create a .env file (don't commit!)
echo "SAM_API_KEY=your-sam-key-here" > .env
echo "NASA_TECHPORT=your-nasa-key-here" >> .env

# Add .env to .gitignore
echo ".env" >> .gitignore
```

## Important Notes

### Security
- ✅ **DO**: Store API keys in GitHub Secrets
- ❌ **DON'T**: Commit API keys to code
- ❌ **DON'T**: Put keys in configuration files
- ✅ **DO**: Use environment variables

### Cost
- **SAM.gov**: FREE (no billing required)
- **NASA API**: FREE (generous rate limits)
- **Both**: No credit card needed for basic tier

### Rate Limits
- **SAM.gov**: 1,000 requests/day (more than enough)
- **NASA**: 1,000 requests/hour (very generous)
- Pipeline runs once daily, well within limits

## Troubleshooting

### "API key not found" errors
- Check that secrets are named exactly: `SAM_API_KEY` and `NASA_TECHPORT`
- Verify secrets are set in repository settings
- Re-run the workflow after adding secrets

### "Invalid API key" errors
- Verify your API key is active on the provider's website
- Check for extra spaces or characters when copying
- Try regenerating the API key

### Still not working?
- Check workflow logs in GitHub Actions
- Look for "Missing API key" warnings
- Verify the secret names match exactly

## Future Enhancements

With API keys configured, we can add:
- Real-time SAM.gov contract awards
- Detailed NASA project budgets
- Enhanced opportunity details
- More accurate deadline tracking
- Better budget validation

## Questions?

If you need help configuring these secrets, let me know and I can:
1. Guide you through the process step-by-step
2. Help troubleshoot any issues
3. Add additional API integrations
4. Optimize the scraper usage of these APIs
