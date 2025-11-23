# shor_actual.py - Targeted Implementation

## Overview

`shor_actual.py` automatically factors **ALL valid composite numbers from 6 to 15 that can be represented with 4 qubits**.

### What Numbers Are Tested?

**Valid numbers (automatically tested):**
- **N=6** (2×3) - 1 base
- **N=10** (2×5) - 3 bases  
- **N=12** (3×4) - 3 bases
- **N=14** (2×7) - 5 bases
- **N=15** (3×5) - 6 bases

**Total: 18 test cases**

### Why Only These Numbers?

Numbers **NOT included** and why:

| Numbers | Reason | Method |
|---------|--------|--------|
| 1 | Not composite | N/A |
| 2, 3, 5, 7, 11, 13, 17, 19 | Prime numbers | Can't factor primes |
| 4, 8, 9, 16 | Powers of primes (2², 2³, 3², 2⁴) | Use classical method |
| 21 and above | Require 5+ qubits | **EXCEEDS STABILITY LIMIT** |

## ⚠️ 4-Qubit Stability Limit

This implementation is **STRICTLY LIMITED TO 4 TARGET QUBITS** for stability.

### Why 4 Qubits?

| Qubits | Range | Stability | Real Hardware Success |
|--------|-------|-----------|----------------------|
| **4** | 0-15 | ✓✓✓ **STABLE** | 70-90% |
| **5** | 0-31 | ⚠️ Less stable | 30-50% |
| **6+** | 0-63+ | ❌ **UNSTABLE** | <20% |

**Quantum noise sources:**
1. **Decoherence**: States decay in ~100 microseconds
2. **Gate errors**: 0.1-1% error per gate (accumulates!)
3. **Crosstalk**: Qubits interfere with neighbors
4. **Connectivity**: Extra SWAP gates needed = deeper circuits

With 4 qubits, we can represent 0-15, so **N≤15 only**.

## Key Features

1. ✅ **NO user input for N** - Automatically tests all valid numbers
2. ✅ **Runs on SIMULATION by default** - Only uses QPU if `--use_ibm` specified
3. ✅ **Tests smallest to largest** - 6, 10, 12, 14, 15
4. ✅ **Multiple bases per N** - Tests all coprime bases
5. ✅ **CSV output** - Compatible with analysis tools
6. ✅ **4 qubits only** - Maximum stability
7. ✅ **Shared functions** - Uses `functions.py` for DRY code
8. ✅ **Circuit export** - Save circuit diagrams as PNG
9. ✅ **Timing display** - Shows detailed timing after each test

## Usage

### Basic Usage (Simulation - Default)

```bash
# Run ALL tests (6, 10, 12, 14, 15) on local simulator
python3 shor_actual.py

# This runs 18 test cases automatically!
