HPC Software Installation and Setup Guide
Overview

This document provides comprehensive instructions for installing and configuring high-performance computing (HPC) software on Ubuntu server nodes. The guide follows best practices for scientific computing environments with optimized performance.
Table of Contents

    System Requirements

    Package Installation

    Development Environment Setup

    MPI Configuration

    Conda/Mamba Environment

    Software Compilation

    Testing and Validation

    Troubleshooting

System Requirements
Minimum Specifications

    OS: Ubuntu 20.04 LTS or newer

    CPU: x86_64 architecture

    RAM: 8GB minimum (16GB+ recommended)

    Storage: 50GB free space

    Network: Internet access for package downloads

Recommended for HPC

    Multi-core processors

    High-speed interconnects (Infiniband, Omni-Path)

    NFS/shared storage for cluster deployments

Package Installation
1. System Update and Base Packages
bash

sudo apt update
sudo apt upgrade -y

# Install essential development tools
sudo apt install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    cmake \
    cmake-curses-gui \
    make \
    autoconf \
    automake \
    libtool \
    pkg-config \
    git \
    wget \
    curl \
    libssl-dev \
    zlib1g-dev

2. Mathematical Libraries
bash

sudo apt install -y \
    libopenblas-dev \
    liblapack-dev \
    liblapacke-dev \
    libfftw3-dev \
    libfftw3-mpi-dev \
    libscalapack-mpi-dev \
    libopenmpi-dev

3. Parallel Computing and I/O
bash

sudo apt install -y \
    openmpi-bin \
    libopenmpi-dev \
    mpich \
    libmpich-dev \
    libhdf5-dev \
    libhdf5-mpi-dev \
    libnetcdf-dev \
    libnetcdff-dev \
    libpnetcdf-dev

4. Python and Additional Tools
bash

sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-setuptools \
    environment-modules \
    nfs-common \
    hwloc \
    numactl

Development Environment Setup
Compiler Configuration

Add to your ~/.bashrc:
bash

# Compiler and MPI environment
export PATH=/usr/lib/x86_64-linux-gnu/openmpi/bin:$PATH
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/openmpi/lib:$LD_LIBRARY_PATH

# Set default compilers
export CC=mpicc
export CXX=mpicxx
export FC=mpif90
export F77=mpif77

# Additional flags for optimization
export CFLAGS="-O3 -march=native"
export CXXFLAGS="-O3 -march=native"
export FCFLAGS="-O3 -march=native"

# For OpenMP support
export OMP_NUM_THREADS=$(nproc)

Apply the changes:
bash

source ~/.bashrc

MPI Configuration
Verification Steps
bash

# Check MPI installation
mpirun --version
which mpicc
mpicc --version

# Test MPI functionality
mpirun -np 4 hostname

# Benchmark MPI communication
mpirun -np 2 pingpong

Multiple MPI Implementation Support

To switch between MPI implementations:
bash

# For OpenMPI
sudo update-alternatives --install /usr/bin/mpicc mpicc /usr/bin/mpicc.openmpi 30
sudo update-alternatives --install /usr/bin/mpif90 mpif90 /usr/bin/mpif90.openmpi 30

# For MPICH
sudo update-alternatives --install /usr/bin/mpicc mpicc /usr/bin/mpicc.mpich 40
sudo update-alternatives --install /usr/bin/mpif90 mpif90 /usr/bin/mpif90.mpich 40

# Configure default
sudo update-alternatives --config mpicc

Conda/Mamba Environment
Installation and Setup
bash

# Clean existing conda initializations
sed -i '/>>> conda initialize >>>/,/<<< conda initialize <<</d' ~/.bashrc
sed -i '/>>> mamba initialize >>>/,/<<< mamba initialize <<</d' ~/.bashrc
exec bash

# Download and install Miniforge
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh -b -p $HOME/miniforge3

# Initialize conda
echo "export PATH=\"\$HOME/miniforge3/bin:\$PATH\"" >> ~/.bashrc
source ~/.bashrc

