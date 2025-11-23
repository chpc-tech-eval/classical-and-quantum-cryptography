#!/usr/bin/env python3
"""
list_backends.py

List all available IBM Quantum backends for your account.
Helps you choose the right backend for batch runs.
"""

import sys

try:
    from qiskit_ibm_runtime import QiskitRuntimeService
except ImportError:
    print("[ERROR] qiskit-ibm-runtime not installed.")
    print("Install with: pip install qiskit-ibm-runtime")
    sys.exit(1)

try:
    import my_credentials
except ImportError:
    print("[ERROR] Could not import my_credentials.py")
    print("Create my_credentials.py with your IBM Quantum credentials.")
    sys.exit(1)

print("="*70)
print("IBM QUANTUM BACKENDS - AVAILABLE FOR YOUR ACCOUNT")
print("="*70)
print()

try:
    service = QiskitRuntimeService(channel="ibm_quantum_platform")
except Exception as e:
    print(f"[ERROR] Could not connect to IBM Quantum: {e}")
    sys.exit(1)

# Get all backends
backends = service.backends()

if not backends:
    print("No backends found!")
    sys.exit(1)

print(f"Found {len(backends)} backends\n")

# Separate by type
real_backends = []
sim_backends = []

for backend in backends:
    if backend.simulator:
        sim_backends.append(backend)
    else:
        real_backends.append(backend)

# Display real quantum hardware
if real_backends:
    print("="*70)
    print("REAL QUANTUM HARDWARE")
    print("="*70)
    print()
    
    for backend in sorted(real_backends, key=lambda b: b.num_qubits, reverse=True):
        status = backend.status()
        operational = "✅" if status.operational else "❌"
        
        print(f"  {operational} {backend.name}")
        print(f"     Qubits: {backend.num_qubits}")
        print(f"     Pending jobs: {status.pending_jobs}")
        
        if hasattr(backend, 'version'):
            print(f"     Version: {backend.version}")
        
        print()

# Display simulators
if sim_backends:
    print("="*70)
    print("SIMULATORS")
    print("="*70)
    print()
    
    for backend in sim_backends:
        status = backend.status()
        operational = "✅" if status.operational else "❌"
        
        print(f"  {operational} {backend.name}")
        print(f"     Qubits: {backend.num_qubits}")
        print()

# Recommendations
print("="*70)
print("RECOMMENDATIONS FOR SHOR'S ALGORITHM")
print("="*70)
print()

# Find suitable backends for actual (12 qubits minimum)
actual_suitable = [b for b in real_backends if b.num_qubits >= 12 and b.status().operational]
if actual_suitable:
    print("For shor_actual.py (needs 12+ qubits):")
    for b in sorted(actual_suitable, key=lambda x: x.status().pending_jobs)[:3]:
        print(f"  ✓ {b.name} ({b.num_qubits} qubits, {b.status().pending_jobs} pending)")
    print()

# Find suitable backends for generic (20+ qubits better)
generic_suitable = [b for b in real_backends if b.num_qubits >= 20 and b.status().operational]
if generic_suitable:
    print("For shor_generic.py with larger N (needs 20+ qubits):")
    for b in sorted(generic_suitable, key=lambda x: x.status().pending_jobs)[:3]:
        print(f"  ✓ {b.name} ({b.num_qubits} qubits, {b.status().pending_jobs} pending)")
    print()

print("="*70)
print("USAGE EXAMPLES")
print("="*70)
print()
print("Single test:")
if actual_suitable:
    print(f"  python3 shor_actual.py --N 15 --a 2 --backend {actual_suitable[0].name}")
print()
print("Batch test:")
if actual_suitable:
    print(f"  ./batch_actual.sh --backend {actual_suitable[0].name}")
print()
print("="*70)
