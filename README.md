# Classical and Quantum Cryptography

---

## Overview

This project provides a comprehensive comparison of **classical** and **quantum** approaches to cryptographic problems, specifically:

- **Classical Approach**: Recurrent Neural Networks (RNNs) for password generation and hash cracking
- **Quantum Approach**: Shor's Algorithm and QAOA (Quantum Approximate Optimization Algorithm) implementations

### Research Goals

1. **Performance Comparison**: Benchmark RNN training and inference on an AMD EPYC CPU and NVIDIA A100 GPU
2. **Quantum Simulation**: Compare Shor's Algorithm performance on CPU (AMD EPYC), GPU (A100), and IBM QPU
3. **Hybrid Approaches**: Explore QAOA-inspired training for classical neural networks
4. **Cryptographic Analysis**: Evaluate the effectiveness of different approaches to password/hash problems

### Hardware Platforms

| Platform | Use Case |
|----------|----------|
| **AMD EPYC** | CPU baseline for RNN training and quantum simulation |
| **NVIDIA A100** | GPU-accelerated RNN training and quantum simulation |
| **IBM Quantum (QPU)** | Real quantum hardware execution |

---

## Project Components

### 1. Neural Network Implementations

#### **`basic-net/`** - Basic RNN
Simple character-level RNN for password generation.
- `model.py` - Basic LSTM architecture
- `train.py` - Training loop
- `generate.py` - Password generation
- `data_prep.py` - Data preprocessing

#### **`better-net/`** - Enhanced RNN
Improved RNN with better architecture and training strategies.
- Enhanced LSTM with dropout and regularization
- Temperature-based sampling
- Multiple generation strategies
- Pre-trained model included (`password_rnn.pth`)

#### **`hash-net/`** - Hash Cracker RNN 🔥
QAOA-inspired neural network for hash cracking.

**Key Features:**
- Multi-objective loss function (hash matching + character prediction + diversity)
- Differentiable hash approximation
- Smart generation with temperature sampling
- Repetition prevention mechanisms

**Files:**
- `hash_model.py` - Neural architecture
- `qaoa_train.py` - QAOA-inspired training
- `hash_generate.py` - Hash cracking generation
- `simple_hash.py` - Differentiable hash function
- `verify_model.py` - Model verification

<!--**Performance:**
- Hash Similarity: 40-60%
- Training Time: 30-60 minutes (150 epochs)
- Generation Speed: ~100ms per attempt-->

#### **`Neural net/`** - Original Implementation
Initial prototype and experimental code.

---

### 2. Quantum Implementations

#### **`shorsTest/`** - Shor's Algorithm Suite

Comprehensive implementation and testing of Shor's factoring algorithm.

**Implementations:**
- `shor_simulation.py` - Simulator-based implementation
- `shor_actual.py` - IBM Quantum hardware implementation
- `shor_generic.py` - Generic implementation for any composite number

**Analysis Tools:**
- `analyze.py` - Performance analysis and visualization
- `batch_run.sh` - Automated benchmark execution
- `plots/` - Generated performance plots

**Documentation:**
- `README.md` - Quick start and guide
- `ACTUAL.md` - Detailed explanation of parameters
- `Generic vs Targeted.md` - Implementation comparison

<!--**Key Metrics:**
- Qubits needed: 12 for N=15 (fixed), O(log N) for generic
- Circuit depth: ~150-200 gates
- Success rate: Varies by implementation and hardware-->

---

### 3. Utility Scripts

#### **Password Hashing Tools**

**`Hash_Password.sh`** - Custom Hash Function
```bash
./Hash_Password.sh 'MyP@ssw0rd!'
```
- Multi-accumulator prime-based hashing
- 64-character hexadecimal output
- Designed for RNN training data generation

**`Custom_Password_Hash_Generator.sh`** - Batch Custom Hashing
```bash
./Custom_Password_Hash_Generator.sh 10000
```
- Generates N random passwords (4-16 characters)
- Applies custom hash function
- Parallel execution across all CPU cores
- Output: `custom_password_hashes.txt`

**`Actual_Password_Hash_Generator.sh`** - Multi-Algorithm Hashing
```bash
./Actual_Password_Hash_Generator.sh 10000
```
- Generates N random passwords (4-16 characters)
- Applies multiple hash algorithms:
  - SHA-1
  - SHA-3
  - SHA-256
  - SHA-512
  - SHA-512Q (placeholder for quantum-resistant)
- Output: `actual_password_hashes.txt`

<!--**Performance:**
- Up to 500,000 passwords supported
- Parallel processing on all cores
- Runtime: ~30-60 seconds for 10,000 passwords-->

---

## Installation

### Prerequisites

