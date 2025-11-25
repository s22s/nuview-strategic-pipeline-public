#!/usr/bin/env python3
"""
NUVIEW Strategic Pipeline - Performance Analysis Tool
Analyze and optimize pipeline performance
Usage: python scripts/analyze_performance.py [--component COMPONENT]
"""

import json
import os
import sys
from datetime import datetime
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


def analyze_scraper_performance():
    """Analyze scraper performance from stats"""
    log_info("Analyzing scraper performance...")

    if not Path('data/scraper_stats.json').exists():
        log_warning("Scraper stats not found - run scrapers first")
        return

    with open('data/scraper_stats.json', 'r') as f:
        stats = json.load(f)

    print("\n" + "=" * 80)
    print("SCRAPER PERFORMANCE ANALYSIS")
    print("=" * 80)

    if 'scrapersRun' in stats:
        print(f"\nTotal Scrapers: {stats['scrapersRun']}")

    if 'totalOpportunities' in stats:
        print(f"Total Opportunities: {stats['totalOpportunities']}")
        if stats['scrapersRun'] > 0:
            avg_per_scraper = stats['totalOpportunities'] / stats['scrapersRun']
            print(f"Average per Scraper: {avg_per_scraper:.2f}")

    if 'totalOpportunities' in stats and 'timestamp' in stats:
        print(f"\nLast Run: {stats['timestamp']}")

    # Analyze by source type
    if Path('data/opportunities.json').exists():
        with open('data/opportunities.json', 'r') as f:
            data = json.load(f)

        opportunities = data.get('opportunities', [])
        if opportunities:
            # Group by pillar
            pillars = {}
            for opp in opportunities:
                pillar = opp.get('pillar', 'Unknown')
                pillars[pillar] = pillars.get(pillar, 0) + 1

            print("\nOpportunities by Pillar:")
            for pillar, count in sorted(pillars.items(), key=lambda x: x[1], reverse=True):
                print(f"  {pillar}: {count}")

            # Group by urgency
            urgencies = {}
            for opp in opportunities:
                urgency = opp.get('timeline', {}).get('urgency', 'Unknown')
                urgencies[urgency] = urgencies.get(urgency, 0) + 1

            print("\nOpportunities by Urgency:")
            for urgency, count in sorted(urgencies.items(), key=lambda x: x[1], reverse=True):
                print(f"  {urgency}: {count}")

    print("=" * 80)


def analyze_data_quality():
    """Analyze data quality metrics"""
    log_info("Analyzing data quality...")

    if not Path('data/processed/qc_report.json').exists():
        log_warning("QC report not found - run QC validator first")
        return

    with open('data/processed/qc_report.json', 'r') as f:
        qc_report = json.load(f)

    print("\n" + "=" * 80)
    print("DATA QUALITY ANALYSIS")
    print("=" * 80)

    print(f"\nQC Status: {qc_report.get('status', 'Unknown')}")

    # Opportunities validation
    opp_data = qc_report.get('opportunities', {})
    print("\nOpportunities Validation:")
    print(f"  Status: {opp_data.get('status', 'Unknown')}")
    print(f"  Errors: {len(opp_data.get('errors', []))}")
    print(f"  Warnings: {len(opp_data.get('warnings', []))}")

    if opp_data.get('errors'):
        print("\n  Error Details:")
        for error in opp_data['errors'][:5]:  # Show first 5
            print(f"    - {error}")

    # Forecast validation
    forecast_data = qc_report.get('forecast', {})
    print("\nForecast Validation:")
    print(f"  Status: {forecast_data.get('status', 'Unknown')}")
    print(f"  Errors: {len(forecast_data.get('errors', []))}")
    print(f"  Warnings: {len(forecast_data.get('warnings', []))}")

    # Source verification
    if 'source_matrix' in qc_report:
        matrix = qc_report['source_matrix']
        print("\nSource Verification:")
        print(f"  Total Opportunities: {matrix.get('total_opportunities', 0)}")
        print(f"  Verified: {matrix.get('verified_opportunities', 0)}")
        print(f"  Missing Sources: {matrix.get('missing_sources', 0)}")
        print(f"  Bathymetry Flagged: {matrix.get('bathymetry_flagged', 0)}")

    print("=" * 80)


