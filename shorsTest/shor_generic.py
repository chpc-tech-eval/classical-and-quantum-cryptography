#!/usr/bin/env python3
"""
shor_generic.py

GENERIC implementation of Shor's algorithm with comprehensive data logging.
Supports both simulation and IBM Quantum hardware execution.
Exports circuit diagrams as PNG files.

Usage:
  # Simulation mode
  python3 shor_generic.py --N 21 --shots 2048 --csv generic_sim.csv --circuits_dir circuits

  # IBM Quantum mode
  python3 shor_generic.py --N 15 --shots 4096 --csv generic_quantum.csv --circuits_dir circuits --use_ibm

  # With specific backend
  python3 shor_generic.py --N 21 --use_ibm --backend ibm_brisbane --shots 2048
"""

import argparse
import math
import sys
import random
import time
from datetime import datetime
from collections import Counter
import numpy as np

# Import shared functions
try:
    from functions import (
        gcd, is_prime, is_power, classical_order_finding,
        check_candidate_period, continued_fractions_convergents,
        qft_dagger, save_circuit_png, save_results_json, append_to_csv
    )
except ImportError as e:
    print(f"[ERROR] Could not import functions.py: {e}")
    print("Make sure functions.py is in the same directory.")
    sys.exit(1)

# Import Qiskit
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit_aer import Aer
    from qiskit import transpile
except ImportError as e:
    print(f"[ERROR] Missing required packages. Install with:")
    print(f"  pip install qiskit qiskit-aer matplotlib")
    sys.exit(1)

# Try to import IBM Quantum runtime
try:
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    HAVE_IBM = True
except ImportError:
    HAVE_IBM = False


# ============================================================================
# QUANTUM CIRCUIT CONSTRUCTION
# ============================================================================

def modular_exponentiation_gate(a, N, n_target):
    """
    Create a quantum gate that performs |x⟩ → |ax mod N⟩.
    
    Args:
        a: Base for modular exponentiation
        N: Modulus
        n_target: Number of target qubits
    
    Returns:
        Gate: Unitary gate implementing modular multiplication
    """
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
    """
    Create generic Shor's algorithm circuit for ANY N.
    
    Args:
        a: Base (coprime to N)
        N: Number to factor
        n_count: Number of counting qubits (auto-calculated if None)
    
    Returns:
        tuple: (QuantumCircuit, n_target, n_count)
    """
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


# ============================================================================
# MAIN ALGORITHM
# ============================================================================

