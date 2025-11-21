#!/usr/bin/env python3
"""
shor_generic.py

GENERIC implementation of Shor's algorithm with comprehensive data logging.
Logs all important metrics to JSON for later analysis and graphing.

Usage:
  python3 shor_generic.py --N 21 --output results.json
  python3 shor_generic.py --N 35 --a 2 --shots 4096
"""

import argparse
import math
import sys
import random
import json
import time
from datetime import datetime
from fractions import Fraction
from collections import Counter

try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit_aer import Aer
    from qiskit import transpile
except ImportError as e:
    print(f"Error: Missing required packages. Install with:")
    print(f"  pip install qiskit qiskit-aer")
    sys.exit(1)

import numpy as np


def gcd(a, b):
    """Compute greatest common divisor using Euclid's algorithm."""
    while b:
        a, b = b, a % b
    return a


def is_prime(n):
    """Check if n is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def is_power(N):
    """Check if N is a perfect power (N = a^b for some a, b > 1)."""
    for b in range(2, int(math.log2(N)) + 1):
        a = int(round(N ** (1.0 / b)))
        if a ** b == N:
            return True, a, b
    return False, None, None


def classical_order_finding(a, N):
    """Classical order finding: find smallest r > 0 such that a^r mod N = 1."""
    if gcd(a, N) != 1:
        return None
    r = 1
    result = a % N
    while result != 1:
        result = (result * a) % N
        r += 1
        if r > N:
            return None
    return r


def check_candidate_period(a, r, N):
    """Verify that r is a valid period for a mod N."""
    return pow(a, r, N) == 1


def continued_fractions_convergents(phi, Q):
    """Find the best rational approximation s/r to phi where r < Q using continued fractions."""
    if phi == 0:
        return (0, 1)
    
    a_list = [int(phi)]
    remainders = [phi - a_list[0]]
    convergents = [(a_list[0], 1)]
    
    for i in range(1, 30):
        if abs(remainders[i-1]) < 1e-10:
            break
        
        next_a = int(1 / remainders[i-1])
        a_list.append(next_a)
        remainders.append(1 / remainders[i-1] - next_a)
        
        if i == 1:
            p = a_list[1] * a_list[0] + 1
            q = a_list[1]
        else:
            p = a_list[i] * convergents[i-1][0] + convergents[i-2][0]
            q = a_list[i] * convergents[i-1][1] + convergents[i-2][1]
        
        convergents.append((p, q))
        
        if q >= Q:
            break
    
    for p, q in reversed(convergents):
        if q < Q and q > 0:
            return (p, q)
    
    return (0, 1)


def qft_dagger(n):
    """Create inverse Quantum Fourier Transform circuit for n qubits."""
    qc = QuantumCircuit(n)
    
    for qubit in range(n // 2):
        qc.swap(qubit, n - qubit - 1)
    
    for j in range(n):
        for m in range(j):
            qc.cp(-math.pi / float(2 ** (j - m)), m, j)
        qc.h(j)
    
    return qc


def modular_exponentiation_gate(a, N, n_target):
    """Create a quantum gate that performs |x⟩ → |ax mod N⟩"""
    size = 2 ** n_target
    permutation = np.zeros((size, size), dtype=complex)
    
    for x in range(size):
        if x < N:
            new_x = (a * x) % N
            permutation[new_x][x] = 1.0
        else:
            permutation[x][x] = 1.0
    
    qc = QuantumCircuit(n_target)
    qc.unitary(permutation, range(n_target), label=f"U_{a}")
    
    return qc.to_gate()


def shor_circuit_generic(a, N, n_count=None):
    """Create generic Shor's algorithm circuit for ANY N."""
    n_target = math.ceil(math.log2(N))
    if n_count is None:
        n_count = max(8, 2 * n_target)
    
    counting_qubits = QuantumRegister(n_count, 'counting')
    target_qubits = QuantumRegister(n_target, 'target')
    classical_bits = ClassicalRegister(n_count, 'classical')
    
    qc = QuantumCircuit(counting_qubits, target_qubits, classical_bits)
    
    # Initialize target register to |1⟩
    qc.x(target_qubits[0])
    
    # Put counting register in superposition
    for q in range(n_count):
        qc.h(counting_qubits[q])
    
    # Apply controlled-U^(2^j) operations
    for q in range(n_count):
        power = 2 ** q
        a_power = pow(a, power, N)
        
        U = modular_exponentiation_gate(a_power, N, n_target)
        c_U = U.control()
        
        qc.append(c_U, [counting_qubits[q]] + [target_qubits[i] for i in range(n_target)])
    
    # Apply inverse QFT
    qc.append(qft_dagger(n_count), counting_qubits)
    
    # Measure
    qc.measure(counting_qubits, classical_bits)
    
    return qc, n_target, n_count


