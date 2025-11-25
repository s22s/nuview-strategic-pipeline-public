import importlib
import pkgutil

# DEBUG PRINT to prove this file is loading
print("   ... [System] Loading Scraper Plugin Architecture ...")

def load_scrapers():
    package = __name__
    scrapers = []
    path = __path__

    for _, modname, _ in pkgutil.iter_modules(path):
        if modname.startswith("__"):
            continue
        try:
            module = importlib.import_module(f"{package}.{modname}")
            if hasattr(module, "fetch"):
                scrapers.append(module.fetch)
        except Exception as e:
            print(f"Error loading {modname}: {e}")
    return scrapers