def analyze_pipeline_efficiency():
    """Analyze overall pipeline efficiency"""
    log_info("Analyzing pipeline efficiency...")

    print("\n" + "=" * 80)
    print("PIPELINE EFFICIENCY ANALYSIS")
    print("=" * 80)

    # Check file sizes
    print("\nData File Sizes:")
    data_files = [
        'data/opportunities.json',
        'data/forecast.json',
        'data/scraper_stats.json',
        'data/processed/programs.json',
        'data/processed/qc_report.json',
        'data/processed/sources_matrix.csv'
    ]

    total_size = 0
    for file_path in data_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            total_size += size
            print(f"  {file_path}: {size:,} bytes ({size/1024:.2f} KB)")

    print(f"\n  Total Data Size: {total_size:,} bytes ({total_size/1024:.2f} KB)")

    # Check processing efficiency
    if Path('data/opportunities.json').exists():
        with open('data/opportunities.json', 'r') as f:
            data = json.load(f)

        opp_count = len(data.get('opportunities', []))
        if opp_count > 0:
            avg_size = total_size / opp_count
            print(f"\n  Average size per opportunity: {avg_size:.2f} bytes")

    print("\nRecommendations:")
    if total_size > 1024 * 1024:  # > 1 MB
        log_warning("Consider data compression for large datasets")
    else:
        log_success("Data size is optimal")

    print("=" * 80)


def analyze_code_quality():
    """Analyze code quality metrics"""
    log_info("Analyzing code quality...")

    print("\n" + "=" * 80)
    print("CODE QUALITY ANALYSIS")
    print("=" * 80)

    # Count Python files
    python_files = list(Path('.').rglob('*.py'))
    print(f"\nTotal Python Files: {len(python_files)}")

    # Count lines of code
    total_lines = 0
    for py_file in python_files:
        try:
            with open(py_file, 'r') as f:
                total_lines += len(f.readlines())
        except Exception:
            pass

    print(f"Total Lines of Code: {total_lines:,}")

    # Run ruff to get linting stats
    try:
        import subprocess
        result = subprocess.run(['ruff', 'check', '.', '--statistics'],
                                capture_output=True, text=True)
        if result.stdout:
            print("\nLinting Issues:")
            for line in result.stdout.strip().split('\n')[-10:]:  # Last 10 lines
                print(f"  {line}")
    except Exception:
        log_warning("Could not run ruff - install with 'pip install ruff'")

    print("=" * 80)


def generate_optimization_report():
    """Generate comprehensive optimization report"""
    log_info("Generating optimization report...")

    report = {
        'timestamp': datetime.now().isoformat(),
        'recommendations': []
    }

    # Check for optimization opportunities
    if Path('data/opportunities.json').exists():
        with open('data/opportunities.json', 'r') as f:
            data = json.load(f)
            opp_count = len(data.get('opportunities', []))

            if opp_count < 50:
                report['recommendations'].append({
                    'category': 'Scraper Coverage',
                    'severity': 'medium',
                    'message': f'Only {opp_count} opportunities found - consider adding more scrapers'
                })

    # Check QC report
    if Path('data/processed/qc_report.json').exists():
        with open('data/processed/qc_report.json', 'r') as f:
            qc_report = json.load(f)

            total_errors = (len(qc_report.get('opportunities', {}).get('errors', [])) +
                            len(qc_report.get('forecast', {}).get('errors', [])))

            if total_errors > 0:
                report['recommendations'].append({
                    'category': 'Data Quality',
                    'severity': 'high',
                    'message': f'{total_errors} QC errors found - fix data quality issues'
                })

    print("\n" + "=" * 80)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)

    if not report['recommendations']:
        log_success("No optimization recommendations - system is running optimally!")
    else:
        for rec in report['recommendations']:
            severity_color = COLOR_RED if rec['severity'] == 'high' else COLOR_ORANGE
            print(f"\n{severity_color}[{rec['severity'].upper()}] {rec['category']}{COLOR_RESET}")
            print(f"  {rec['message']}")

    print("=" * 80)

    # Save report
    report_path = Path('data/processed/optimization_report.json')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    log_success(f"Optimization report saved to {report_path}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='NUVIEW Pipeline Performance Analysis Tool')
    parser.add_argument('--component', '-c',
                        choices=['scrapers', 'quality', 'efficiency', 'code', 'all'],
                        default='all', help='Component to analyze')

    args = parser.parse_args()

    print("=" * 80)
    print("NUVIEW STRATEGIC PIPELINE - PERFORMANCE ANALYSIS TOOL")
    print("=" * 80)
    print()

    if args.component in ['scrapers', 'all']:
        analyze_scraper_performance()

    if args.component in ['quality', 'all']:
        analyze_data_quality()

    if args.component in ['efficiency', 'all']:
        analyze_pipeline_efficiency()

    if args.component in ['code', 'all']:
        analyze_code_quality()

    if args.component == 'all':
        generate_optimization_report()


if __name__ == "__main__":
    main()
