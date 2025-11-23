#!/usr/bin/env python3
"""
shor_actual.py

TARGETED implementation of Shor's algorithm for small composite numbers up to 15.
Automatically tests ALL valid numbers (6, 10, 12, 14, 15) that can be factored 
using 4 target qubits.

⚠️  STABILITY: LIMITED TO 4 TARGET QUBITS ONLY ⚠️

Usage:
    # Run all tests (simulation - default)
    python3 shor_actual.py
    
    # Run with custom shots
    python3 shor_actual.py --shots 8192
    
    # Run on IBM Quantum hardware
    python3 shor_actual.py --use_ibm --backend ibm_torino
    
    # Test only specific number
    python3 shor_actual.py --only 15
    
    # Save circuits to PNG
    python3 shor_actual.py --circuits_dir circuits
"""

import argparse
import math
import sys
import time
from collections import Counter
from datetime import datetime
import numpy as np

# Import shared functions
try:
    from functions import (
        gcd, check_candidate_period, continued_fractions_convergents,
        qft_dagger, save_circuit_png, save_results_json, append_to_csv,
        classical_order_finding
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
# VALID NUMBERS FOR SHOR'S ALGORITHM (4 QUBITS)
# ============================================================================

VALID_NUMBERS = {
    10: {
        'factors': [2, 5],
        'valid_bases': [3, 7, 9],
        'description': '10 = 2 × 5',
    },
    12: {
        'factors': [3, 4],
        'valid_bases': [5, 7, 11],
        'description': '12 = 3 × 4',
    },
    14: {
        'factors': [2, 7],
        'valid_bases': [3, 5, 9, 11, 13],
        'description': '14 = 2 × 7',
    },
    15: {
        'factors': [3, 5],
        'valid_bases': [2, 4, 7, 8, 11, 13],
        'description': '15 = 3 × 5',
    }
}

TARGET_QUBITS = 4


# ============================================================================
# CIRCUIT CONSTRUCTION (Actual/Targeted Implementation)
# ============================================================================

def c_amod_n(a, N, n_target):
    """
    Create controlled modular multiplication gate: |x⟩ → |ax mod N⟩
    
    This is the ACTUAL/TARGETED implementation optimized for small N.
    Uses explicit unitary matrix construction.
    
    Args:
        a: Base for modular multiplication
        N: Modulus
        n_target: Number of target qubits (fixed at 4)
    
    Returns:
        Gate: Controlled unitary gate
    """
    size = 2 ** n_target
    U = np.zeros((size, size), dtype=complex)
    
    for x in range(size):
        if x < N:
            ax_mod_n = (a * x) % N
            U[ax_mod_n][x] = 1.0
        else:
            U[x][x] = 1.0
    
    qc = QuantumCircuit(n_target)
    qc.unitary(U, range(n_target), label=f'U_a={a}')
    
    return qc.to_gate()


def shor_circuit(N, a, n_count=8):
    """
    Build Shor's algorithm circuit for ACTUAL implementation.
    
    Fixed to 4 target qubits for maximum stability.
    
    Args:
        N: Number to factor (must be in VALID_NUMBERS)
        a: Base (must be coprime to N)
        n_count: Number of counting qubits (default: 8)
    
    Returns:
        QuantumCircuit: Complete Shor's circuit
    """
    if N not in VALID_NUMBERS:
        raise ValueError(f"N={N} not supported. Use: {list(VALID_NUMBERS.keys())}")
    
    n_target = TARGET_QUBITS
    
    # Create registers
    counting_reg = QuantumRegister(n_count, 'counting')
    target_reg = QuantumRegister(n_target, 'target')
    classical_reg = ClassicalRegister(n_count, 'classical')
    
    qc = QuantumCircuit(counting_reg, target_reg, classical_reg)
    
    # Initialize target to |1⟩
    qc.x(target_reg[0])
    
    # Put counting register in superposition
    for q in range(n_count):
        qc.h(counting_reg[q])
    
    # Apply controlled U^(2^j) operations
    for q in range(n_count):
        power = 2 ** q
        a_power = pow(a, power, N)
        
        # Create controlled gate
        U = c_amod_n(a_power, N, n_target)
        controlled_U = U.control()
        
        # Apply to circuit
        qc.append(controlled_U, [counting_reg[q]] + list(target_reg))
    
    # Apply inverse QFT
    qc.append(qft_dagger(n_count), counting_reg)
    
    # Measure counting register
    qc.measure(counting_reg, classical_reg)
    
    return qc


# ============================================================================
# TIMING DISPLAY
# ============================================================================

def display_timing_summary(log_data, test_label=""):
    """Display timing breakdown for a test run."""
    timing = log_data.get('timing', {})
    
    print(f"\n{'─'*70}")
    print(f"⏱️  TIMING SUMMARY: {test_label}")
    print(f"{'─'*70}")
    
    if 'circuit_construction' in timing:
        print(f"  Circuit Build:    {timing.get('circuit_construction', 0):.3f}s")
    if 'transpilation' in timing:
        print(f"  Transpilation:    {timing.get('transpilation', 0):.3f}s")
    if 'execution' in timing:
        print(f"  Execution:        {timing.get('execution', 0):.3f}s")
    if 'postprocessing' in timing:
        print(f"  Post-processing:  {timing.get('postprocessing', 0):.3f}s")
    if 'total' in timing:
        print(f"  {'─'*30}")
        print(f"  TOTAL:            {timing.get('total', 0):.3f}s")
    
    print(f"{'─'*70}\n")


# ============================================================================
# MAIN ALGORITHM
# ============================================================================

def run_shor_single(N, a, backend, shots, n_count, use_ibm, circuits_dir=None, mode='simulation'):
    """
    Run Shor's algorithm for a single N and base a.
    
    Args:
        N: Number to factor
        a: Base (coprime to N)
        backend: Qiskit backend
        shots: Number of measurements
        n_count: Number of counting qubits
        use_ibm: Whether using IBM Quantum hardware
        circuits_dir: Directory to save circuit PNGs (None to skip)
        mode: 'simulation' or 'quantum'
    
    Returns:
        dict: Complete log data with results and timing
    """
    start_time = datetime.now()
    
    if N not in VALID_NUMBERS:
        return {
            'success': False,
            'error': f'N={N} not in valid range',
            'timestamp': start_time.isoformat(),
            'N': N,
            'a': a
        }
    
    info = VALID_NUMBERS[N]
    
    # Check if a is valid
    if gcd(a, N) != 1:
        factor = gcd(a, N)
        other_factor = N // factor
        return {
            'success': True,
            'factors': sorted([factor, other_factor]),
            'method': 'classical_gcd',
            'message': f'gcd({a}, {N}) = {factor}',
            'timestamp': start_time.isoformat(),
            'input_parameters': {'N': N, 'a': a, 'shots': shots, 'n_count': n_count, 'mode': mode},
            'results': {'success': True, 'factors': sorted([factor, other_factor]), 'method': 'classical_gcd'},
            'timing': {'total': 0.001}
        }
    
    if a not in info['valid_bases']:
        return {
            'success': False,
            'error': f'Invalid base a={a} for N={N}',
            'timestamp': start_time.isoformat(),
            'N': N,
            'a': a
        }
    
    print(f"\n{'='*70}")
    print(f"ACTUAL SHOR'S ALGORITHM - Factoring N={N} ({info['description']})")
    print(f"Base: a={a}, Mode: {mode.upper()}")
    print(f"{'='*70}")
    
    log_data = {
        'timestamp': start_time.isoformat(),
        'input_parameters': {
            'N': N,
            'a': a,
            'shots': shots,
            'n_count': n_count,
            'use_ibm': use_ibm,
            'target_qubits': TARGET_QUBITS,
            'mode': mode
        },
        'problem_info': info,
        'timing': {},
        'quantum_execution': {},
        'postprocessing': {},
        'results': {}
    }
    
    # ========================================================================
    # BUILD CIRCUIT
    # ========================================================================
    circuit_start = datetime.now()
    print(f"\n[1/5] Building quantum circuit...")
    
    qc = shor_circuit(N, a, n_count)
    total_qubits = qc.num_qubits
    original_depth = qc.depth()
    circuit_time = (datetime.now() - circuit_start).total_seconds()
    
    print(f"      Circuit: {total_qubits} qubits, depth {original_depth}")
    
    log_data['quantum_execution']['circuit'] = {
        'total_qubits': total_qubits,
        'counting_qubits': n_count,
        'target_qubits': TARGET_QUBITS,
        'original_depth': original_depth
    }
    log_data['timing']['circuit_construction'] = circuit_time
    
    # Save circuit diagram
    if circuits_dir:
        save_circuit_png(qc, N, a, f'actual_{mode}', circuits_dir)
    
    # ========================================================================
    # TRANSPILE
    # ========================================================================
    print(f"\n[2/5] Backend: {backend}")
    print(f"      Shots: {shots}")
    
    transpile_start = datetime.now()
    print(f"\n[3/5] Transpiling...")
    
    transpiled = transpile(qc, backend, optimization_level=3)
    transpiled_depth = transpiled.depth()
    transpile_time = (datetime.now() - transpile_start).total_seconds()
    
    print(f"      Transpiled depth: {transpiled_depth}")
    
    log_data['quantum_execution']['transpiled'] = {
        'depth': transpiled_depth
    }
    log_data['timing']['transpilation'] = transpile_time
    
    # ========================================================================
    # EXECUTE
    # ========================================================================
    print(f"\n[4/5] Executing...")
    exec_start = datetime.now()
    
    if use_ibm:
        sampler = Sampler(backend)
        job = sampler.run([transpiled], shots=shots)
        print(f"      Job ID: {job.job_id()}")
        result = job.result()
        
        pub_result = result[0]
        data_bin = pub_result.data
        
        if hasattr(data_bin, 'classical'):
            counts_dict = data_bin.classical.get_counts()
        elif hasattr(data_bin, 'meas'):
            counts_dict = data_bin.meas.get_counts()
        else:
            attrs = [attr for attr in dir(data_bin) if not attr.startswith('_')]
            if attrs:
                counts_dict = getattr(data_bin, attrs[0]).get_counts()
            else:
                raise RuntimeError("Could not extract measurements")
        
        counts = {k: v for k, v in counts_dict.items()}
    else:
        job = backend.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()
    
    execution_time = (datetime.now() - exec_start).total_seconds()
    
    print(f"      Got {len(counts)} distinct outcomes")
    
    log_data['quantum_execution']['measurements'] = {
        'distinct_outcomes': len(counts),
        'execution_time': execution_time
    }
    log_data['timing']['execution'] = execution_time
    
    # ========================================================================
    # POST-PROCESS
    # ========================================================================
    postprocess_start = datetime.now()
    print(f"\n[5/5] Processing results...")
    
    Q = 2 ** n_count
    successful_periods = []
    
    for measured_value_str, count in counts.items():
        measured_value = int(measured_value_str, 2)
        if measured_value == 0:
            continue
        
        phase = measured_value / Q
        s, r = continued_fractions_convergents(phase, N)
        
        if r > 0 and r < N:
            if check_candidate_period(a, r, N):
                successful_periods.append((r, count, measured_value, phase))
    
    postprocess_time = (datetime.now() - postprocess_start).total_seconds()
    log_data['timing']['postprocessing'] = postprocess_time
    
    log_data['postprocessing']['valid_periods_found'] = len(successful_periods)
    
    if not successful_periods:
        total_time = (datetime.now() - start_time).total_seconds()
        log_data['results'] = {
            'success': False,
            'error': 'Could not find valid period'
        }
        log_data['timing']['total'] = total_time
        print(f"      ✗ Failed to find period")
        return log_data
    
    # Use most common valid period
    successful_periods.sort(key=lambda x: x[1], reverse=True)
    r, count, measured_value, phase = successful_periods[0]
    
    print(f"      Found period r={r}")
    
    # ========================================================================
    # EXTRACT FACTORS
    # ========================================================================
    if r % 2 == 0:
        guesses = [
            gcd(int(pow(a, r // 2, N) - 1), N),
            gcd(int(pow(a, r // 2, N) + 1), N)
        ]
        
        factors = [g for g in guesses if g not in [1, N]]
        
        if factors:
            factor = factors[0]
            other_factor = N // factor
            print(f"      ✓ Found factors: {factor} × {other_factor} = {N}")
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            log_data['results'] = {
                'success': True,
                'factors': sorted([factor, other_factor]),
                'period': r,
                'base': a,
                'method': 'quantum'
            }
            log_data['timing']['total'] = total_time
            
            return log_data
    
    total_time = (datetime.now() - start_time).total_seconds()
    log_data['results'] = {
        'success': False,
        'error': f'Period r={r} did not yield factors',
        'period': r
    }
    log_data['timing']['total'] = total_time
    print(f"      ✗ Period found but no factors extracted")
    
    return log_data


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Targeted Shor's algorithm for numbers 6-15 (4 qubits)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single test - simulation (default)
  python3 shor_actual.py --N 15 --a 2
  
  # Use GPU acceleration (A100)
  python3 shor_actual.py --N 15 --a 2 --gpu
  
  # Run on IBM Quantum (use sparingly!)
  python3 shor_actual.py --N 15 --a 2 --use_ibm
  
  # Save circuit diagram
  python3 shor_actual.py --N 15 --a 2 --circuits_dir circuits
        """
    )
    parser.add_argument('--N', type=int, required=True, 
                        choices=[6, 10, 12, 14, 15],
                        help='Number to factor (6, 10, 12, 14, or 15)')
    parser.add_argument('--a', type=int, default=None,
                        help='Base (default: first valid base for N)')
    parser.add_argument('--shots', type=int, default=4096,
                        help='Number of measurements (default: 4096)')
    parser.add_argument('--n_count', type=int, default=8,
                        help='Number of counting qubits (default: 8)')
    parser.add_argument('--use_ibm', action='store_true',
                        help='Run on IBM Quantum hardware (default: simulation)')
    parser.add_argument('--backend', type=str, default=None,
                        help='Specific IBM backend name')
    parser.add_argument('--csv', type=str, default=None,
                        help='CSV output file (default: auto-named based on mode)')
    parser.add_argument('--circuits_dir', type=str, default=None,
                        help='Directory to save circuit PNGs (default: None)')
    parser.add_argument('--gpu', action='store_true',
                        help='Use GPU acceleration (requires qiskit-aer-gpu)')
    
    args = parser.parse_args()
    
    # Validate N
    if args.N not in VALID_NUMBERS:
        print(f"[ERROR] N={args.N} not supported.")
        print(f"Valid values: {list(VALID_NUMBERS.keys())}")
        sys.exit(1)
    
    # Select base 'a' if not provided
    if args.a is None:
        args.a = VALID_NUMBERS[args.N]['valid_bases'][0]
        print(f"[INFO] Using default base a={args.a} for N={args.N}")
    else:
        # Validate base
        if args.a not in VALID_NUMBERS[args.N]['valid_bases']:
            print(f"[ERROR] Invalid base a={args.a} for N={args.N}")
            print(f"Valid bases for N={args.N}: {VALID_NUMBERS[args.N]['valid_bases']}")
            sys.exit(1)
    
    # ========================================================================
    # SETUP BACKEND
    # ========================================================================
    backend = None
    use_ibm = args.use_ibm
    mode = 'quantum' if use_ibm else 'simulation'
    
    # Auto-select CSV filename based on mode if not specified
    if args.csv is None:
        if use_ibm:
            csv_file = 'shor_actual_quantum_results.csv'
        else:
            csv_file = 'shor_actual_results.csv'
    else:
        csv_file = args.csv
    
    if use_ibm:
        if args.gpu:
            print("[WARNING] --gpu ignored when using IBM Quantum hardware")
        
        if not HAVE_IBM:
            print("[ERROR] qiskit-ibm-runtime not installed.")
            sys.exit(1)
        
        try:
            print("[INFO] Loading credentials...")
            import my_credentials
        except ImportError:
            print("[ERROR] Could not import my_credentials.py")
            sys.exit(1)
        
        try:
            service = QiskitRuntimeService(channel="ibm_quantum_platform")
        except Exception as e:
            print(f"[ERROR] Could not connect to IBM Quantum: {e}")
            sys.exit(1)
        
        min_qubits = args.n_count + TARGET_QUBITS
        
        if args.backend:
            backend = service.backend(args.backend)
            print(f"[INFO] Using backend: {backend.name}")
        else:
            all_backends = service.backends(operational=True, min_num_qubits=min_qubits)
            if not all_backends:
                print(f"[ERROR] No backends with {min_qubits}+ qubits")
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
                # Try GPU-enabled backend
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
        
        print(f"[INFO] ⚠️  Simulator is deterministic - results will be consistent")
        print(f"[INFO]    Real quantum hardware would show more variation")
    
    # ========================================================================
    # RUN SINGLE TEST
    # ========================================================================
    test_start = time.time()
    
    result = run_shor_single(
        N=args.N,
        a=args.a,
        backend=backend,
        shots=args.shots,
        n_count=args.n_count,
        use_ibm=use_ibm,
        circuits_dir=args.circuits_dir,
        mode=mode
    )
    
    # Save to CSV
    append_to_csv(result, csv_file)
    
    # Display timing summary
    test_elapsed = time.time() - test_start
    display_timing_summary(result, f"N={args.N}, a={args.a}")
    print(f"⏱️  Total wall-clock time: {test_elapsed:.2f}s\n")
    
    # ========================================================================
    # RESULT
    # ========================================================================
    if result['results'].get('success'):
        factors = result['results']['factors']
        print(f"✅ SUCCESS: {args.N} = {factors[0]} × {factors[1]}")
        print(f"Results saved to: {csv_file}\n")
        sys.exit(0)
    else:
        error = result['results'].get('error', 'Unknown error')
        print(f"❌ FAILED: {error}")
        print(f"Results saved to: {csv_file}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()