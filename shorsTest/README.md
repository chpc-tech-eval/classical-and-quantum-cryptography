### Activate the virtual environment
```bash
source ~/qiskit-env/bin/activate
```

### Install Qiskit - if not installed
```bash
pip install --upgrade pip
pip install qiskit[all]
```

### Run Shor's algorithm
- Simulation
```bash
python3 shors_simulation.py
```
- Actual (for IBM)
```bash
python3 shors_actual.py
```

## About Shor's Algorithm implementation
Shor's algorithm is a quantum algorithm that can factor large numbers exponentially faster than the best known classical algorithms.
### What It Does  
Shor's algorithm takes a large composite number (like 15, 21, or even numbers with hundreds of digits) and finds its prime factors. For example, it can determine that 15 = 3 × 5.  
### Why It's Important
Breaking encryption:
- Most modern internet security (RSA encryption) relies on the fact that factoring large numbers is extremely hard for classical computers. A number with 2048 bits would take classical computers millions of years to factor, but a sufficiently powerful quantum computer running Shor's algorithm could do it in hours or days.
- This is why Shor's algorithm is considered one of the most important quantum algorithms ever discovered - it poses a genuine threat to current cryptographic systems.
### How It Works (High Level)
Shor's algorithm is clever because it transforms the hard problem of factoring into a different problem that quantum computers are good at:
- Classical preprocessing: Pick a random number a that shares no common factors with N
Quantum part - Period Finding: Find the period r of the function f(x) = a^x mod N. This means finding the smallest r where a^r mod N = 1. This is the hard part that classical computers struggle with, but quantum computers can do efficiently using:
  - Superposition: Create a quantum state representing all possible values at once
  - Phase kickback: Encode the period information into quantum phases
  - Quantum Fourier Transform: Extract the period from those phases


Classical postprocessing: Once you have the period r, use it to calculate factors:  
If r is even, compute gcd(a^(r/2) - 1, N) and gcd(a^(r/2) + 1, N)
These will likely be factors of N