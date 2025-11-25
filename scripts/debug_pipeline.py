#!/usr/bin/env python3
"""
NUVIEW Strategic Pipeline - Debug & Diagnostic Tool
Comprehensive debugging and diagnostics for the full pipeline
Usage: python scripts/debug_pipeline.py [--verbose] [--component COMPONENT]
"""

import json
import os
import sys
import time
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

# ANSI color codes
COLOR_GREEN = '\033[92m'
COLOR_ORANGE = '\033[93m'
COLOR_RED = '\033[91m'
COLOR_BLUE = '\033[94m'
COLOR_RESET = '\033[0m'


def log_info(msg):
    print(f"{COLOR_BLUE}ℹ️  {msg}{COLOR_RESET}")


def log_success(msg):
    print(f"{COLOR_GREEN}✅ {msg}{COLOR_RESET}")


def log_warning(msg):
    print(f"{COLOR_ORANGE}⚠️  {msg}{COLOR_RESET}")


def log_error(msg):
    print(f"{COLOR_RED}❌ {msg}{COLOR_RESET}")


def check_dependencies():
    """Check if all required Python dependencies are installed"""
    log_info("Checking dependencies...")
    dependencies = {
        'pandas': 'pandas',
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'pdfplumber': 'pdfplumber',
        'jsonschema': 'jsonschema',
        'ruff': 'ruff'
    }

    all_ok = True
    for module, package in dependencies.items():
        try:
            __import__(module)
            log_success(f"{package} is installed")
        except ImportError:
            log_error(f"{package} is NOT installed")
            all_ok = False

    return all_ok


def check_file_structure():
    """Check if all required directories and files exist"""
    log_info("Checking file structure...")
    required_paths = [
        'data/',
        'data/processed/',
        'scripts/',
        'scripts/scrapers/',
        'schemas/',
        'schemas/opportunities.json',
        'requirements.txt',
        'pyproject.toml',
        'pytest.ini'
    ]

    all_ok = True
    for path in required_paths:
        if Path(path).exists():
            log_success(f"{path} exists")
        else:
            log_error(f"{path} is MISSING")
            all_ok = False

    return all_ok


def check_data_files():
    """Check data files and their validity"""
    log_info("Checking data files...")
    data_files = {
        'data/opportunities.json': 'Opportunities data',
        'data/forecast.json': 'Forecast data',
        'data/scraper_stats.json': 'Scraper statistics',
        'data/processed/programs.json': 'Dashboard programs',
        'data/processed/qc_report.json': 'QC report',
        'data/processed/sources_matrix.csv': 'Source verification matrix'
    }

    all_ok = True
    for file_path, description in data_files.items():
        if Path(file_path).exists():
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        log_success(f"{description}: Valid JSON ({len(str(data))} bytes)")
                else:
                    size = Path(file_path).stat().st_size
                    log_success(f"{description}: {size} bytes")
            except Exception as e:
                log_error(f"{description}: Error reading - {e}")
                all_ok = False
        else:
            log_warning(f"{description}: File not found (may need to run pipeline)")

    return all_ok


def test_scraper_system(verbose=False):
    """Test the scraper system"""
    log_info("Testing scraper system...")
    try:
        from scrapers.scrape_all import run_pipeline
        start_time = time.time()
        run_pipeline()
        elapsed = time.time() - start_time
        log_success(f"Scraper system completed in {elapsed:.2f} seconds")

        # Check output
        if Path('data/opportunities.json').exists():
            with open('data/opportunities.json', 'r') as f:
                data = json.load(f)
                opp_count = len(data.get('opportunities', []))
                log_success(f"Collected {opp_count} opportunities")
        return True
    except Exception as e:
        log_error(f"Scraper system failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def test_qc_system(verbose=False):
    """Test the QC validation system"""
    log_info("Testing QC validation system...")
    try:
        from qc_validator import generate_sources_matrix, validate_forecast, validate_opportunities
        start_time = time.time()

        # Validate opportunities
        opp_errors, opp_warnings, _ = validate_opportunities()
        forecast_errors, forecast_warnings, _ = validate_forecast()

        # Generate sources matrix
        if Path('data/opportunities.json').exists():
            with open('data/opportunities.json', 'r') as f:
                data = json.load(f)
            matrix_export_status, matrix_stats = generate_sources_matrix(data)

        elapsed = time.time() - start_time

        if len(opp_errors) == 0 and len(forecast_errors) == 0:
            log_success(f"QC validation passed in {elapsed:.2f} seconds")
            log_info(f"  Opportunities warnings: {len(opp_warnings)}")
            log_info(f"  Forecast warnings: {len(forecast_warnings)}")
            return True
        else:
            log_error(f"QC validation failed with {len(opp_errors) + len(forecast_errors)} errors")
            if verbose:
                for error in opp_errors + forecast_errors:
                    log_error(f"  {error}")
            return False
    except Exception as e:
        log_error(f"QC system failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def test_dashboard_generation(verbose=False):
    """Test dashboard data generation"""
    log_info("Testing dashboard generation...")
    try:
        from generate_programs import main
        start_time = time.time()
        main()
        elapsed = time.time() - start_time
        log_success(f"Dashboard generation completed in {elapsed:.2f} seconds")

        # Check output
        if Path('data/processed/programs.json').exists():
            with open('data/processed/programs.json', 'r') as f:
                data = json.load(f)
                log_success(f"Generated programs data: {len(str(data))} bytes")
        return True
    except Exception as e:
        log_error(f"Dashboard generation failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def run_integration_test(verbose=False):
    """Run full integration test of the pipeline"""
    log_info("Running full integration test...")
    print("=" * 80)

    results = {
        'dependencies': check_dependencies(),
        'file_structure': check_file_structure(),
        'data_files': check_data_files(),
        'scraper_system': test_scraper_system(verbose),
        'qc_system': test_qc_system(verbose),
        'dashboard_generation': test_dashboard_generation(verbose)
    }

    print("\n" + "=" * 80)
    log_info("INTEGRATION TEST SUMMARY")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")

    all_passed = all(results.values())
    print("=" * 80)
    if all_passed:
        log_success("🎯 ALL INTEGRATION TESTS PASSED")
    else:
        log_error("❌ SOME INTEGRATION TESTS FAILED")
    print("=" * 80)

    return all_passed


def show_system_info():
    """Display system information"""
    log_info("System Information")
    print("=" * 80)

    # Python version
    print(f"Python: {sys.version.split()[0]}")

    # Repository info
    if Path('.git').exists():
        try:
            import subprocess
            branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()
            commit = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], text=True).strip()
            print(f"Git Branch: {branch}")
            print(f"Git Commit: {commit}")
        except Exception:
            pass

    # Data statistics
    if Path('data/opportunities.json').exists():
        with open('data/opportunities.json', 'r') as f:
            data = json.load(f)
            print(f"Opportunities: {len(data.get('opportunities', []))}")
            if 'meta' in data:
                print(f"Last Updated: {data['meta'].get('timestamp', 'Unknown')}")

    print("=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='NUVIEW Pipeline Debug & Diagnostic Tool')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output with stack traces')
    parser.add_argument('--component', '-c', choices=['deps', 'files', 'data', 'scrapers', 'qc', 'dashboard', 'all'],
                        default='all', help='Component to test')
    parser.add_argument('--info', action='store_true', help='Show system information')

    args = parser.parse_args()

    print("=" * 80)
    print("NUVIEW STRATEGIC PIPELINE - DEBUG & DIAGNOSTIC TOOL")
    print("=" * 80)
    print()

    if args.info:
        show_system_info()
        return

    if args.component == 'all':
        success = run_integration_test(args.verbose)
        sys.exit(0 if success else 1)
    else:
        component_tests = {
            'deps': check_dependencies,
            'files': check_file_structure,
            'data': check_data_files,
            'scrapers': lambda: test_scraper_system(args.verbose),
            'qc': lambda: test_qc_system(args.verbose),
            'dashboard': lambda: test_dashboard_generation(args.verbose)
        }

        if args.component in component_tests:
            success = component_tests[args.component]()
            sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
