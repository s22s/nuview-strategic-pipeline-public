"""
Global procurement and opportunity sources configuration.
Defines procurement portals, API endpoints, and scraping schedules for all
countries relevant to NUVIEW's geospatial/LiDAR pipeline opportunities.
"""

from config.keywords import PILLARS, IMPLIED_DEMAND

# ---------------------------------------------------------------------------
# Core keyword lists (shared across sources)
# ---------------------------------------------------------------------------
_GEO_KEYWORDS = [
    "lidar", "elevation", "dem", "topographic", "geospatial", "mapping",
    "remote sensing", "satellite", "hyperspectral", "sar", "photogrammetry",
    "point cloud", "orthoimagery", "digital twin", "geoint",
]

_SPACE_KEYWORDS = [
    "satellite", "payload", "orbit", "launch", "space systems", "sar",
    "hyperspectral", "nasa", "esa", "space force", "sda",
]

_CLIMATE_KEYWORDS = [
    "flood resilience", "disaster risk", "climate adaptation",
    "infrastructure modernization", "coastal erosion", "carbon stock",
    "vegetation encroachment",
]

_ALL_KEYWORDS = list(dict.fromkeys(_GEO_KEYWORDS + _SPACE_KEYWORDS + _CLIMATE_KEYWORDS))

# ---------------------------------------------------------------------------
# GLOBAL_SOURCES
# Keyed by country; each entry has an "agencies" list.
# Each agency has "name", "url", and "sources" (list of source dicts).
# Each source dict: {"name", "url", "data_type", "schedule", "keywords"}
# ---------------------------------------------------------------------------
GLOBAL_SOURCES = {
    "United States": {
        "agencies": [
            {
                "name": "SAM.gov (System for Award Management)",
                "url": "https://sam.gov/",
                "sources": [
                    {
                        "name": "SAM.gov Opportunities",
                        "url": "https://sam.gov/api/prod/sgs/v1/search/",
                        "data_type": "procurement",
                        "schedule": "daily",
                        "keywords": _ALL_KEYWORDS,
                    }
                ],
            },
            {
                "name": "NASA (National Aeronautics and Space Administration)",
                "url": "https://www.nasa.gov/",
                "sources": [
                    {
                        "name": "NASA ROSES Solicitations",
                        "url": "https://solicitation.nasaprs.com/ROSES2024",
                        "data_type": "grant",
                        "schedule": "weekly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    },
                    {
                        "name": "NASA SBIR/STTR",
                        "url": "https://sbir.nasa.gov/",
                        "data_type": "grant",
                        "schedule": "weekly",
                        "keywords": _SPACE_KEYWORDS,
                    },
                ],
            },
            {
                "name": "Grants.gov",
                "url": "https://www.grants.gov/",
                "sources": [
                    {
                        "name": "Grants.gov Federal Grants",
                        "url": "https://www.grants.gov/web/grants/search-grants.html",
                        "data_type": "grant",
                        "schedule": "daily",
                        "keywords": _GEO_KEYWORDS + _CLIMATE_KEYWORDS,
                    }
                ],
            },
            {
                "name": "USGS (United States Geological Survey)",
                "url": "https://www.usgs.gov/",
                "sources": [
                    {
                        "name": "USGS 3DEP Program",
                        "url": "https://www.usgs.gov/3d-elevation-program",
                        "data_type": "procurement",
                        "schedule": "monthly",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            },
        ]
    },
    "European Union": {
        "agencies": [
            {
                "name": "TED (Tenders Electronic Daily)",
                "url": "https://ted.europa.eu/",
                "sources": [
                    {
                        "name": "TED EU Public Procurement",
                        "url": "https://ted.europa.eu/TED/browse/browseByMap.do",
                        "data_type": "procurement",
                        "schedule": "daily",
                        "keywords": _ALL_KEYWORDS,
                    }
                ],
            },
            {
                "name": "ESA (European Space Agency)",
                "url": "https://www.esa.int/",
                "sources": [
                    {
                        "name": "ESA EMITS Tenders",
                        "url": "https://emits.esa.int/emits/owa/emits.main",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    },
                    {
                        "name": "ESA Copernicus Programme",
                        "url": "https://www.copernicus.eu/en/opportunities",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _GEO_KEYWORDS + _CLIMATE_KEYWORDS,
                    },
                ],
            },
        ]
    },
    "United Kingdom": {
        "agencies": [
            {
                "name": "UKSA (UK Space Agency)",
                "url": "https://www.gov.uk/government/organisations/uk-space-agency",
                "sources": [
                    {
                        "name": "UKSA Funding Opportunities",
                        "url": "https://www.gov.uk/government/collections/uk-space-agency-funding",
                        "data_type": "grant",
                        "schedule": "weekly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    }
                ],
            },
            {
                "name": "Find a Tender Service",
                "url": "https://www.find-tender.service.gov.uk/",
                "sources": [
                    {
                        "name": "UK Government Tenders",
                        "url": "https://www.find-tender.service.gov.uk/Search/Results",
                        "data_type": "procurement",
                        "schedule": "daily",
                        "keywords": _ALL_KEYWORDS,
                    }
                ],
            },
        ]
    },
    "Australia": {
        "agencies": [
            {
                "name": "Geoscience Australia",
                "url": "https://www.ga.gov.au/",
                "sources": [
                    {
                        "name": "Geoscience Australia Tenders",
                        "url": "https://www.ga.gov.au/about/about-us/contracts-and-funding/tenders",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            },
            {
                "name": "AusTender",
                "url": "https://www.tenders.gov.au/",
                "sources": [
                    {
                        "name": "AusTender Government Procurement",
                        "url": "https://www.tenders.gov.au/Atm/ListAtmlist",
                        "data_type": "procurement",
                        "schedule": "daily",
                        "keywords": _ALL_KEYWORDS,
                    }
                ],
            },
        ]
    },
    "Canada": {
        "agencies": [
            {
                "name": "Canadian Space Agency (CSA)",
                "url": "https://www.asc-csa.gc.ca/",
                "sources": [
                    {
                        "name": "CSA Funding Opportunities",
                        "url": "https://www.asc-csa.gc.ca/eng/funding-programs/",
                        "data_type": "grant",
                        "schedule": "weekly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    }
                ],
            },
            {
                "name": "CanadaBuys",
                "url": "https://canadabuys.canada.ca/",
                "sources": [
                    {
                        "name": "CanadaBuys Procurement",
                        "url": "https://canadabuys.canada.ca/en/tender-opportunities",
                        "data_type": "procurement",
                        "schedule": "daily",
                        "keywords": _ALL_KEYWORDS,
                    }
                ],
            },
        ]
    },
    "Japan": {
        "agencies": [
            {
                "name": "JAXA (Japan Aerospace Exploration Agency)",
                "url": "https://global.jaxa.jp/",
                "sources": [
                    {
                        "name": "JAXA Procurement Notices",
                        "url": "https://www.jaxa.jp/procurement/index_j.html",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    }
                ],
            }
        ]
    },
    "Germany": {
        "agencies": [
            {
                "name": "DLR (German Aerospace Center)",
                "url": "https://www.dlr.de/",
                "sources": [
                    {
                        "name": "DLR Tenders",
                        "url": "https://www.dlr.de/dlr/en/desktopdefault.aspx/tabid-10371/",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    }
                ],
            }
        ]
    },
    "France": {
        "agencies": [
            {
                "name": "CNES (French Space Agency)",
                "url": "https://cnes.fr/",
                "sources": [
                    {
                        "name": "CNES Procurement",
                        "url": "https://cnes.fr/en/web/CNES-en/10278-business-opportunities.php",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    }
                ],
            },
            {
                "name": "IGN (Institut National de l'Information Géographique)",
                "url": "https://www.ign.fr/",
                "sources": [
                    {
                        "name": "IGN Tenders",
                        "url": "https://www.ign.fr/",
                        "data_type": "procurement",
                        "schedule": "monthly",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            },
        ]
    },
    "India": {
        "agencies": [
            {
                "name": "ISRO (Indian Space Research Organisation)",
                "url": "https://www.isro.gov.in/",
                "sources": [
                    {
                        "name": "ISRO Tenders",
                        "url": "https://www.isro.gov.in/tenders",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    }
                ],
            },
            {
                "name": "GeM (Government e-Marketplace)",
                "url": "https://gem.gov.in/",
                "sources": [
                    {
                        "name": "GeM Geospatial Bids",
                        "url": "https://gem.gov.in/bidding/bids",
                        "data_type": "procurement",
                        "schedule": "daily",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            },
        ]
    },
    "Brazil": {
        "agencies": [
            {
                "name": "IBGE (Brazilian Institute of Geography and Statistics)",
                "url": "https://www.ibge.gov.br/",
                "sources": [
                    {
                        "name": "IBGE Licitações",
                        "url": "https://www.ibge.gov.br/acesso-informacao/licitacoes-e-contratos.html",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _GEO_KEYWORDS + _CLIMATE_KEYWORDS,
                    }
                ],
            },
            {
                "name": "Comprasnet",
                "url": "https://www.comprasnet.gov.br/",
                "sources": [
                    {
                        "name": "Brazil Federal Procurement Portal",
                        "url": "https://www.comprasnet.gov.br/seguro/loginportal.asp",
                        "data_type": "procurement",
                        "schedule": "daily",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            },
        ]
    },
    "Italy": {
        "agencies": [
            {
                "name": "ASI (Italian Space Agency)",
                "url": "https://www.asi.it/",
                "sources": [
                    {
                        "name": "ASI Bandi e Gare",
                        "url": "https://www.asi.it/bandi-gare-e-contratti/",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    }
                ],
            }
        ]
    },
    "Spain": {
        "agencies": [
            {
                "name": "IGN España",
                "url": "https://www.ign.es/",
                "sources": [
                    {
                        "name": "IGN Spain Tenders",
                        "url": "https://www.ign.es/web/ign/portal",
                        "data_type": "procurement",
                        "schedule": "monthly",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            },
            {
                "name": "Plataforma de Contratación del Sector Público",
                "url": "https://contrataciondelestado.es/",
                "sources": [
                    {
                        "name": "Spain Public Procurement",
                        "url": "https://contrataciondelestado.es/wps/portal/plataforma",
                        "data_type": "procurement",
                        "schedule": "daily",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            },
        ]
    },
    "Netherlands": {
        "agencies": [
            {
                "name": "TenderNed",
                "url": "https://www.tenderned.nl/",
                "sources": [
                    {
                        "name": "TenderNed Dutch Procurement",
                        "url": "https://www.tenderned.nl/aankondigingen",
                        "data_type": "procurement",
                        "schedule": "daily",
                        "keywords": _ALL_KEYWORDS,
                    }
                ],
            }
        ]
    },
    "Norway": {
        "agencies": [
            {
                "name": "Doffin (Norwegian Public Procurement)",
                "url": "https://www.doffin.no/",
                "sources": [
                    {
                        "name": "Doffin Tenders",
                        "url": "https://www.doffin.no/Notice/Search",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _GEO_KEYWORDS + _CLIMATE_KEYWORDS,
                    }
                ],
            },
            {
                "name": "Norwegian Space Agency",
                "url": "https://www.romfartsnorge.no/",
                "sources": [
                    {
                        "name": "Norway Space Tenders",
                        "url": "https://www.romfartsnorge.no/",
                        "data_type": "procurement",
                        "schedule": "monthly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    }
                ],
            },
        ]
    },
    "Sweden": {
        "agencies": [
            {
                "name": "Upphandlingsmyndigheten",
                "url": "https://www.upphandlingsmyndigheten.se/",
                "sources": [
                    {
                        "name": "Sweden Public Procurement",
                        "url": "https://www.upphandlingsmyndigheten.se/",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            }
        ]
    },
    "New Zealand": {
        "agencies": [
            {
                "name": "LINZ (Land Information New Zealand)",
                "url": "https://www.linz.govt.nz/",
                "sources": [
                    {
                        "name": "LINZ Procurement",
                        "url": "https://www.linz.govt.nz/about-linz/procurement",
                        "data_type": "procurement",
                        "schedule": "monthly",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            },
            {
                "name": "GETS (Government Electronic Tender Service)",
                "url": "https://www.gets.govt.nz/",
                "sources": [
                    {
                        "name": "NZ Government Tenders",
                        "url": "https://www.gets.govt.nz/ExternalIndex.htm",
                        "data_type": "procurement",
                        "schedule": "daily",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            },
        ]
    },
    "South Africa": {
        "agencies": [
            {
                "name": "SANSA (South African National Space Agency)",
                "url": "https://www.sansa.org.za/",
                "sources": [
                    {
                        "name": "SANSA Tenders",
                        "url": "https://www.sansa.org.za/business-opportunities/",
                        "data_type": "procurement",
                        "schedule": "monthly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    }
                ],
            },
            {
                "name": "eTenders (South Africa National Treasury)",
                "url": "https://www.etenders.gov.za/",
                "sources": [
                    {
                        "name": "South Africa eTenders",
                        "url": "https://www.etenders.gov.za/home/opportunities",
                        "data_type": "procurement",
                        "schedule": "daily",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            },
        ]
    },
    "Mexico": {
        "agencies": [
            {
                "name": "INEGI (National Statistics and Geography Institute)",
                "url": "https://www.inegi.org.mx/",
                "sources": [
                    {
                        "name": "INEGI Licitaciones",
                        "url": "https://www.inegi.org.mx/inegi/licitaciones/",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            },
            {
                "name": "CompraNet",
                "url": "https://compranet.hacienda.gob.mx/",
                "sources": [
                    {
                        "name": "Mexico Federal Procurement",
                        "url": "https://compranet.hacienda.gob.mx/",
                        "data_type": "procurement",
                        "schedule": "daily",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            },
        ]
    },
    "South Korea": {
        "agencies": [
            {
                "name": "KARI (Korea Aerospace Research Institute)",
                "url": "https://www.kari.re.kr/",
                "sources": [
                    {
                        "name": "KARI Procurement",
                        "url": "https://www.kari.re.kr/",
                        "data_type": "procurement",
                        "schedule": "monthly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    }
                ],
            },
            {
                "name": "Korea ON2ne (National Procurement Service)",
                "url": "https://www.g2b.go.kr/",
                "sources": [
                    {
                        "name": "Korea Public Procurement",
                        "url": "https://www.g2b.go.kr/",
                        "data_type": "procurement",
                        "schedule": "daily",
                        "keywords": _GEO_KEYWORDS,
                    }
                ],
            },
        ]
    },
    "Nigeria": {
        "agencies": [
            {
                "name": "NASRDA (National Space Research and Development Agency)",
                "url": "https://www.nasrda.gov.ng/",
                "sources": [
                    {
                        "name": "NASRDA Tenders",
                        "url": "https://www.nasrda.gov.ng/",
                        "data_type": "procurement",
                        "schedule": "monthly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    }
                ],
            }
        ]
    },
    "Argentina": {
        "agencies": [
            {
                "name": "CNIDEP / CONAE (Argentine Space Agency)",
                "url": "https://www.conae.gov.ar/",
                "sources": [
                    {
                        "name": "CONAE Licitaciones",
                        "url": "https://www.conae.gov.ar/",
                        "data_type": "procurement",
                        "schedule": "monthly",
                        "keywords": _SPACE_KEYWORDS + _GEO_KEYWORDS,
                    }
                ],
            }
        ]
    },
    "World Bank / Multilateral": {
        "agencies": [
            {
                "name": "World Bank Procurement",
                "url": "https://projects.worldbank.org/en/projects-operations/procurement",
                "sources": [
                    {
                        "name": "World Bank Contract Awards / Notices",
                        "url": "https://projects.worldbank.org/en/projects-operations/procurement",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _GEO_KEYWORDS + _CLIMATE_KEYWORDS,
                    }
                ],
            },
            {
                "name": "UNDP Procurement",
                "url": "https://procurement-notices.undp.org/",
                "sources": [
                    {
                        "name": "UNDP Procurement Notices",
                        "url": "https://procurement-notices.undp.org/",
                        "data_type": "procurement",
                        "schedule": "weekly",
                        "keywords": _GEO_KEYWORDS + _CLIMATE_KEYWORDS,
                    }
                ],
            },
        ]
    },
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_all_procurement_sources():
    """
    Return a flat list of all procurement source configurations.

    Each entry is a dict with keys:
        country   (str)  - Country or region name
        name      (str)  - Source / portal name
        url       (str)  - Primary URL for the source
        keywords  (list) - Relevant search keywords
    """
    sources = []
    for country, config in GLOBAL_SOURCES.items():
        for agency in config.get("agencies", []):
            for source in agency.get("sources", []):
                sources.append({
                    "country": country,
                    "name": source["name"],
                    "url": source["url"],
                    "keywords": source.get("keywords", _ALL_KEYWORDS),
                })
    return sources


def get_scrape_schedule():
    """
    Return sources grouped by their scraping frequency.

    Returns a dict keyed by frequency ('daily', 'weekly', 'monthly',
    'quarterly', 'yearly'), each containing a list of source dicts with
    keys: country, source, data_type, url.
    """
    schedule = {
        "daily": [],
        "weekly": [],
        "monthly": [],
        "quarterly": [],
        "yearly": [],
    }

    for country, config in GLOBAL_SOURCES.items():
        for agency in config.get("agencies", []):
            for source in agency.get("sources", []):
                frequency = source.get("schedule", "weekly")
                if frequency not in schedule:
                    frequency = "weekly"
                schedule[frequency].append({
                    "country": country,
                    "source": source["name"],
                    "data_type": source.get("data_type", "procurement"),
                    "url": source.get("url", ""),
                })

    return schedule