export PATH="$HOME/miniforge3/bin:$PATH"

# Install mamba for faster package management
conda install mamba -n base -c conda-forge -y

# Verify installation
conda --version
mamba --version

Common Scientific Packages
bash

# Create a scientific computing environment
mamba create -n science -c conda-forge \
    numpy \
    scipy \
    matplotlib \
    pandas \
    jupyter \
    jupyterlab \
    h5py \
    netcdf4 \
    mpi4py \
    cmake \
    compilers \
    openmpi

conda activate science

Software Compilation
General Build Process
bash

# Example compilation workflow
git clone <repository_url>
cd <software_directory>
mkdir build && cd build

# Configure with CMake
cmake .. \
    -DCMAKE_INSTALL_PREFIX=$HOME/software/<package_name> \
    -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_MPI=ON \
    -DENABLE_OPENMP=ON \
    -DBUILD_SHARED_LIBS=ON

# Build and install
make -j$(nproc)
make install

# Add to PATH
echo "export PATH=\"\$HOME/software/<package_name>/bin:\$PATH\"" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=\"\$HOME/software/<package_name>/lib:\$LD_LIBRARY_PATH\"" >> ~/.bashrc
source ~/.bashrc

Performance Optimization Flags
bash

# For GCC
export CFLAGS="-O3 -march=native -ffast-math -funroll-loops"
export CXXFLAGS="-O3 -march=native -ffast-math -funroll-loops"
export FCFLAGS="-O3 -march=native -ffast-math -funroll-loops"

# For Intel compilers (if available)
export CFLAGS="-O3 -xHost -ip -fp-model fast=2"
export CXXFLAGS="-O3 -xHost -ip -fp-model fast=2"
export FCFLAGS="-O3 -xHost -ip -fp-model fast=2"

Testing and Validation
System Verification
bash

# Test compilers
$CC --version
$CXX --version
$FC --version

# Test MPI
mpirun -np 2 echo "MPI working"

# Test OpenMP
echo | $CC -fopenmp -E - > /dev/null && echo "OpenMP supported"

# Check mathematical libraries
pkg-config --cflags --libs openblas
pkg-config --cflags --libs fftw3

Performance Benchmarks
bash

# BLAS performance test
git clone https://github.com/xianyi/OpenBLAS
cd OpenBLAS
make -j$(nproc)
make install PREFIX=$HOME/software/OpenBLAS

# Run simple matrix multiplication test
cd benchmark
make
./sgemm.goto

Troubleshooting
Common Issues and Solutions

    MPI Runtime Errors
    bash

# Fix library paths
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/openmpi/lib:$LD_LIBRARY_PATH

# Check process limits
ulimit -a

Missing Dependencies
bash

# Use apt-file to find packages
sudo apt install apt-file
sudo apt-file update
apt-file search <missing_file>

Python Package Conflicts
bash

# Clean conda cache
conda clean --all

# Create fresh environment
conda remove -n science --all
mamba create -n science <packages>

Compilation Failures
bash

# Check for mixed compiler versions
which gcc
which mpicc

# Verify environment variables
echo $CC
echo $CXX
echo $FC

Performance Tuning

    Processor Affinity
    bash

# Set CPU affinity for better performance
export OMP_PROC_BIND=true
export OMP_PLACES=cores

Memory Allocation
bash

# For large memory applications
export OMP_STACKSIZE=512M
ulimit -s unlimited

MPI Tuning
bash

# Optimize MPI for your network
export OMPI_MCA_btl=self,vader,tcp,openib
export OMPI_MCA_mpi_leave_pinned=1

Maintenance
Regular Updates
bash

# System updates
sudo apt update && sudo apt upgrade -y

# Conda environment updates
conda update --all -n base
conda clean --all

# Rebuild software with latest dependencies
cd <software_build_directory>
git pull
make clean
make -j$(nproc)

Backup Configuration
bash

# Backup important configuration files
cp ~/.bashrc ~/.bashrc.backup
conda env export -n science > environment.yml