```bash
# System packages (Rocky Linux / RHEL)
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y cmake git wget curl openssl-devel zlib-devel \
    openblas-devel lapack-devel openmpi openmpi-devel

# Enable MPI
export PATH=/usr/lib64/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:$LD_LIBRARY_PATH
```

### Python Environment Setup

#### For RNN Components (PyTorch)

```bash
# Create virtual environment
python3 -m venv pytorch_env
source pytorch_env/bin/activate

# Install dependencies
pip install --upgrade pip
pip install torch torchvision torchaudio numpy matplotlib
```

#### For Quantum Components (Qiskit)

```bash
# Create separate virtual environment
python3 -m venv qiskit_env
source qiskit_env/bin/activate

# Install Qiskit
pip install --upgrade pip
pip install qiskit[all] qiskit-aer qiskit-ibm-runtime
```

### Clone Repository

```bash
git clone <repository-url>
cd classical-and-quantum-cryptography
```

---

## Usage

### Neural Network Training

#### Basic Password Generation RNN

```bash
cd better-net
source ~/pytorch_env/bin/activate

# Generate training data
python generate_training_data.py --count 10000 --output passwords.txt

# Train model
python train.py

# Generate passwords
python generate.py
```

#### Hash Cracker RNN

```bash
cd hash-net
source ~/pytorch_env/bin/activate

# 1. Generate training data
python generate_training_data.py --count 10000 --output passwords.txt

# 2. Train the hash cracker
python qaoa_train.py

# 3. Test hash cracking
python hash_generate.py

# 4. Verify model performance
python verify_model.py
```

**Advanced Usage:**

```python
from smart_generate import smart_crack_hash
from simple_hash import SimpleHashFunction

hash_function = SimpleHashFunction()
target_hash = hash_function.actual_hash("mypassword123")

cracked, similarity = smart_crack_hash(
    target_hash,
    max_attempts=20,
    max_length=20
)
```

---

### Quantum Algorithm Execution

#### Shor's Algorithm - Simulation

```bash
cd shorsTest
source ~/qiskit_env/bin/activate

# Run on simulator
python3 shor_simulation.py

# Generic implementation (any composite number)
python3 shor_generic.py
```

#### Shor's Algorithm - Real Quantum Hardware

```bash
# Configure IBM Quantum credentials
# Set up your IBM Quantum account at https://quantum-computing.ibm.com/

# Run on IBM QPU
python3 shor_actual.py
```

#### Batch Benchmarking

```bash
# Run comprehensive benchmark suite
./batch_run.sh

# Analyze results
python3 analyze.py

# View generated plots
ls plots/
```

---

### Password Generation & Hashing

#### Generate Custom Hash Dataset

```bash
# Generate 10,000 passwords with custom hash
./Custom_Password_Hash_Generator.sh 10000

# Output: custom_password_hashes.txt
# Format: password: hash
```

#### Generate Multi-Algorithm Hash Dataset

```bash
# Generate 10,000 passwords with multiple hash algorithms
./Actual_Password_Hash_Generator.sh 10000

# Output: actual_password_hashes.txt
# Format:
# password
#   SHA-1:     hash
#   SHA-3:     hash
#   SHA-256:   hash
#   SHA-512:   hash
#   SHA-512Q:  hash
```

#### Hash Single Password

```bash
# Custom hash algorithm
./Hash_Password.sh 'SecurePassword123!'

# Output: Password and 64-character hex hash
```

---

## Benchmarking

### RNN Performance Benchmarking

#### Setup

```python
# benchmark_rnn.py
import torch
import time
from model import PasswordRNN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = PasswordRNN().to(device)

# Benchmark training
start = time.time()
train_model(model, epochs=100)
train_time = time.time() - start

# Benchmark inference
start = time.time()
for _ in range(1000):
    generate_password(model)
inference_time = time.time() - start

print(f"Training: {train_time:.2f}s")
print(f"Inference (1000 passwords): {inference_time:.2f}s")
```

#### Run Benchmarks

```bash
# On AMD EPYC (CPU)
CUDA_VISIBLE_DEVICES="" python benchmark_rnn.py

# On NVIDIA A100 (GPU)
CUDA_VISIBLE_DEVICES=0 python benchmark_rnn.py
```

---

### Quantum Simulation Benchmarking

#### Setup

```bash
cd shorsTest

# Edit batch_run.sh to configure:
# - Number of runs
# - Qubit counts
# - Backend types (CPU/GPU simulator)
```

#### Execute Benchmark Suite

```bash
./batch_run.sh

# Results saved to:
# - shor_results.csv (raw data)
# - experiment_log.txt (detailed log)
# - plots/ (visualizations)
```