def run_shor_generic_with_logging(N, a=None, shots=2048, n_count=None, backend=None):
    """
    Run Shor's algorithm with comprehensive logging.
    
    Returns a dictionary with all metrics for analysis.
    """
    start_time = time.time()
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'input_parameters': {
            'N': N,
            'a': a,
            'shots': shots,
            'n_count': n_count
        },
        'preprocessing': {},
        'quantum_execution': {},
        'postprocessing': {},
        'results': {},
        'timing': {}
    }
    
    print(f"\n{'='*70}")
    print(f"GENERIC SHOR'S ALGORITHM - Factoring N = {N}")
    print(f"{'='*70}\n")
    
    # Preprocessing
    preprocess_start = time.time()
    
    if N < 4:
        log_data['results'] = {'success': False, 'error': f'N must be at least 4'}
        return log_data
    
    if N % 2 == 0:
        log_data['preprocessing']['method'] = 'trivial_even'
        log_data['results'] = {
            'success': True,
            'factors': [2, N // 2],
            'method': 'trivial_even'
        }
        return log_data
    
    if is_prime(N):
        log_data['results'] = {'success': False, 'error': f'{N} is prime'}
        return log_data
    
    is_pow, base, exp = is_power(N)
    if is_pow:
        log_data['preprocessing']['method'] = 'perfect_power'
        log_data['results'] = {
            'success': True,
            'factors': [base, base] if exp == 2 else [base, N // base],
            'method': 'perfect_power'
        }
        return log_data
    
    # Choose random 'a'
    if a is None:
        while True:
            a = random.randint(2, N - 1)
            if gcd(a, N) == 1:
                break
    
    log_data['input_parameters']['a'] = a
    
    g = gcd(a, N)
    if g != 1:
        log_data['preprocessing']['method'] = 'classical_gcd'
        log_data['results'] = {
            'success': True,
            'factors': [g, N // g],
            'method': 'classical_gcd'
        }
        return log_data
    
    # Classical order for reference
    classical_r = classical_order_finding(a, N)
    log_data['preprocessing']['classical_period'] = classical_r
    
    preprocess_time = time.time() - preprocess_start
    log_data['timing']['preprocessing'] = preprocess_time
    
    print(f"[SETUP]")
    print(f"  N = {N}, a = {a}")
    print(f"  Classical period: r = {classical_r}")
    
    # Build circuit
    circuit_start = time.time()
    
    if n_count is None:
        n_count = max(8, 2 * math.ceil(math.log2(N)))
    
    qc, n_target, n_count = shor_circuit_generic(a, N, n_count)
    
    log_data['quantum_execution']['circuit'] = {
        'n_counting_qubits': n_count,
        'n_target_qubits': n_target,
        'total_qubits': qc.num_qubits,
        'original_depth': qc.depth(),
        'gate_count': len(qc.data)
    }
    
    circuit_time = time.time() - circuit_start
    log_data['timing']['circuit_construction'] = circuit_time
    
    print(f"\n[CIRCUIT]")
    print(f"  Total qubits: {qc.num_qubits}")
    print(f"  Circuit depth: {qc.depth()}")
    print(f"  Construction time: {circuit_time:.2f}s")
    
    # Transpile and run
    if backend is None:
        backend = Aer.get_backend('aer_simulator')
    
    transpile_start = time.time()
    transpiled = transpile(qc, backend, optimization_level=3)
    transpile_time = time.time() - transpile_start
    
    log_data['quantum_execution']['transpiled'] = {
        'depth': transpiled.depth(),
        'gate_count': len(transpiled.data)
    }
    log_data['timing']['transpilation'] = transpile_time
    
    print(f"\n[TRANSPILATION]")
    print(f"  Transpiled depth: {transpiled.depth()}")
    print(f"  Time: {transpile_time:.2f}s")
    
    # Execute
    execution_start = time.time()
    job = backend.run(transpiled, shots=shots)
    result = job.result()
    counts = result.get_counts()
    execution_time = time.time() - execution_start
    
    log_data['timing']['execution'] = execution_time
    log_data['quantum_execution']['measurements'] = {
        'shots': shots,
        'distinct_outcomes': len(counts),
        'execution_time': execution_time
    }
    
    # Store top measurements
    top_measurements = []
    for measured_value, count in Counter(counts).most_common(10):
        top_measurements.append({
            'bitstring': measured_value,
            'decimal': int(measured_value, 2),
            'count': count,
            'probability': count / shots
        })
    log_data['quantum_execution']['top_measurements'] = top_measurements
    
    print(f"\n[EXECUTION]")
    print(f"  Time: {execution_time:.2f}s")
    print(f"  Distinct outcomes: {len(counts)}")
    
    # Post-processing
    postprocess_start = time.time()
    
    Q = 2 ** n_count
    successful_periods = []
    all_candidates = []
    
    for measured_value_str, count in counts.items():
        measured_value = int(measured_value_str, 2)
        if measured_value == 0:
            continue
        
        phase = measured_value / Q
        s, r = continued_fractions_convergents(phase, N)
        
        candidate = {
            'measured_value': measured_value,
            'phase': phase,
            'convergent_numerator': s,
            'convergent_denominator': r,
            'count': count,
            'valid_period': False
        }
        
        if r > 1 and r < N:
            if check_candidate_period(a, r, N):
                candidate['valid_period'] = True
                successful_periods.append((r, count, measured_value, phase))
        
        all_candidates.append(candidate)
    
    log_data['postprocessing']['period_candidates'] = all_candidates[:20]  # Top 20
    log_data['postprocessing']['valid_periods_found'] = len(successful_periods)
    
    postprocess_time = time.time() - postprocess_start
    log_data['timing']['postprocessing'] = postprocess_time
    
    if not successful_periods:
        log_data['results'] = {
            'success': False,
            'error': 'Could not find valid period from measurements'
        }
        return log_data
    
    # Use most common valid period
    successful_periods.sort(key=lambda x: x[1], reverse=True)
    r, count, measured_value, phase = successful_periods[0]
    
    log_data['postprocessing']['found_period'] = {
        'period': r,
        'measured_value': measured_value,
        'phase': phase,
        'count': count,
        'matches_classical': (r == classical_r)
    }
    
    print(f"\n[PERIOD FOUND]")
    print(f"  r = {r} (matches classical: {r == classical_r})")
    
    # Extract factors
    if r % 2 != 0:
        log_data['results'] = {
            'success': False,
            'error': 'Period is odd',
            'period': r
        }
        return log_data
    
    x = pow(a, r // 2, N)
    
    if x == N - 1:
        log_data['results'] = {
            'success': False,
            'error': 'a^(r/2) ≡ -1 (mod N)',
            'period': r
        }
        return log_data
    
    guesses = [gcd(x - 1, N), gcd(x + 1, N)]
    factors = [g for g in guesses if g not in [1, N]]
    
    if factors:
        factor = factors[0]
        other_factor = N // factor
        
        total_time = time.time() - start_time
        log_data['timing']['total'] = total_time
        
        log_data['results'] = {
            'success': True,
            'factors': sorted([factor, other_factor]),
            'period': r,
            'base': a,
            'N': N,
            'verification': {
                'product': factor * other_factor,
                'matches_N': (factor * other_factor == N)
            }
        }
        
        print(f"\n{'='*70}")
        print(f"SUCCESS! {N} = {factor} × {other_factor}")
        print(f"Total time: {total_time:.2f}s")
        print(f"{'='*70}\n")
        
        return log_data
    
    log_data['results'] = {
        'success': False,
        'error': 'Period did not yield factors',
        'period': r
    }
    
    return log_data


def save_results(log_data, filename):
    """Save results to JSON file."""
    with open(filename, 'w') as f:
        json.dump(log_data, f, indent=2)
    print(f"\n[SAVED] Results written to {filename}")


def append_to_csv(log_data, filename):
    """Append results to CSV for easy graphing."""
    import csv
    import os
    
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as f:
        fieldnames = [
            'timestamp', 'N', 'a', 'shots', 'n_count',
            'success', 'factors', 'period', 'classical_period', 'matches_classical',
            'total_qubits', 'circuit_depth', 'transpiled_depth',
            'distinct_outcomes', 'valid_periods_found',
            'preprocessing_time', 'circuit_time', 'transpile_time',
            'execution_time', 'postprocess_time', 'total_time',
            'method'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        row = {
            'timestamp': log_data['timestamp'],
            'N': log_data['input_parameters']['N'],
            'a': log_data['input_parameters'].get('a', 'N/A'),
            'shots': log_data['input_parameters']['shots'],
            'n_count': log_data['input_parameters'].get('n_count', 'auto'),
            'success': log_data['results'].get('success', False),
            'factors': str(log_data['results'].get('factors', [])),
            'period': log_data['results'].get('period', 'N/A'),
            'classical_period': log_data['preprocessing'].get('classical_period', 'N/A'),
            'matches_classical': log_data.get('postprocessing', {}).get('found_period', {}).get('matches_classical', 'N/A'),
            'total_qubits': log_data.get('quantum_execution', {}).get('circuit', {}).get('total_qubits', 'N/A'),
            'circuit_depth': log_data.get('quantum_execution', {}).get('circuit', {}).get('original_depth', 'N/A'),
            'transpiled_depth': log_data.get('quantum_execution', {}).get('transpiled', {}).get('depth', 'N/A'),
            'distinct_outcomes': log_data.get('quantum_execution', {}).get('measurements', {}).get('distinct_outcomes', 'N/A'),
            'valid_periods_found': log_data.get('postprocessing', {}).get('valid_periods_found', 'N/A'),
            'preprocessing_time': log_data.get('timing', {}).get('preprocessing', 0),
            'circuit_time': log_data.get('timing', {}).get('circuit_construction', 0),
            'transpile_time': log_data.get('timing', {}).get('transpilation', 0),
            'execution_time': log_data.get('timing', {}).get('execution', 0),
            'postprocess_time': log_data.get('timing', {}).get('postprocessing', 0),
            'total_time': log_data.get('timing', {}).get('total', 0),
            'method': log_data['results'].get('method', 'quantum')
        }
        
        writer.writerow(row)
    
    print(f"[SAVED] Results appended to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Generic Shor's algorithm with comprehensive logging"
    )
    
    parser.add_argument('--N', type=int, required=True, help='Number to factor')
    parser.add_argument('--a', type=int, default=None, help='Base (default: random)')
    parser.add_argument('--shots', type=int, default=2048, help='Number of measurements')
    parser.add_argument('--n_count', type=int, default=None, help='Counting qubits (default: auto)')
    parser.add_argument('--output', type=str, default=None, help='Output JSON file')
    parser.add_argument('--csv', type=str, default='shor_results.csv', help='CSV file for results')
    parser.add_argument('--max_attempts', type=int, default=5, help='Max attempts')
    
    args = parser.parse_args()
    
    # Try multiple attempts
    for attempt in range(args.max_attempts):
        if attempt > 0:
            print(f"\n{'='*70}")
            print(f"Attempt {attempt + 1}/{args.max_attempts}")
            print(f"{'='*70}")
        
        log_data = run_shor_generic_with_logging(
            args.N,
            a=args.a if attempt == 0 else None,
            shots=args.shots,
            n_count=args.n_count
        )
        
        # Save results
        if args.output:
            output_file = args.output if attempt == 0 else args.output.replace('.json', f'_attempt{attempt+1}.json')
            save_results(log_data, output_file)
        
        # Append to CSV
        append_to_csv(log_data, args.csv)
        
        if log_data['results'].get('success'):
            sys.exit(0)
    
    print(f"\n✗ Failed after {args.max_attempts} attempts")
    sys.exit(1)


if __name__ == '__main__':
    main()
