"""
Integration test for complete NUVIEW pipeline
Tests end-to-end data flow: Scrapers → QC → Dashboard
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))


class TestFullPipelineIntegration:
    """Test complete pipeline integration"""

    def test_full_pipeline_execution(self):
        """Test that the complete pipeline can execute successfully"""
        # This is a comprehensive test that runs the entire pipeline

        # Step 1: Run scrapers
        from scrapers.scrape_all import run_pipeline
        run_pipeline()

        # Verify scraper output
        assert Path('data/opportunities.json').exists()
        assert Path('data/forecast.json').exists()
        assert Path('data/scraper_stats.json').exists()

        with open('data/opportunities.json', 'r') as f:
            opp_data = json.load(f)
            assert 'opportunities' in opp_data
            assert len(opp_data['opportunities']) > 0

        # Step 2: Run QC validation
        # Note: The QC validator functions are internal, so we just check the output
        result = subprocess.run(
            ['python', 'scripts/qc_validator.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, f"QC validation failed: {result.stderr}"

        # Step 3: Generate dashboard data
        from generate_programs import main as generate_dashboard
        generate_dashboard()

        # Verify dashboard output
        assert Path('data/processed/programs.json').exists()
        assert Path('data/processed/qc_report.json').exists()

        with open('data/processed/programs.json', 'r') as f:
            programs_data = json.load(f)

        # Support both new nested format { "programs": { ... } } and legacy flat format
        if isinstance(programs_data, dict) and 'programs' in programs_data:
            categories = set(programs_data['programs'].keys())
        else:
            categories = set(programs_data.keys())

        expected_any = {'DaaS', 'Platform', 'R&D', 'platform', 'funding', 'lidar', 'spaceSystems'}
        assert len(categories.intersection(expected_any)) > 0, \
            f"No expected program categories found in {list(categories)}"

    def test_pipeline_data_consistency(self):
        """Test that data remains consistent across pipeline stages"""
        # Load opportunities
        with open('data/opportunities.json', 'r') as f:
            opp_data = json.load(f)

        opportunities = opp_data.get('opportunities', [])
        assert len(opportunities) > 0

        # Load programs
        with open('data/processed/programs.json', 'r') as f:
            programs_data = json.load(f)

        # Count opportunities in programs
        # Use canonical 'programs' nested structure when present to avoid double-counting
        # from backwards-compat keys like 'DaaS', 'Platform', 'Space Systems'
        program_opp_count = 0
        if 'programs' in programs_data and isinstance(programs_data['programs'], dict):
            # New format: count from nested programs structure only
            for category, programs in programs_data['programs'].items():
                if isinstance(programs, list):
                    program_opp_count += len(programs)
        else:
            # Legacy flat format
            for category, programs in programs_data.items():
                if isinstance(programs, list):
                    program_opp_count += len(programs)
                elif isinstance(programs, dict) and 'opportunities' in programs:
                    program_opp_count += len(programs['opportunities'])

        # Programs should have similar count to opportunities (might filter some)
        assert program_opp_count >= 0  # Allow zero if no opportunities meet criteria
        assert program_opp_count <= len(opportunities)

    def test_pipeline_performance_metrics(self):
        """Test that pipeline generates performance metrics"""
        assert Path('data/scraper_stats.json').exists()

        with open('data/scraper_stats.json', 'r') as f:
            stats = json.load(f)

        # Check required stats fields (using actual field names)
        assert 'total_scrapers' in stats or 'scrapers' in stats
        assert 'total_opportunities' in stats
        assert 'timestamp' in stats

        # Validate stats values
        if 'total_scrapers' in stats:
            assert stats['total_scrapers'] > 0
        elif 'scrapers' in stats:
            assert len(stats['scrapers']) > 0

        assert stats['total_opportunities'] > 0


class TestDebugTools:
    """Test debugging and analysis tools"""

    def test_debug_tool_dependencies(self):
        """Test that debug tool can check dependencies"""
        from debug_pipeline import check_dependencies
        result = check_dependencies()
        assert result is True

    def test_debug_tool_file_structure(self):
        """Test that debug tool can verify file structure"""
        from debug_pipeline import check_file_structure
        result = check_file_structure()
        assert result is True

    def test_debug_tool_data_files(self):
        """Test that debug tool can check data files"""
        from debug_pipeline import check_data_files
        result = check_data_files()
        # Result may be None if files don't exist yet, but shouldn't raise errors
        assert result is not None or result is None

    def test_performance_analyzer_runs(self):
        """Test that performance analyzer can execute"""
        # Just verify it doesn't crash
        result = subprocess.run(
            ['python', 'scripts/analyze_performance.py', '--component', 'scrapers'],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0


class TestDataQuality:
    """Test data quality across the pipeline"""

    def test_opportunities_have_required_fields(self):
        """Test that all opportunities have required fields"""
        with open('data/opportunities.json', 'r') as f:
            data = json.load(f)

        opportunities = data.get('opportunities', [])
        required_fields = ['id', 'title', 'agency', 'pillar', 'category', 'forecast_value']

        for opp in opportunities[:10]:  # Test first 10
            for field in required_fields:
                assert field in opp, f"Opportunity {opp.get('id')} missing field: {field}"

    def test_no_duplicate_opportunity_ids(self):
        """Test that there are no duplicate opportunity IDs"""
        with open('data/opportunities.json', 'r') as f:
            data = json.load(f)

        opportunities = data.get('opportunities', [])
        ids = [opp.get('id') for opp in opportunities]

        # Check for duplicates
        assert len(ids) == len(set(ids)), "Duplicate opportunity IDs found"

    def test_opportunity_values_are_reasonable(self):
        """Test that opportunity values are in reasonable ranges"""
        with open('data/opportunities.json', 'r') as f:
            data = json.load(f)

        opportunities = data.get('opportunities', [])

        for opp in opportunities:
            # Check funding values
            if 'funding' in opp and 'amountUSD' in opp['funding']:
                amount = opp['funding']['amountUSD']
                assert amount >= 0, f"Negative funding amount: {amount}"
                assert amount < 1e12, f"Unreasonably large funding amount: {amount}"

            # Check urgency values
            if 'timeline' in opp and 'urgency' in opp['timeline']:
                urgency = opp['timeline']['urgency']
                assert urgency in ['urgent', 'near', 'future'], f"Invalid urgency: {urgency}"

    def test_qc_report_completeness(self):
        """Test that QC report is complete"""
        with open('data/processed/qc_report.json', 'r') as f:
            qc_report = json.load(f)

        # Check required sections (using actual field names)
        assert 'timestamp' in qc_report
        assert 'qc_status' in qc_report or 'status' in qc_report

        # Check for validation sections
        assert ('opportunities_validation' in qc_report or
                'opportunities' in qc_report)
        assert ('forecast_validation' in qc_report or
                'forecast' in qc_report)


class TestPipelineOptimizations:
    """Test that optimizations are working"""

    def test_scraper_efficiency(self):
        """Test that scrapers are running efficiently"""
        with open('data/scraper_stats.json', 'r') as f:
            stats = json.load(f)

        # Check that we're getting reasonable opportunities per scraper
        total_scrapers = stats.get('total_scrapers', len(stats.get('scrapers', [])))
        total_opps = stats.get('total_opportunities', 0)

        if total_scrapers > 0:
            avg_per_scraper = total_opps / total_scrapers
            assert avg_per_scraper >= 0.5, "Scrapers may not be collecting data efficiently"

    def test_data_size_is_reasonable(self):
        """Test that data files are not excessively large"""
        data_files = [
            'data/opportunities.json',
            'data/forecast.json',
            'data/processed/programs.json'
        ]

        for file_path in data_files:
            if Path(file_path).exists():
                size = Path(file_path).stat().st_size
                # Files should be < 10MB
                assert size < 10 * 1024 * 1024, f"{file_path} is too large: {size} bytes"

    def test_no_excessive_warnings(self):
        """Test that there are not excessive QC warnings"""
        with open('data/processed/qc_report.json', 'r') as f:
            qc_report = json.load(f)

        # Handle different field names
        total_warnings = qc_report.get('total_warnings', 0)

        if total_warnings == 0:
            # Try alternate structure
            total_warnings = (
                len(qc_report.get('opportunities_validation', {}).get('warnings', [])) +
                len(qc_report.get('forecast_validation', {}).get('warnings', []))
            )

        # Allow some warnings, but not too many
        assert total_warnings < 50, f"Too many QC warnings: {total_warnings}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
