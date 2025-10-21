#!/usr/bin/env python3
"""
scripts/view_test_results.py

View and analyze test results from agent testing.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def load_test_results(results_path: str) -> Dict[str, Any]:
    """Load test results from JSON file."""
    with open(results_path, 'r') as f:
        return json.load(f)


def print_summary(results: Dict[str, Any]):
    """Print test results summary."""
    print("\n" + "="*80)
    print(f"TEST RESULTS: {results['agent_name']}")
    print("="*80)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Total Tests: {len(results['test_results'])}")

    # Count statuses
    passed = sum(1 for r in results['test_results'] if r['status'] == 'passed')
    failed = sum(1 for r in results['test_results'] if r['status'] == 'failed')
    errors = sum(1 for r in results['test_results'] if r['status'] == 'error')

    print(f"\n✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"⚠ Errors: {errors}")

    success_rate = (passed / len(results['test_results']) * 100) if results['test_results'] else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")

    # Average execution time
    avg_time = sum(r['execution_time_seconds'] for r in results['test_results']) / len(results['test_results'])
    print(f"Avg Execution Time: {avg_time:.2f}s")


def print_detailed_results(results: Dict[str, Any]):
    """Print detailed test results."""
    print("\n" + "="*80)
    print("DETAILED RESULTS")
    print("="*80)

    for i, test_result in enumerate(results['test_results'], 1):
        test_case = test_result['test_case']
        status = test_result['status']

        # Status emoji
        status_emoji = {
            'passed': '✓',
            'failed': '✗',
            'error': '⚠'
        }.get(status, '?')

        print(f"\n{i}. {status_emoji} {test_case['test_name']}")
        print(f"   ID: {test_case['test_id']}")
        print(f"   Status: {status}")
        print(f"   Time: {test_result['execution_time_seconds']:.2f}s")

        if status == 'failed':
            validation = test_result.get('validation_details', {})
            print(f"   Failure Reason: {validation.get('reason', 'Unknown')}")

            # Show failed checks
            checks = validation.get('checks', [])
            failed_checks = [c for c in checks if not c.get('passed')]
            if failed_checks:
                print("   Failed Checks:")
                for check in failed_checks:
                    print(f"     - {check.get('check')}: expected {check.get('expected')}, got {check.get('actual')}")

        elif status == 'error':
            print(f"   Error: {test_result.get('error_message', 'Unknown error')}")

        elif status == 'passed':
            # Show output preview
            output = test_result.get('actual_output', {})
            print(f"   Output Keys: {', '.join(output.keys())}")


def print_test_output(results: Dict[str, Any], test_id: str):
    """Print full output for a specific test."""
    for test_result in results['test_results']:
        if test_result['test_case']['test_id'] == test_id:
            print("\n" + "="*80)
            print(f"TEST OUTPUT: {test_id}")
            print("="*80)

            test_case = test_result['test_case']

            print("\nTest Case:")
            print(f"  Name: {test_case['test_name']}")
            print(f"  Description: {test_case['description']}")
            print(f"  Prompt: {test_case['input_prompt']}")

            print("\nInput Data:")
            print(json.dumps(test_case['input_data'], indent=2))

            print(f"\nStatus: {test_result['status']}")
            print(f"Execution Time: {test_result['execution_time_seconds']:.2f}s")

            if test_result.get('actual_output'):
                print("\nActual Output:")
                print(json.dumps(test_result['actual_output'], indent=2))

            if test_result.get('error_message'):
                print(f"\nError: {test_result['error_message']}")

            if test_result.get('validation_details'):
                print("\nValidation Details:")
                print(json.dumps(test_result['validation_details'], indent=2))

            return

    print(f"Test {test_id} not found")


def compare_results(results_path1: str, results_path2: str):
    """Compare two test result files."""
    results1 = load_test_results(results_path1)
    results2 = load_test_results(results_path2)

    print("\n" + "="*80)
    print(f"COMPARING RESULTS")
    print("="*80)
    print(f"File 1: {results_path1}")
    print(f"  Agent: {results1['agent_name']}")
    print(f"  Timestamp: {results1['timestamp']}")
    print(f"  Tests: {len(results1['test_results'])}")

    print(f"\nFile 2: {results_path2}")
    print(f"  Agent: {results2['agent_name']}")
    print(f"  Timestamp: {results2['timestamp']}")
    print(f"  Tests: {len(results2['test_results'])}")

    # Compare test outcomes
    test_map1 = {r['test_case']['test_id']: r for r in results1['test_results']}
    test_map2 = {r['test_case']['test_id']: r for r in results2['test_results']}

    common_tests = set(test_map1.keys()) & set(test_map2.keys())

    print(f"\nCommon Tests: {len(common_tests)}")

    improvements = []
    regressions = []

    for test_id in common_tests:
        r1 = test_map1[test_id]
        r2 = test_map2[test_id]

        if r1['status'] != 'passed' and r2['status'] == 'passed':
            improvements.append((test_id, r1['status'], r2['status']))
        elif r1['status'] == 'passed' and r2['status'] != 'passed':
            regressions.append((test_id, r1['status'], r2['status']))

    if improvements:
        print(f"\n✓ Improvements: {len(improvements)}")
        for test_id, old, new in improvements:
            print(f"  {test_id}: {old} → {new}")

    if regressions:
        print(f"\n✗ Regressions: {len(regressions)}")
        for test_id, old, new in regressions:
            print(f"  {test_id}: {old} → {new}")

    if not improvements and not regressions:
        print("\nNo changes in test outcomes")


def list_result_files():
    """List all available result files."""
    results_dir = Path("tests/agent_tests/results")

    if not results_dir.exists():
        print("No results directory found")
        return

    result_files = list(results_dir.glob("*.json"))

    if not result_files:
        print("No result files found")
        return

    print("\n" + "="*80)
    print("AVAILABLE RESULT FILES")
    print("="*80)

    for i, filepath in enumerate(result_files, 1):
        try:
            with open(filepath) as f:
                data = json.load(f)

            agent_name = data.get('agent_name', 'Unknown')
            timestamp = data.get('timestamp', 'Unknown')
            num_tests = len(data.get('test_results', []))

            print(f"\n{i}. {filepath.name}")
            print(f"   Agent: {agent_name}")
            print(f"   Timestamp: {timestamp}")
            print(f"   Tests: {num_tests}")
        except:
            print(f"\n{i}. {filepath.name}")
            print(f"   (Could not read file)")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="View agent test results")
    parser.add_argument("results_file", nargs='?', help="Path to results JSON file")
    parser.add_argument("--detailed", action="store_true", help="Show detailed results")
    parser.add_argument("--test-id", help="Show output for specific test ID")
    parser.add_argument("--compare", help="Compare with another results file")
    parser.add_argument("--list", action="store_true", help="List available result files")

    args = parser.parse_args()

    if args.list:
        list_result_files()
        return

    if not args.results_file:
        print("Error: results_file required (or use --list)")
        parser.print_help()
        return

    # Load results
    try:
        results = load_test_results(args.results_file)
    except FileNotFoundError:
        print(f"Error: File not found: {args.results_file}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {args.results_file}")
        return

    # Display results
    if args.test_id:
        print_test_output(results, args.test_id)
    elif args.compare:
        compare_results(args.results_file, args.compare)
    elif args.detailed:
        print_summary(results)
        print_detailed_results(results)
    else:
        print_summary(results)


if __name__ == "__main__":
    main()
