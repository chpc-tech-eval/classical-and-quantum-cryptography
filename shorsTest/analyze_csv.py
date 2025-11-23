#!/usr/bin/env python3
"""
analyze_csv.py

Quick analysis of batch run CSV results.
"""

import sys
import csv
from collections import Counter

if len(sys.argv) < 2:
    print("Usage: python3 analyze_csv.py <csv_file>")
    sys.exit(1)

csv_file = sys.argv[1]

print("="*70)
print(f"CSV ANALYSIS: {csv_file}")
print("="*70)
print()

try:
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
except FileNotFoundError:
    print(f"[ERROR] File not found: {csv_file}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Could not read CSV: {e}")
    sys.exit(1)

if not rows:
    print("CSV file is empty or has no data rows.")
    sys.exit(0)

print(f"Total records: {len(rows)}")
print()

# Count successes/failures
successes = sum(1 for r in rows if r.get('success', '').lower() == 'true')
failures = len(rows) - successes

print("RESULTS:")
print(f"  ✅ Successes: {successes} ({successes/len(rows)*100:.1f}%)")
print(f"  ❌ Failures: {failures} ({failures/len(rows)*100:.1f}%)")
print()

# Break down by N
print("BY NUMBER (N):")
n_values = Counter(r.get('N') for r in rows)
for n in sorted(n_values.keys(), key=lambda x: int(x) if x.isdigit() else 0):
    n_rows = [r for r in rows if r.get('N') == n]
    n_success = sum(1 for r in n_rows if r.get('success', '').lower() == 'true')
    print(f"  N={n}: {n_success}/{len(n_rows)} succeeded ({n_success/len(n_rows)*100:.0f}%)")
print()

# Show failures
if failures > 0:
    print("FAILED TESTS:")
    for i, row in enumerate(rows, 1):
        if row.get('success', '').lower() != 'true':
            N = row.get('N', 'N/A')
            a = row.get('a', 'N/A')
            error = row.get('method', 'Unknown error')
            print(f"  {i}. N={N}, a={a}: {error}")
    print()

# Timing statistics
print("TIMING STATISTICS:")
try:
    total_times = [float(r.get('total_time', 0)) for r in rows if r.get('total_time')]
    if total_times:
        print(f"  Average: {sum(total_times)/len(total_times):.2f}s")
        print(f"  Min: {min(total_times):.2f}s")
        print(f"  Max: {max(total_times):.2f}s")
        print(f"  Total: {sum(total_times):.2f}s ({sum(total_times)/60:.1f} minutes)")
except:
    print("  (Could not parse timing data)")
print()

# Mode breakdown
print("BY MODE:")
modes = Counter(r.get('mode', 'unknown') for r in rows)
for mode, count in modes.most_common():
    mode_rows = [r for r in rows if r.get('mode') == mode]
    mode_success = sum(1 for r in mode_rows if r.get('success', '').lower() == 'true')
    print(f"  {mode}: {mode_success}/{count} succeeded")
print()

print("="*70)
