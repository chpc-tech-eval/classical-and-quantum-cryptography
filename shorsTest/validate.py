#!/usr/bin/env python3
"""
validate_results.py

Validate that Shor's algorithm results match theoretical expectations.

Usage:
  python3 validate_results.py shor_results.csv
  python3 validate_results.py results_21.json
"""

import argparse
import json
import math
import pandas as pd
import numpy as np


def load_data(filename):
    """Load results from CSV or JSON."""
    if filename.endswith('.csv'):
        return pd.read_csv(filename), 'csv'
    elif filename.endswith('.json'):
        with open(filename) as f:
            return json.load(f), 'json'
    else:
        raise ValueError("File must be .csv or .json")


def check_qubit_scaling(df):
    """Check if qubit count matches theory: 3*ceil(log2(N))"""
    print(f"\n{'='*70}")
    print("QUBIT SCALING CHECK")
    print(f"{'='*70}\n")
    
    all_good = True
    for _, row in df.iterrows():
        N = row['N']
        actual_qubits = row['total_qubits']
        expected_qubits = 3 * math.ceil(math.log2(N))
        
        match = actual_qubits == expected_qubits
        symbol = "✓" if match else "✗"
        
        print(f"N={N:3d}: Expected {expected_qubits:2d} qubits, got {actual_qubits:2d} {symbol}")
        
        if not match:
            all_good = False
    
    if all_good:
        print(f"\n✓ All runs use correct number of qubits")
    else:
        print(f"\n✗ Some runs use incorrect number of qubits")
    
    return all_good


def check_period_accuracy(df):
    """Check if quantum period matches classical period."""
    print(f"\n{'='*70}")
    print("PERIOD ACCURACY CHECK")
    print(f"{'='*70}\n")
    
    successful = df[df['success'] == True]
    
    if len(successful) == 0:
        print("⚠ No successful runs to check")
        return None
    
    # Check if matches_classical column exists and is valid
    if 'matches_classical' in successful.columns:
        matches = successful['matches_classical'].apply(
            lambda x: x == True or x == 'True' or x == 'true'
        ).sum()
        total = len(successful)
        percentage = 100 * matches / total
        
        print(f"Successful runs: {total}")
        print(f"Quantum period matched classical: {matches}/{total} ({percentage:.1f}%)")
        
        if percentage == 100:
            print(f"\n✓ Perfect accuracy - quantum always finds correct period")
            return True
        elif percentage >= 90:
            print(f"\n⚠ Good accuracy but not perfect - check n_count")
            return True
        else:
            print(f"\n✗ Poor accuracy - quantum period often wrong")
            print("  → Increase n_count (counting qubits)")
            print("  → Increase shots")
            return False
    else:
        print("⚠ Cannot check - 'matches_classical' column not found")
        return None


