import logging

from scripts.schemas.opportunity import Opportunity
from scripts.utils.http import safe_get


def fetch():
    print("   ► Running Sniper: World Bank Global...")
    url = "https://search.worldbank.org/api/v2/projects"
    params = {
        "format": "json",
        "fl": "project_name,totalamt,countryname,url,closingdate,project_abstract",
        "qterm": "disaster resilience digital",
        "rows": 50
    }
    resp = safe_get(url, params)
    if not resp:
        return []
    data = resp.json()
    opps = []
    for k, v in data.get('projects', {}).items():
        val = v.get('totalamt', 0)
        try:
            val = float(str(val).replace(',', ''))
        except Exception as e:
            if isinstance(e, (KeyboardInterrupt, SystemExit)):
                raise
            logging.exception("Failed to parse World Bank amount for project %s: %s", k, e)
            val = 0.0
        opps.append(Opportunity(
            title=v.get('project_name'),
            agency=f"World Bank - {v.get('countryname')}",
            description=str(v.get('project_abstract', {}).get('cdata', '')),
            value=val,
            close_date=v.get('closingdate'),
            url=v.get('url', '#'),
            source="World Bank",
            country=v.get('countryname', 'Global')
        ).dict())
    return opps