def run_shor_generic_with_logging(N, a=None, shots=2048, n_count=None, 
                                   backend=None, circuits_dir=None, mode='simulation'):
    """
    Run Shor's algorithm with comprehensive logging.
    
    Args:
        N: Number to factor
        a: Base (random if None)
        shots: Number of measurements
        n_count: Number of counting qubits (auto if None)
        backend: Qiskit backend to use
        circuits_dir: Directory to save circuit PNGs (None to skip)
        mode: 'simulation' or 'quantum'
    
    Returns:
        dict: Complete log data with all metrics
    """
    start_time = time.time()
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'input_parameters': {
            'N': N,
            'a': a,
            'shots': shots,
            'n_count': n_count,
            'mode': mode
        },
        'preprocessing': {},
        'quantum_execution': {},
        'postprocessing': {},
        'results': {},
        'timing': {}
    }
    
    print(f"\n{'='*70}")
    print(f"GENERIC SHOR'S ALGORITHM - Factoring N = {N}")
    print(f"Mode: {mode.upper()}")
    print(f"{'='*70}\n")
    
    # ========================================================================
    # PREPROCESSING
    # ========================================================================
    preprocess_start = time.time()
    
    # Basic checks
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
    
    # Choose random 'a' coprime to N
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
    
    # ========================================================================
    # CIRCUIT CONSTRUCTION
    # ========================================================================
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
    
    # Save circuit diagram
    if circuits_dir:
        save_circuit_png(qc, N, a, f'generic_{mode}', circuits_dir)
    
    circuit_time = time.time() - circuit_start
    log_data['timing']['circuit_construction'] = circuit_time
    
    print(f"\n[CIRCUIT]")
    print(f"  Total qubits: {qc.num_qubits}")
    print(f"  Circuit depth: {qc.depth()}")
    print(f"  Construction time: {circuit_time:.2f}s")
    
    # ========================================================================
    # TRANSPILATION
    # ========================================================================
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
    
    # ========================================================================
    # EXECUTION
    # ========================================================================
    execution_start = time.time()
    
    if mode == 'quantum' and HAVE_IBM:
        # Use IBM Quantum Sampler
        sampler = Sampler(backend)
        job = sampler.run([transpiled], shots=shots)
        print(f"\n[EXECUTION]")
        print(f"  Job ID: {job.job_id()}")
        result = job.result()
        
        # Extract counts from result
        pub_result = result[0]
        data_bin = pub_result.data
        
        if hasattr(data_bin, 'classical'):
            counts = data_bin.classical.get_counts()
        elif hasattr(data_bin, 'meas'):
            counts = data_bin.meas.get_counts()
        else:
            attrs = [attr for attr in dir(data_bin) if not attr.startswith('_')]
            if attrs:
                counts = getattr(data_bin, attrs[0]).get_counts()
            else:
                raise RuntimeError("Could not extract measurements")
    else:
        # Use local simulator
        job = backend.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()
        print(f"\n[EXECUTION]")
    
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
    
    print(f"  Time: {execution_time:.2f}s")
    print(f"  Distinct outcomes: {len(counts)}")
    
    # ========================================================================
    # POST-PROCESSING
    # ========================================================================
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
    
    log_data['postprocessing']['period_candidates'] = all_candidates[:20]
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
    
    # ========================================================================
    # FACTOR EXTRACTION
    # ========================================================================
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
        print(f"✓ SUCCESS! {N} = {factor} × {other_factor}")
        print(f"Total time: {total_time:.2f}s")
        print(f"{'='*70}\n")
        
        return log_data
    
    log_data['results'] = {
        'success': False,
        'error': 'Period did not yield factors',
        'period': r
    }
    
    return log_data


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generic Shor's algorithm with comprehensive logging",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--N', type=int, required=True, 
                        help='Number to factor')
    parser.add_argument('--a', type=int, default=None, 
                        help='Base (default: random coprime to N)')
    parser.add_argument('--shots', type=int, default=2048, 
                        help='Number of measurements (default: 2048)')
    parser.add_argument('--n_count', type=int, default=None, 
                        help='Counting qubits (default: auto = 2*ceil(log2(N)))')
    parser.add_argument('--output', type=str, default=None, 
                        help='Output JSON file for detailed results')
    parser.add_argument('--csv', type=str, default=None, 
                        help='CSV file for results (default: auto-named based on mode)')
    parser.add_argument('--circuits_dir', type=str, default=None,
                        help='Directory to save circuit PNGs (default: None)')
    parser.add_argument('--max_attempts', type=int, default=5, 
                        help='Maximum attempts (default: 5)')
    parser.add_argument('--use_ibm', action='store_true',
                        help='Use IBM Quantum hardware')
    parser.add_argument('--backend', type=str, default=None,
                        help='Specific IBM backend name')
    parser.add_argument('--gpu', action='store_true',
                        help='Use GPU acceleration (requires qiskit-aer-gpu)')
    
    args = parser.parse_args()
    
    # ========================================================================
    # BACKEND SETUP
    # ========================================================================
    backend = None
    mode = 'quantum' if args.use_ibm else 'simulation'
    
    # Auto-select CSV filename based on mode if not specified
    if args.csv is None:
        if args.use_ibm:
            csv_file = 'shor_generic_quantum_results.csv'
        else:
            csv_file = 'shor_generic_results.csv'
    else:
        csv_file = args.csv
    
    if args.use_ibm:
        if args.gpu:
            print("[WARNING] --gpu ignored when using IBM Quantum hardware")
        
        if not HAVE_IBM:
            print("[ERROR] qiskit-ibm-runtime not installed.")
            print("Install with: pip install qiskit-ibm-runtime")
            sys.exit(1)
        
        try:
            print("[INFO] Loading IBM Quantum credentials...")
            import my_credentials
        except ImportError:
            print("[ERROR] Could not import my_credentials.py")
            print("Create my_credentials.py with your IBM Quantum token.")
            sys.exit(1)
        
        try:
            service = QiskitRuntimeService(channel="ibm_quantum_platform")
        except Exception as e:
            print(f"[ERROR] Could not connect to IBM Quantum: {e}")
            sys.exit(1)
        
        min_qubits = max(8, 2 * math.ceil(math.log2(args.N))) + math.ceil(math.log2(args.N))
        
        if args.backend:
            backend = service.backend(args.backend)
            print(f"[INFO] Using backend: {backend.name}")
        else:
            all_backends = service.backends(operational=True, min_num_qubits=min_qubits)
            if not all_backends:
                print(f"[ERROR] No available backends with {min_qubits}+ qubits")
                sys.exit(1)
            
            real_backends = [b for b in all_backends if not b.simulator]
            if real_backends:
                backend = min(real_backends, key=lambda b: b.status().pending_jobs)
                print(f"[INFO] Auto-selected: {backend.name}")
            else:
                backend = all_backends[0]
                print(f"[INFO] Using simulator: {backend.name}")
        
        print(f"[INFO] Backend qubits: {backend.num_qubits}")
        print(f"[INFO] Pending jobs: {backend.status().pending_jobs}")
    else:
        # Setup local simulator with optional GPU
        if args.gpu:
            try:
                backend = Aer.get_backend('aer_simulator')
                backend.set_options(device='GPU')
                print(f"[INFO] Using Aer simulator with GPU acceleration")
                print(f"[INFO] ⚡ GPU backend configured (CUDA/cuQuantum)")
            except Exception as e:
                print(f"[WARNING] GPU acceleration requested but not available: {e}")
                print(f"[INFO] Falling back to CPU simulator")
                backend = Aer.get_backend('aer_simulator')
        else:
            backend = Aer.get_backend('aer_simulator')
            print(f"[INFO] Using Aer simulator (CPU)")
    
    print(f"[INFO] Output CSV: {csv_file}")

    # ========================================================================
    # RUN ATTEMPTS
    # ========================================================================
    for attempt in range(args.max_attempts):
        if attempt > 0:
            print(f"\n{'='*70}")
            print(f"Attempt {attempt + 1}/{args.max_attempts}")
            print(f"{'='*70}")
        
        log_data = run_shor_generic_with_logging(
            N=args.N,
            a=args.a if attempt == 0 else None,
            shots=args.shots,
            n_count=args.n_count,
            backend=backend,
            circuits_dir=args.circuits_dir,
            mode=mode
        )
        
        # Save results
        if args.output:
            output_file = args.output if attempt == 0 else args.output.replace('.json', f'_attempt{attempt+1}.json')
            save_results_json(log_data, output_file)
        
        # Append to CSV
        append_to_csv(log_data, csv_file)
        
        if log_data['results'].get('success'):
            sys.exit(0)
    
    print(f"\n✗ Failed after {args.max_attempts} attempts")
    sys.exit(1)


if __name__ == '__main__':
    main()
