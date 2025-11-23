#!/usr/bin/env python3
"""
functions.py

Shared utility functions for Shor's algorithm implementations.
Contains common math, quantum, and I/O functions used by both
generic and actual implementations.

DO NOT include main algorithm logic here - only reusable utilities.
"""

import math
import os
import csv
import json
from datetime import datetime

try:
    from qiskit import QuantumCircuit
    from qiskit.visualization import circuit_drawer
except ImportError:
    pass  # Will be caught by main scripts


# ============================================================================
# MATHEMATICAL UTILITIES
# ============================================================================

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


# ============================================================================
# QUANTUM UTILITIES
# ============================================================================

def continued_fractions_convergents(phi, Q):
    """
    Find the best rational approximation s/r to phi where r < Q 
    using continued fractions expansion.
    
    Args:
        phi: Phase value (float between 0 and 1)
        Q: Maximum denominator (typically 2^n_count)
    
    Returns:
        tuple: (numerator, denominator) of best approximation
    """
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
    """
    Create inverse Quantum Fourier Transform circuit for n qubits.
    
    Args:
        n: Number of qubits
    
    Returns:
        QuantumCircuit: Inverse QFT circuit
    """
    qc = QuantumCircuit(n)
    
    # Swap qubits
    for qubit in range(n // 2):
        qc.swap(qubit, n - qubit - 1)
    
    # Apply controlled rotations and Hadamard gates
    for j in range(n):
        for m in range(j):
            qc.cp(-math.pi / float(2 ** (j - m)), m, j)
        qc.h(j)
    
    return qc


# ============================================================================
# CIRCUIT VISUALIZATION
# ============================================================================

def save_circuit_png(circuit, N, a, mode='sim', circuits_dir='circuits', timestamp=None):
    """
    Save quantum circuit diagram as PNG.
    
    Args:
        circuit: QuantumCircuit to visualize
        N: Number being factored
        a: Base used
        mode: String describing mode (e.g., 'generic_sim', 'actual_quantum')
        circuits_dir: Directory to save PNG files
        timestamp: Optional timestamp string (auto-generated if None)
    
    Returns:
        str: Path to saved file, or None if save failed
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        
        os.makedirs(circuits_dir, exist_ok=True)
        
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"circuit_N{N}_a{a}_{mode}_{timestamp}.png"
        filepath = os.path.join(circuits_dir, filename)
        
        # Draw circuit
        fig = circuit_drawer(
            circuit, 
            output='mpl', 
            style='iqp',
            fold=200,
            scale=0.7
        )
        
        if fig is not None:
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"[CIRCUIT] Saved to {filepath}")
            return filepath
        else:
            print(f"[WARNING] Circuit drawer returned None")
            return None
            
    except Exception as e:
        print(f"[WARNING] Could not save circuit: {e}")
        return None


# ============================================================================
# DATA I/O UTILITIES
# ============================================================================

def save_results_json(log_data, filename):
    """Save results to JSON file with pretty printing."""
    try:
        with open(filename, 'w') as f:
            json.dump(log_data, f, indent=2)
        print(f"[SAVED] Results saved to {filename}")
        return True
    except Exception as e:
        print(f"[ERROR] Could not save JSON: {e}")
        return False


def append_to_csv(log_data, filename, fieldnames=None):
    """
    Append results to CSV file.
    
    Args:
        log_data: Dictionary containing run data
        filename: Path to CSV file
        fieldnames: List of field names (auto-detected if None)
    """
    file_exists = os.path.isfile(filename)
    
    # Default fieldnames for Shor's algorithm
    if fieldnames is None:
        fieldnames = [
            'timestamp', 'N', 'a', 'shots', 'n_count',
            'success', 'factors', 'period', 'classical_period', 'matches_classical',
            'total_qubits', 'circuit_depth', 'transpiled_depth',
            'distinct_outcomes', 'valid_periods_found',
            'preprocessing_time', 'circuit_time', 'transpile_time',
            'execution_time', 'postprocess_time', 'total_time',
            'method', 'mode'
        ]
    
    with open(filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        # Extract data with safe defaults
        row = {
            'timestamp': log_data.get('timestamp', ''),
            'N': log_data.get('input_parameters', {}).get('N', 'N/A'),
            'a': log_data.get('input_parameters', {}).get('a', 'N/A'),
            'shots': log_data.get('input_parameters', {}).get('shots', 'N/A'),
            'n_count': log_data.get('input_parameters', {}).get('n_count', 'auto'),
            'success': log_data.get('results', {}).get('success', False),
            'factors': str(log_data.get('results', {}).get('factors', [])),
            'period': log_data.get('results', {}).get('period', 'N/A'),
            'classical_period': log_data.get('preprocessing', {}).get('classical_period', 'N/A'),
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
            'method': log_data.get('results', {}).get('method', 'quantum'),
            'mode': log_data.get('input_parameters', {}).get('mode', 'simulation')
        }
        
        writer.writerow(row)
    
    print(f"[SAVED] Results appended to {filename}")