#!/usr/bin/env python3
"""
Quick script to check available IBM Quantum backends
"""

from qiskit_ibm_runtime import QiskitRuntimeService

# Import credentials
import my_credentials

# Connect to service
service = QiskitRuntimeService(channel="ibm_quantum_platform")

print("=" * 70)
print("Available IBM Quantum Backends")
print("=" * 70)

# Get all available backends
backends = service.backends()

print(f"\nFound {len(backends)} backend(s):\n")

for backend in backends:
    status = backend.status()
    num_qubits = backend.num_qubits
    is_simulator = backend.simulator
    operational = status.operational
    pending = status.pending_jobs
    
    print(f"Backend: {backend.name}")
    print(f"  Qubits: {num_qubits}")
    print(f"  Simulator: {is_simulator}")
    print(f"  Operational: {operational}")
    print(f"  Pending jobs: {pending}")
    print()

print("=" * 70)
