# Shor's Algorithm - Quantum Factorization

A quantum computing implementation of Shor's algorithm for factoring composite numbers, demonstrating the power of quantum computers over classical approaches.  
Here we show an implementation of Shor's algorithm using Qiskit.

Shor's algorithm is a quantum algorithm that can factor large numbers **exponentially faster** than the best known classical algorithms.  We have implemented a generic implementation for inputting a number to factor and a direct implementation that has set numbers for both Simulation and Actual Quantum Hardware.

---

## Quick Start

### 1. Create the Virtual Environment
```bash
python3 -m venv qvenv
```

### 2. Activate the Virtual Environment
```bash
source qvenv/bin/activate  # Note: fixed typo from 'qenv' to 'qvenv'
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install qiskit[all] qiskit-aer matplotlib pandas numpy qiskit-ibm-runtime
```

### 4. Run Shor's Algorithm

#### Simulation (Local)
```bash
python3 shors_simulation.py
```

#### On Actual Quantum Hardware (IBM)
```bash
python3 shors_actual.py
```

#### Batch Experiments
```bash
./batch_run.sh
```

---

# About our implementation

## What It Does

Takes a large composite number (like 15, 21, or even numbers with hundreds of digits) and finds its prime factors.

**Example:** 15 = 3 × 5

## Why It's Important

**Breaking Modern Encryption:**
- Most internet security (RSA encryption) relies on the computational difficulty of factoring large numbers
- Classical computers would take **millions of years** to factor a 2048-bit number
- A sufficiently powerful quantum computer could factor it in **hours or days**
- This makes Shor's algorithm one of the most important—and potentially dangerous—quantum algorithms ever discovered

### How It Works (High Level)

Shor's algorithm cleverly transforms the hard problem of factoring into a different problem that quantum computers excel at:

#### **Step 1: Classical Preprocessing**
Pick a random number `a` that shares no common factors with `N`

#### **Step 2: Quantum Period Finding**
Find the period `r` of the function: `f(x) = aˣ mod N`

This means finding the smallest `r` where `aʳ mod N = 1`

**Quantum Techniques Used:**
- **Superposition:** Create a quantum state representing all possible values simultaneously
- **Phase Kickback:** Encode period information into quantum phases
- **Quantum Fourier Transform (QFT):** Extract the period from those phases

#### **Step 3: Classical Postprocessing**
Once you have the period `r`, calculate the factors:
- If `r` is even, compute:
  - `gcd(aʳ/² - 1, N)`
  - `gcd(aʳ/² + 1, N)`
- These will likely be factors of `N`

---

## 📊 Performance Expectations

### Impact of Increasing Shots

The number of **shots** (measurement repetitions) significantly affects algorithm performance.

#### ✅ **What Improves:**

| Shots | Expected Success Rate | Description |
|-------|----------------------|-------------|
| 1024  | ~60-70% | Basic accuracy, some missed periods |
| 2048  | ~75-85% | Better period detection |
| 4096  | ~85-95% | High reliability |

**Benefits:**
- ✓ More measurements → more chances to observe the correct period
- ✓ Better statistical confidence in measurement outcomes
- ✓ Less susceptible to quantum noise and random fluctuations
- ✓ More reliable period identification

#### ⏱️ **Trade-offs:**
- ⚠️ **Execution time increases linearly** with shot count
  - 4096 shots ≈ 4× longer than 1024 shots
- ⚠️ **Diminishing returns** at very high shot counts

#### 🔄 **What Doesn't Change:**
- Number of qubits required
- Circuit depth/complexity
- Transpilation time (circuit is compiled once)
- The actual factors found (when successful)

### 💡 Recommended Shot Counts

| Environment | Recommended Shots | Reasoning |
|-------------|------------------|-----------|
| **Simulator** | 1024 - 2048 | Less noise, fewer shots needed |
| **Real QPU** | 4096 - 8192 | Compensates for hardware noise & decoherence |

---

## 📁 Project Structure

```
shorsTest/
├── shor_generic.py          # Main Shor's algorithm implementation
├── shors_simulation.py      # Simulation runner
├── shors_actual.py          # Real quantum hardware runner
├── batch_run.sh             # Automated batch experiments
├── analyze.py               # Results analysis and visualization
├── README.md                # This file
└── results_n/               # Generated results folders
    ├── shor_results.csv     # Raw experimental data
    ├── experiment_log.txt   # Execution logs
    ├── shor_report.txt      # Analysis summary
    └── plots/               # Visualizations
        ├── success_rate_by_n.png
        ├── timing_breakdown.png
        ├── qubits_vs_n.png
        ├── depth_vs_n.png
        ├── execution_time_vs_n.png
        └── shots_vs_success.png
```

---

## 🔬 Running Experiments

### Single Run
```bash
python3 shor_generic.py --N 15 --shots 2048
```

### Batch Analysis
```bash
./batch_run.sh
```

This will:
1. Create a unique `results_n/` directory
2. Run Shor's algorithm on multiple composite numbers (15, 21, 33, 35, 51, 55, 77, 91, 143)
3. Test with different shot counts (1024, 2048, 4096)
4. Generate comprehensive analysis and visualizations

### View Results
```bash
cd results_1/
cat shor_report.txt
ls plots/
```

---

## 📈 Analysis Tools

### Generate Custom Analysis
```bash
python3 analyze.py results_1/shor_results.csv --graphs all
python3 analyze.py results_1/shor_results.csv --graphs timing
python3 analyze.py results_1/shor_results.csv --graphs scaling
```

### Available Graph Types
- `all` - Generate all visualizations
- `timing` - Timing breakdown and execution time plots
- `scaling` - Qubit and circuit depth scaling
- `success` - Success rate analysis

---

## 🛠️ Troubleshooting

### Low Success Rates
- Try increasing shot count to 4096 or 8192
- Check that N is a valid composite number
- Review `experiment_log.txt` for errors

### Slow Execution
- Reduce shot count for faster (but less accurate) results
- Use smaller test numbers (15, 21, 33)
- Ensure you're using the Aer simulator, not real hardware

---