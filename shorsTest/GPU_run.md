# GPU Acceleration Setup for Shor's Algorithm

## Overview

Running Shor's algorithm on GPU (like NVIDIA A100) can provide significant speedup for larger circuits. This guide covers setup and usage.

## Requirements

### Hardware
- **NVIDIA GPU** with CUDA support (tested on A100)
- **Minimum**: CUDA Compute Capability 7.0+
- **Recommended**: A100, V100, or similar datacenter GPU

### Software
- NVIDIA CUDA Toolkit 11.2+
- cuQuantum SDK (optional, but recommended for best performance)
- Python 3.8+

## Installation

### 1. Install CUDA

```bash
# Check if CUDA is installed
nvcc --version

# If not installed, download from NVIDIA website
# https://developer.nvidia.com/cuda-downloads
