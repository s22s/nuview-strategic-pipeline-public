import json
import os
import sys
import time
from pathlib import Path

from tqdm import tqdm

# --- PATH FIX: Force Python to see the project root ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.loader import load_plugins

# ----------------------------------------------------

OUTPUT = Path("data/raw/all_opportunities.json")
STATUS = Path("data/processed/api_status.json")

def main():
    print("\n🚀 INITIALIZING GLOBAL INTELLIGENCE SWEEP...")

    all_data = []
    report = {}

    # 1. LOAD PLUGINS
    scrapers = load_plugins()

    if not scrapers:
        print("⚠️  No plugins found. Creating Factory Defaults...")
        try:
            import scripts.scrapers.factory_states as factory
            factory.main()
            scrapers = load_plugins()
        except ImportError:
            pass

    print(f"   ► Loaded {len(scrapers)} Intelligence Agents.")
    print("   ► Targets Acquired. Engaging...\n")

    # 2. EXECUTE
    with tqdm(total=len(scrapers), desc="   📡 Scanning", unit="source", colour="green") as pbar:
        for fetch in scrapers:
            name = fetch.__module__.split('.')[-1]
            pbar.set_description(f"   📡 Scanning: {name.upper()}")

            try:
                time.sleep(0.1)
                data = fetch()
                all_data.extend(data)
                report[name] = {"status": "healthy", "count": len(data)}
            except Exception as e:
                report[name] = {"status": "failed", "error": str(e)}

            pbar.update(1)

    # 3. SAVE
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(all_data, f, indent=2)

    STATUS.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS, "w") as f:
        json.dump(report, f, indent=2)

    print("\n✅ MISSION COMPLETE.")
    print(f"   ► Total Intel: {len(all_data)}")

if __name__ == "__main__":
    main()