def check_success_rate(df):
    """Check if success rate is reasonable (40-70%)."""
    print(f"\n{'='*70}")
    print("SUCCESS RATE CHECK")
    print(f"{'='*70}\n")
    
    # Filter out trivial cases (even numbers, gcd cases)
    quantum_runs = df[~df.get('method', 'quantum').isin(['trivial_even', 'classical_gcd', 'perfect_power'])]
    
    if len(quantum_runs) == 0:
        print("⚠ No quantum runs found (all were trivial cases)")
        return None
    
    success_rate = 100 * quantum_runs['success'].mean()
    total = len(quantum_runs)
    successful = quantum_runs['success'].sum()
    
    print(f"Quantum runs: {total}")
    print(f"Successful: {successful}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if 40 <= success_rate <= 80:
        print(f"\n✓ Success rate within expected range (40-80%)")
        return True
    elif 25 <= success_rate < 40:
        print(f"\n⚠ Success rate lower than expected")
        print("  → Try increasing shots")
        print("  → Try increasing n_count")
        return True
    elif success_rate < 25:
        print(f"\n✗ Success rate too low - likely implementation bug")
        return False
    elif success_rate > 90:
        print(f"\n⚠ Success rate unusually high")
        print("  → Might be lucky with base choices")
        print("  → Run more trials for better statistics")
        return True
    
    return True


def check_measurement_distribution(data_json):
    """Check if measurement distribution shows clear peaks."""
    print(f"\n{'='*70}")
    print("MEASUREMENT DISTRIBUTION CHECK")
    print(f"{'='*70}\n")
    
    if 'quantum_execution' not in data_json:
        print("⚠ No quantum execution data in JSON")
        return None
    
    top_measurements = data_json['quantum_execution'].get('top_measurements', [])
    
    if not top_measurements:
        print("⚠ No measurement data found")
        return None
    
    print(f"Top 5 measurements:")
    for i, m in enumerate(top_measurements[:5]):
        print(f"  {i+1}. {m['bitstring']:12s}: {m['count']:4d} times ({100*m['probability']:.1f}%)")
    
    # Check if top measurements dominate
    total_prob = sum(m['probability'] for m in top_measurements[:5])
    
    print(f"\nTop 5 measurements account for {100*total_prob:.1f}% of outcomes")
    
    # Theoretical: for period r, we expect r peaks each with probability ~1/r
    # So top 5 should account for significant portion if r ≤ 5
    period = data_json.get('postprocessing', {}).get('found_period', {}).get('period')
    
    if period:
        expected_peaks = period
        expected_prob_per_peak = 1.0 / period
        expected_top5_prob = min(5, period) / period
        
        print(f"\nExpected {expected_peaks} peaks (period r={period})")
        print(f"Each peak should have ~{100*expected_prob_per_peak:.1f}% probability")
        print(f"Top 5 should account for ~{100*expected_top5_prob:.1f}%")
        
        if total_prob >= expected_top5_prob * 0.8:  # Within 80% of expectation
            print(f"\n✓ Measurement distribution shows clear peaks")
            return True
        else:
            print(f"\n⚠ Measurements more spread out than expected")
            print("  → Might indicate noise or insufficient n_count")
            return True
    
    # If no period info, just check if distribution is not uniform
    if total_prob > 0.5:  # Top 5 have >50%
        print(f"\n✓ Clear peaks detected (non-uniform distribution)")
        return True
    else:
        print(f"\n✗ Distribution too uniform - no clear periodicity")
        print("  → Check modular exponentiation implementation")
        print("  → Check QFT implementation")
        return False


def check_timing_pattern(df):
    """Check if timing follows expected pattern."""
    print(f"\n{'='*70}")
    print("TIMING PATTERN CHECK")
    print(f"{'='*70}\n")
    
    successful = df[df['success'] == True]
    
    if len(successful) == 0:
        print("⚠ No successful runs to check")
        return None
    
    # Check that execution dominates
    avg_exec = successful['execution_time'].mean()
    avg_preproc = successful['preprocessing_time'].mean()
    avg_transpile = successful['transpile_time'].mean()
    avg_postproc = successful['postprocess_time'].mean()
    
    print("Average times:")
    print(f"  Preprocessing:  {avg_preproc:.3f}s")
    print(f"  Transpilation:  {avg_transpile:.3f}s")
    print(f"  Execution:      {avg_exec:.3f}s  ← Should dominate")
    print(f"  Postprocessing: {avg_postproc:.3f}s")
    
    if avg_exec > avg_preproc and avg_exec > avg_postproc:
        print(f"\n✓ Execution time dominates (as expected for simulation)")
        return True
    else:
        print(f"\n⚠ Unusual timing pattern")
        return None


def generate_validation_report(filename):
    """Generate full validation report."""
    print(f"\n{'='*70}")
    print(f"VALIDATION REPORT FOR: {filename}")
    print(f"{'='*70}")
    
    data, data_type = load_data(filename)
    
    results = {}
    
    if data_type == 'csv':
        results['qubit_scaling'] = check_qubit_scaling(data)
        results['period_accuracy'] = check_period_accuracy(data)
        results['success_rate'] = check_success_rate(data)
        results['timing_pattern'] = check_timing_pattern(data)
    
    elif data_type == 'json':
        results['measurement_distribution'] = check_measurement_distribution(data)
        
        # If JSON has full data, check more
        if 'results' in data:
            print(f"\nSingle run result:")
            print(f"  Success: {data['results'].get('success')}")
            if data['results'].get('success'):
                print(f"  Factors: {data['results'].get('factors')}")
                print(f"  Period: {data['results'].get('period')}")
    
    # Summary
    print(f"\n{'='*70}")
    print("VALIDATION SUMMARY")
    print(f"{'='*70}\n")
    
    passed = sum(1 for v in results.values() if v == True)
    failed = sum(1 for v in results.values() if v == False)
    unknown = sum(1 for v in results.values() if v is None)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}")
    print(f"Checks failed: {failed}/{total}")
    print(f"Checks skipped: {unknown}/{total}")
    
    if failed == 0 and passed > 0:
        print(f"\n✓✓✓ VALIDATION PASSED ✓✓✓")
        print("Your implementation matches theoretical expectations!")
    elif failed > 0:
        print(f"\n✗✗✗ VALIDATION FAILED ✗✗✗")
        print("Some checks did not pass. Review the messages above.")
    else:
        print(f"\n⚠⚠⚠ INSUFFICIENT DATA ⚠⚠⚠")
        print("Not enough data to validate. Run more experiments.")


def main():
    parser = argparse.ArgumentParser(description="Validate Shor's algorithm results")
    parser.add_argument('filename', help='CSV or JSON file with results')
    
    args = parser.parse_args()
    
    generate_validation_report(args.filename)


if __name__ == '__main__':
    main()
