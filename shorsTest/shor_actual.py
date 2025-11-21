#!/usr/bin/env python3
"""
shor_actual.py

Actual implementation of Shor's algorithm for factoring N=15.
This implementation works with modern Qiskit (1.0+) and qiskit-aer.

Usage:
    # Run locally (simulation)
    python3 shor_actual.py --N 15 --a 7
    python3 shor_actual.py --N 15 --a 7 --shots 1024
    
    # Run on IBM Quantum
    python3 shor_actual.py --N 15 --a 7 --use_ibm --token <TOKEN>

    # Specify IBM backend
    python3 shor_actual.py --N 15 --a 7 --use_ibm --token <TOKEN> --backend <SPECIFIED_BACKEND>
"""

import argparse
import math
import sys
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

# Try to import IBM Quantum runtime
try:
    from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Session
    from qiskit_ibm_runtime import Options
    HAVE_IBM = True
except ImportError:
    HAVE_IBM = False

def gcd(a, b):
    """Compute greatest common divisor using Euclid's algorithm."""
    while b:
        a, b = b, a % b
    return a

def check_candidate_period(a, r, N):
    """Verify that r is a valid period for a mod N."""
    return pow(a, r, N) == 1

def continued_fractions_convergents(phi, Q):
    """
    Find the best rational approximation s/r to phi where r < Q
    using continued fractions.
    
    This is the classical post-processing step that extracts the period
    from the phase measured by the quantum circuit.
    """
    if phi == 0:
        return (0, 1)
    
    # Generate continued fraction convergents
    a = [int(phi)]
    remainders = [phi - a[0]]
    convergents = [(a[0], 1)]
    
    for i in range(1, 20):  # Limit iterations
        if abs(remainders[i-1]) < 1e-10:
            break
        
        next_a = int(1 / remainders[i-1])
        a.append(next_a)
        remainders.append(1 / remainders[i-1] - next_a)
        
        # Calculate convergent p/q
        if i == 1:
            p = a[1] * a[0] + 1
            q = a[1]
        else:
            p = a[i] * convergents[i-1][0] + convergents[i-2][0]
            q = a[i] * convergents[i-1][1] + convergents[i-2][1]
        
        convergents.append((p, q))
        
        if q >= Q:
            break
    
    # Return the convergent with largest denominator < Q
    for p, q in reversed(convergents):
        if q < Q and q > 0:
            return (p, q)
    
    return (0, 1)


