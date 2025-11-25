#!/usr/bin/env python3
"""
URL Validation Module for NUVIEW Strategic Pipeline
Validates that opportunity source links are accessible
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests


def is_valid_url(url):
    """Check if URL is properly formatted"""
    if not url:
        return False
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def check_url_accessible(url, timeout=10):
    """
    Check if a URL is accessible (returns HTTP 200)

    Args:
        url: The URL to check
        timeout: Request timeout in seconds

    Returns:
        dict with status info: {'accessible': bool, 'status_code': int, 'error': str}
    """
    if not is_valid_url(url):
        return {
            'accessible': False,
            'status_code': None,
            'error': 'Invalid URL format'
        }

    try:
        # Use HEAD request for efficiency (doesn't download body)
        response = requests.head(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={'User-Agent': 'NUVIEW-Pipeline-Validator/1.0'}
        )

        accessible = response.status_code < 400

        return {
            'accessible': accessible,
            'status_code': response.status_code,
            'error': None if accessible else f'HTTP {response.status_code}'
        }

    except requests.exceptions.Timeout:
        return {
            'accessible': False,
            'status_code': None,
            'error': 'Request timeout'
        }
    except requests.exceptions.ConnectionError:
        return {
            'accessible': False,
            'status_code': None,
            'error': 'Connection failed'
        }
    except requests.exceptions.TooManyRedirects:
        return {
            'accessible': False,
            'status_code': None,
            'error': 'Too many redirects'
        }
    except Exception as e:
        return {
            'accessible': False,
            'status_code': None,
            'error': str(e)[:100]  # Limit error message length
        }


def validate_opportunity_url(opp, timeout=10):
    """
    Validate URL for a single opportunity

    Args:
        opp: Opportunity dict with 'link' field
        timeout: Request timeout

    Returns:
        dict with validation results
    """
    opp_id = opp.get('id', 'unknown')
    url = opp.get('link', '')

    result = check_url_accessible(url, timeout)

    return {
        'opportunity_id': opp_id,
        'url': url,
        **result
    }


def validate_all_urls(opportunities, max_workers=10, timeout=10):
    """
    Validate URLs for multiple opportunities in parallel

    Args:
        opportunities: List of opportunity dicts
        max_workers: Maximum concurrent requests
        timeout: Request timeout per URL

    Returns:
        dict with validation results and statistics
    """
    results = []
    total = len(opportunities)

    # Parallel URL checking for efficiency
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_opp = {
            executor.submit(validate_opportunity_url, opp, timeout): opp
            for opp in opportunities
        }

        for future in as_completed(future_to_opp):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                opp = future_to_opp[future]
                results.append({
                    'opportunity_id': opp.get('id', 'unknown'),
                    'url': opp.get('link', ''),
                    'accessible': False,
                    'status_code': None,
                    'error': f'Validation error: {str(e)[:100]}'
                })

    # Calculate statistics
    accessible_count = sum(1 for r in results if r['accessible'])
    inaccessible_count = total - accessible_count

    # Group errors
    error_types = {}
    for r in results:
        if not r['accessible'] and r['error']:
            error_type = r['error'].split(':')[0]  # Get error category
            error_types[error_type] = error_types.get(error_type, 0) + 1

    return {
        'total_checked': total,
        'accessible': accessible_count,
        'inaccessible': inaccessible_count,
        'success_rate': (accessible_count / total * 100) if total > 0 else 0,
        'error_types': error_types,
        'results': results
    }


def get_inaccessible_opportunities(validation_results):
    """
    Get list of opportunities with inaccessible URLs

    Args:
        validation_results: Results from validate_all_urls()

    Returns:
        List of inaccessible opportunity IDs with error info
    """
    return [
        {
            'id': r['opportunity_id'],
            'url': r['url'],
            'error': r['error']
        }
        for r in validation_results['results']
        if not r['accessible']
    ]


def generate_url_validation_report(validation_results):
    """
    Generate human-readable URL validation report

    Args:
        validation_results: Results from validate_all_urls()

    Returns:
        String report
    """
    stats = validation_results
    report = []

    report.append("=" * 60)
    report.append("URL VALIDATION REPORT")
    report.append("=" * 60)
    report.append(f"Total URLs Checked: {stats['total_checked']}")
    report.append(f"Accessible: {stats['accessible']} ({stats['success_rate']:.1f}%)")
    report.append(f"Inaccessible: {stats['inaccessible']}")

    if stats['error_types']:
        report.append("\nError Breakdown:")
        for error_type, count in sorted(stats['error_types'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {error_type}: {count}")

    inaccessible = get_inaccessible_opportunities(validation_results)
    if inaccessible:
        report.append(f"\nInaccessible Opportunities ({len(inaccessible)}):")
        for item in inaccessible[:10]:  # Show first 10
            report.append(f"  {item['id']}: {item['error']}")
            report.append(f"    URL: {item['url'][:80]}")

        if len(inaccessible) > 10:
            report.append(f"  ... and {len(inaccessible) - 10} more")

    report.append("=" * 60)

    return "\n".join(report)


if __name__ == "__main__":
    # Test with sample opportunities
    import json
    from pathlib import Path

    data_file = Path("data/opportunities.json")
    if data_file.exists():
        with open(data_file) as f:
            data = json.load(f)

        opportunities = data.get('opportunities', [])
        if opportunities:
            print(f"Validating URLs for {len(opportunities)} opportunities...")
            print("This may take a minute...\n")

            results = validate_all_urls(opportunities, max_workers=20, timeout=5)

            print(generate_url_validation_report(results))

            # Save detailed results
            output_file = Path("data/processed/url_validation.json")
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nDetailed results saved to: {output_file}")
    else:
        print("No opportunities data found. Run scrapers first.")
