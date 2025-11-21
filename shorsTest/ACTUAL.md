# Shor's Algorithm Explained - What Each Number Means

## Overview
Shor's algorithm finds the prime factors of a number N using quantum computing.
For example: 15 = 3 × 5

## The Key Parameters

### 1. **N** (The number to factor)
- **What it is**: The composite number you want to break into prime factors
- **Example**: N = 15
- **Why it matters**: This is what you're trying to factor
- **Limitation**: Our implementation only works for N=15 because we've hardcoded the modular multiplication circuits for this specific case
- **Scaling**: Larger N requires more qubits and more complex circuits

### 2. **a** (The base)
- **What it is**: A random number between 2 and N-1 that's coprime to N (gcd(a,N)=1)
- **Valid values for N=15**: 2, 4, 7, 8, 11, 13
- **Why it matters**: We use 'a' to create a periodic function f(x) = a^x mod N
- **Example with a=7, N=15**:
  