def qft_dagger(n):
    """
    Create inverse Quantum Fourier Transform circuit for n qubits.
    
    The QFT is crucial for period finding - it converts the periodic
    pattern in the quantum state into measurable phase information.
    
    Args:
        n: Number of qubits
    
    Returns:
        QuantumCircuit implementing QFT†
    """
    qc = QuantumCircuit(n)
    
    # Reverse order of qubits for the QFT
    for qubit in range(n // 2):
        qc.swap(qubit, n - qubit - 1)
    
    for j in range(n):
        for m in range(j):
            qc.cp(-math.pi / float(2 ** (j - m)), m, j)
        qc.h(j)
    
    return qc


def c_amod15(a, power):
    """
    Controlled multiplication by a^power mod 15.
    
    This implements the unitary U where U|y> = |ay mod 15>
    The controlled version applies this transformation only when
    the control qubit is |1>.
    
    Args:
        a: Base number (must be coprime to 15)
        power: How many times to apply the multiplication
    
    Returns:
        Controlled gate that performs modular multiplication
    """
    if a not in [2, 4, 7, 8, 11, 13]:
        raise ValueError(f"'a' must be coprime to 15 and not 1. Got a={a}")
    
    U = QuantumCircuit(4)
    
    for _ in range(power):
        if a in [2, 13]:
            U.swap(0, 1)
            U.swap(1, 2)
            U.swap(2, 3)
        if a in [7, 8]:
            U.swap(2, 3)
            U.swap(1, 2)
            U.swap(0, 1)
        if a in [4, 11]:
            U.swap(1, 3)
            U.swap(0, 2)
        if a in [7, 11, 13]:
            for q in range(4):
                U.x(q)
    
    U = U.to_gate()
    U.name = f"{a}^{power} mod 15"
    c_U = U.control()
    return c_U


def shor_circuit(a, n_count=8):
    """
    Create the quantum circuit for Shor's algorithm to factor 15.
    
    Circuit structure:
    1. Initialize target register to |1>
    2. Create superposition in counting register (Hadamard on all qubits)
    3. Apply controlled modular exponentiation (the "quantum" part)
    4. Apply inverse QFT to extract phase information
    5. Measure to get the period
    
    Args:
        a: The base for modular exponentiation (must be coprime to 15)
        n_count: Number of counting qubits (more = better precision, but deeper circuit)
    
    Returns:
        QuantumCircuit ready to run
    """
    # Create quantum registers
    counting_qubits = QuantumRegister(n_count, 'counting')
    target_qubits = QuantumRegister(4, 'target')
    classical_bits = ClassicalRegister(n_count, 'classical')
    
    qc = QuantumCircuit(counting_qubits, target_qubits, classical_bits)
    
    # Initialize target register to |1>
    qc.x(target_qubits[0])
    
    # Put counting register in superposition
    for q in range(n_count):
        qc.h(counting_qubits[q])
    
    # Apply controlled-U operations
    # For each counting qubit j, apply U^(2^j)
    for q in range(n_count):
        power = 2 ** q
        qc.append(
            c_amod15(a, power),
            [counting_qubits[q]] + [target_qubits[i] for i in range(4)]
        )
    
    # Apply inverse QFT to counting register
    qc.append(qft_dagger(n_count), counting_qubits)
    
    # Measure counting register
    qc.measure(counting_qubits, classical_bits)
    
    return qc


def run_shor(N, a, backend=None, shots=1024, n_count=8, use_ibm=False):
    """
    Run Shor's algorithm to factor N using base a.
    
    PARAMETER EXPLANATIONS:
    
    N (int): The number you want to factor. This implementation only works for N=15.
             15 is the smallest non-trivial number that demonstrates Shor's algorithm.
             15 = 3 × 5
    
    a (int): The "base" for modular exponentiation. Must be coprime to N (gcd(a,N)=1).
             For N=15, valid choices are: 2, 4, 7, 8, 11, 13
             Different values of 'a' have different periods:
             - a=2: period r=4  (2^1=2, 2^2=4, 2^3=8, 2^4=16≡1 mod 15)
             - a=7: period r=4  (7^1=7, 7^2=4, 7^3=13, 7^4=1 mod 15)
             - a=11: period r=2 (11^1=11, 11^2=121≡1 mod 15)
             - a=13: period r=4 (13^1=13, 13^2=4, 13^3=7, 13^4=1 mod 15)
    
    shots (int): How many times to run the quantum circuit and measure.
                 More shots = more statistics = higher chance of success.
                 Typical values: 1024-8192
                 For IBM hardware, you might want 4096+ shots due to noise.
    
    n_count (int): Number of "counting qubits" (precision qubits).
                   More qubits = better precision in finding the period.
                   Rule of thumb: n_count ≥ 2*log2(N)
                   For N=15: need at least 8 qubits (2*log2(15) ≈ 7.7)
                   Tradeoff: More qubits = deeper circuit = more errors on real hardware
    
    backend: Where to run the circuit (Aer simulator or IBM quantum computer)
    
    use_ibm (bool): Whether running on IBM hardware (affects how results are processed)
    
    Returns:
        Dictionary with results including factors if successful
    """
    if N != 15:
        return {
            'success': False,
            'error': 'This implementation only works for N=15'
        }
    
    # Check if a is valid
    if gcd(a, N) != 1:
        factor = gcd(a, N)
        return {
            'success': True,
            'factors': [factor, N // factor],
            'method': 'classical_gcd',
            'message': f'gcd({a}, {N}) = {factor} is a non-trivial factor!'
        }
    
    if a not in [2, 4, 7, 8, 11, 13]:
        return {
            'success': False,
            'error': f'For N=15, a must be in [2, 4, 7, 8, 11, 13]. Got a={a}'
        }
    
    print(f"\n{'='*60}")
    print(f"Running Shor's algorithm to factor N={N} with a={a}")
    print(f"{'='*60}\n")
    
    # Create the circuit
    print(f"[1/4] Building quantum circuit with {n_count} counting qubits...")
    qc = shor_circuit(a, n_count)
    print(f"      Circuit has {qc.num_qubits} qubits and depth {qc.depth()}")
    
    if backend is None:
        backend = Aer.get_backend('aer_simulator')
    
    print(f"\n[2/4] Running on backend: {backend}")
    print(f"      Shots: {shots}")
    
    transpiled = transpile(qc, backend, optimization_level=3)
    print(f"      Transpiled circuit depth: {transpiled.depth()}")
    
    job = backend.run(transpiled, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    print(f"      Got {len(counts)} distinct measurement outcomes")
    
    # Process the measurement results
    print(f"\n[3/4] Processing measurement results...")
    print(f"      Top 5 measurements:")
    for measured_value, count in Counter(counts).most_common(5):
        print(f"        {measured_value}: {count} times ({100*count/shots:.1f}%)")
    
    # Try to find the period from measurements
    print(f"\n[4/4] Extracting period using continued fractions...")
    Q = 2 ** n_count
    
    successful_periods = []
    
    for measured_value_str, count in counts.items():
        measured_value = int(measured_value_str, 2)
        if measured_value == 0:
            continue
        
        # Phase estimation: measured value / 2^n_count ≈ s/r
        phase = measured_value / Q
        
        # Use continued fractions to find best rational approximation
        s, r = continued_fractions_convergents(phase, N)
        
        if r > 0 and r < N:
            # Verify this is a valid period
            if check_candidate_period(a, r, N):
                successful_periods.append((r, count, measured_value, phase))
    
    if not successful_periods:
        return {
            'success': False,
            'error': 'Could not find valid period from measurements',
            'counts': counts
        }
    
    # Use the most common valid period
    successful_periods.sort(key=lambda x: x[1], reverse=True)
    r, count, measured_value, phase = successful_periods[0]
    
    print(f"\n      Found period r={r} (measured {measured_value}, phase={phase:.4f})")
    print(f"      Verification: {a}^{r} mod {N} = {pow(a, r, N)}")
    
    # Extract factors from period
    if r % 2 == 0:
        guesses = [
            gcd(int(a ** (r // 2) - 1), N),
            gcd(int(a ** (r // 2) + 1), N)
        ]
        
        factors = [g for g in guesses if g not in [1, N]]
        
        if factors:
            factor = factors[0]
            other_factor = N // factor
            print(f"\n{'='*60}")
            print(f"SUCCESS! Found factors: {factor} × {other_factor} = {N}")
            print(f"{'='*60}\n")
            return {
                'success': True,
                'factors': sorted([factor, other_factor]),
                'period': r,
                'base': a,
                'counts': counts
            }
    
    return {
        'success': False,
        'error': f'Period r={r} did not yield factors (r is odd or a^(r/2)=-1 mod N)',
        'period': r,
        'counts': counts
    }


def main():
    parser = argparse.ArgumentParser(
        description="Manual implementation of Shor's algorithm for N=15",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
PARAMETER GUIDE:
  --N:        Number to factor (must be 15 for this implementation)
  --a:        Base for modular exponentiation. Valid: 2, 4, 7, 8, 11, 13
              This is the number we raise to powers mod N to find periodicity.
  --shots:    Number of times to measure the quantum circuit.
              More shots = better statistics. Typical: 1024-8192
  --n_count:  Number of precision qubits (counting register).
              More qubits = better precision but deeper circuit.
              For N=15, use 8 (default) or more.
              
EXAMPLES:
  # Run locally with default settings:
  python3 shor_manual_ibm.py --N 15 --a 7
  
  # Run with more shots for better statistics:
  python3 shor_manual_ibm.py --N 15 --a 7 --shots 4096
  
  # Run on IBM Quantum (requires token):
  python3 shor_manual_ibm.py --N 15 --a 7 --use_ibm --token YOUR_TOKEN
  
  # Use specific IBM backend:
  python3 shor_manual_ibm.py --N 15 --a 7 --use_ibm --backend ibm_brisbane --shots 8192
"""
    )
    parser.add_argument('--N', type=int, default=15, help='Number to factor (must be 15)')
    parser.add_argument('--a', type=int, default=7, help='Base (must be in [2,4,7,8,11,13])')
    parser.add_argument('--shots', type=int, default=2048, help='Number of measurements')
    parser.add_argument('--n_count', type=int, default=8, help='Number of counting qubits')
    parser.add_argument('--use_ibm', action='store_true', help='Run on IBM Quantum backend')
    parser.add_argument('--token', type=str, help='IBM Quantum API token')
    parser.add_argument('--backend', type=str, default=None, help='Specific IBM backend name')
    
    args = parser.parse_args()
    
    backend = None
    use_ibm = args.use_ibm
    
    if use_ibm:
        if not HAVE_IBM:
            print("[ERROR] qiskit-ibm-runtime not installed.")
            print("Install with: pip install qiskit-ibm-runtime")
            sys.exit(1)
        
        # Setup IBM Quantum
        if args.token:
            QiskitRuntimeService.save_account(
                channel="ibm_quantum",
                token=args.token,
                overwrite=True
            )
            print("[INFO] Saved IBM Quantum token")
        
        try:
            service = QiskitRuntimeService(channel="ibm_quantum")
        except Exception as e:
            print(f"[ERROR] Could not connect to IBM Quantum: {e}")
            print("Make sure you've provided --token or saved your credentials")
            sys.exit(1)
        
        # Select backend
        if args.backend:
            backend = service.backend(args.backend)
        else:
            # Get least busy backend
            backends = service.backends(simulator=False, operational=True, min_num_qubits=12)
            if backends:
                backend = min(backends, key=lambda b: b.status().pending_jobs)
                print(f"[INFO] Auto-selected least busy backend: {backend.name}")
            else:
                print("[ERROR] No suitable IBM backends found")
                sys.exit(1)
        
        print(f"[INFO] Using IBM Quantum backend: {backend.name}")
        print(f"[INFO] Pending jobs: {backend.status().pending_jobs}")
        print(f"[WARNING] Running on real quantum hardware - expect noise/errors!")
    else:
        backend = Aer.get_backend('aer_simulator')
        print(f"[INFO] Using local Aer simulator")
    
    result = run_shor(
        args.N,
        args.a,
        backend=backend,
        shots=args.shots,
        n_count=args.n_count,
        use_ibm=use_ibm
    )
    
    if result['success']:
        print(f"\n✓ Factorization successful!")
        print(f"  {args.N} = {' × '.join(map(str, result['factors']))}")
    else:
        print(f"\n✗ Factorization failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()