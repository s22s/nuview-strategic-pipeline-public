import importlib
import os
import pkgutil
import sys

# Ensure we can see the scripts package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def load_plugins():
    """Manual plugin loader that bypasses init caching issues."""
    scrapers = []

    # Point explicitly to the scrapers directory
    scrapers_path = os.path.join(os.path.dirname(__file__), 'scrapers')

    print(f"   ... Scanning {scrapers_path} ...")

    # Iterate files in scripts/scrapers/
    for _, name, _ in pkgutil.iter_modules([scrapers_path]):
        if name.startswith("__"):
            continue
        try:
            # Dynamically import scripts.scrapers.{name}
            module = importlib.import_module(f"scripts.scrapers.{name}")
            if hasattr(module, "fetch"):
                scrapers.append(module.fetch)
        except Exception:
            # Silent fail for non-scraper files to keep logs clean
            pass

    return scrapers