#### Analyze Results

```bash
python3 analyze.py

# Generates:
# - Performance comparison plots
# - Success rate analysis
# - Resource utilization metrics
```

---

<!--## Results

### Expected Performance Characteristics

#### RNN Training (100 epochs, 10K passwords)

| Hardware | Training Time | Inference (1000 passwords) | Memory Usage |
|----------|---------------|---------------------------|--------------|
| AMD EPYC (64 cores) | ~45-60 min | ~5-10 sec | ~4 GB |
| NVIDIA A100 (40GB) | ~10-15 min | ~1-2 sec | ~8 GB |

#### Shor's Algorithm (N=15, 12 qubits)

| Backend | Execution Time | Success Rate | Resource Requirements |
|---------|---------------|--------------|----------------------|
| Qiskit Aer (CPU) | ~2-5 sec | 70-85% | 16 GB RAM |
| Qiskit Aer (GPU) | ~0.5-1 sec | 70-85% | 8 GB VRAM |
| IBM QPU | ~minutes-hours (queue) | 40-60% | Real quantum hardware |

#### Hash Cracker RNN Performance

| Metric | Value |
|--------|-------|
| Hash Similarity | 40-60% |
| Exact Match Rate | 0% (current implementation) |
| Training Time (150 epochs) | 30-60 minutes |
| Generation Speed | ~100ms per attempt |
| Model Parameters | ~1.5 million |-->

<!--------->
<!--
## Architecture Details

### RNN Architecture (Hash Cracker)

```
Input: Target Hash (128-bit binary vector)
  ↓
Hash Encoder (Linear 128 → 128)
  ↓
Character Embeddings (Vocab size: 72, Embedding dim: 64)
  ↓
2-Layer LSTM (Hidden size: 256, Dropout: 0.2)
  ↓
Output Layer (Linear 256 → 72)
  ↓
Character Probabilities (Softmax)
```

**Loss Function (QAOA-inspired):**
```
Total Loss = α × Hash_Loss + β × Char_Loss + γ × Diversity_Loss

where:
  α = 1.0   (hash matching weight)
  β = 0.1-0.2 (character prediction weight)
  γ = 0.05  (diversity penalty weight)-->
<!--```-->
<!--
### Shor's Algorithm Quantum Circuit

```
Counting Qubits (n_count = 8):
  H—•—————————QFT†—M
  H—•—————————QFT†—M
  H—•—————————QFT†—M
  ... (8 qubits)

Work Qubits (n_work = 4):
  |0⟩—[Controlled Modular Multiplication]—
  |0⟩—[Controlled Modular Multiplication]—
  |0⟩—[Controlled Modular Multiplication]—
  |1⟩—[Controlled Modular Multiplication]—
```

**Stages:**
1. Hadamard gates on counting qubits (superposition)
2. Controlled modular exponentiation (phase kickback)
3. Inverse Quantum Fourier Transform (period extraction)
4. Measurement and classical post-processing-->

<!------->

## Additional Documentation

- **`shorsTest/ACTUAL.md`** - Detailed explanation of Shor's algorithm parameters
- **`shorsTest/Generic vs Targeted.md`** - Comparison of implementation strategies
- **`hash-net/instructions.txt`** - Comprehensive hash cracker RNN manual
- **`dftb.md`** - DFTB+ installation guide (optional quantum chemistry component)

---

## Research Applications

### Cryptographic Security Analysis
- **Password Strength Evaluation**: Test password generation strategies
- **Hash Function Robustness**: Evaluate resistance to ML-based attacks
- **Post-Quantum Cryptography**: Assess quantum algorithm threat to current systems

### Algorithm Benchmarking
- **Classical vs Quantum**: Direct performance comparison
- **Hardware Evaluation**: CPU vs GPU vs QPU characteristics
- **Scalability Analysis**: Performance as problem size increases

### Machine Learning Research
- **QAOA-Inspired Training**: Novel loss functions for optimization
- **Hybrid Classical-Quantum**: Combining strengths of both approaches
- **Adversarial Training**: Neural networks vs cryptographic primitives

---

## Troubleshooting

### Common Issues

#### "No training pairs created"
```bash
# Solution: Regenerate training data
python generate_training_data.py --count 10000 --output passwords.txt
```

#### "CUDA out of memory"
```python
# Solution: Reduce batch size
# Edit train.py:
batch_size = 32  # Instead of 64
```

#### "Device mismatch errors"
```python
# Solution: Ensure all tensors on same device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
input_tensor = input_tensor.to(device)
```

#### Qiskit Authentication Error
```bash
# Solution: Configure IBM Quantum credentials
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(channel="ibm_quantum", token="YOUR_TOKEN")
```