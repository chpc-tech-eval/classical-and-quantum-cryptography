# Generic vs Specific Implementation - What's the Difference?

## TL;DR

| Feature | N=15 Implementation | Generic Implementation |
|---------|---------------------|------------------------|
| **Works for** | Only N=15 | ANY composite number |
| **Quantum gates** | Fully quantum (SWAP, X) | Semi-classical (uses unitary matrices) |
| **Can run on real QC?** | Yes (12 qubits) | Theoretically yes, practically limited |
| **Circuit depth** | ~150-200 | Grows with N |
| **Qubits needed** | 12 fixed | O(log N) |
| **Honest implementation?** | ✓ Pure quantum | ⚠️ Classical cheating in oracle |

## Why Can't We Just Make Everything Quantum?

### The Challenge: Modular Arithmetic

The hard part of Shor's algorithm is implementing:
