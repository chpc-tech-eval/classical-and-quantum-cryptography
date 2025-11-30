# ASCOT5 5.6.2 - HPC Installation and Setup

## What is it?

ASCOT5 (Accelerated Simulation of Charged Particle Orbits in Tokamaks) is a high-performance, test-particle orbit-following code for fusion plasma physics and engineering. It is designed to solve minority species' distribution functions, transport, and losses in tokamaks and stellarators. The code can trace full gyro-orbits, guiding centers, field-lines, and neutrals, and is extensively parallelized to support simulations with large numbers of markers.

## GitHub repo and documentation

- **Repository**: [https://github.com/ascot4fusion/ascot5](https://github.com/ascot4fusion/ascot5) 
- **Documentation**: [https://ascot4fusion.github.io/ascot5/](https://ascot4fusion.github.io/ascot5/) 

## Prerequisites and Setup

We will install the following components optimized for HPC:
* Miniforge (user-level Conda distribution)
* Mamba (fast environment solver)
* Intel-optimized compilers and libraries
* MPI: OpenMPI (optimized for Intel)
* Math libraries: OpenBLAS, LAPACK, FFTW
* HDF5 with MPI support
* ASCOT5 (version 5.6.2) from source with MPI parallelization

### 1) System Package Installation (Head Node)

Install all necessary dependencies on the head node:

```bash
sudo apt update
sudo apt upgrade -y

# Install development tools and compilers
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
    zlib1g-dev \
    libopenblas-dev \
    liblapack-dev \
    libfftw3-dev \
    libfftw3-mpi-dev \
    openmpi-bin \
    libopenmpi-dev \
    python3-dev \
    python3-pip \
    python3-venv \
    libhdf5-dev \
    libhdf5-mpi-dev \
    libnetcdf-dev \
    libnetcdff-dev \
    environment-modules \
    nfs-common
```

### 2) MPI and environment setup (if not already done)

```bash
# Add to ~/.bashrc for all users
echo "export PATH=/usr/lib/x86_64-linux-gnu/openmpi/bin:\$PATH" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/openmpi/lib:\$LD_LIBRARY_PATH" >> ~/.bashrc
echo "export CC=mpicc" >> ~/.bashrc
echo "export CXX=mpicxx" >> ~/.bashrc
echo "export FC=mpif90" >> ~/.bashrc
echo "export F77=mpif77" >> ~/.bashrc

source ~/.bashrc

# Test MPI installation
mpirun --version
which mpicc
mpicc --version
```

### 3) Conda/Mamba installation in the shared NFS directory

```bash
# Clean up any existing conda initialization
sed -i '/>>> conda initialize >>>/,/<<< conda initialize <<</d' ~/.bashrc
sed -i '/>>> mamba initialize >>>/,/<<< mamba initialize <<</d' ~/.bashrc
exec bash

# Download and install Miniforge in shared location
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh -b -p $HOME/miniforge3

# Initialize conda for all nodes
echo "export PATH=\"\$HOME/miniforge3/bin:\$PATH\"" >> ~/.bashrc
source ~/.bashrc

export PATH="$HOME/miniforge3/bin:$PATH"

# Install mamba for faster dependency solving
conda install mamba -n base -c conda-forge -y

# Verify installation
conda --version
mamba --version
```

### 5) Build ASCOT5 from source

```bash
#clone the repo
git clone https://github.com/ascot4fusion/ascot5.git
cd ascot5

#install a5py and compile the executables
#will be located at build/
# ~/ascot5/build

make clean
make ascot5_main -j MPI=1
make libascot -j MPI=1
pip install -e .

```

### 4) Configure the HPC optimized ASCOT5 environment

```bash
# Create environment with MPI and HPC packages (choose ONE MPI implementation)
mamba create -n ascot5 python=3.10 numpy scipy matplotlib h5py jupyter ipython cmake make compilers fftw openblas hdf5 netcdf4 -c conda-forge -y

# Manually set the path and activate
export PATH="$HOME/miniforge3/bin:$PATH"
source activate ascot5

# Option A: Install with MPICH (recommended for stability)
mamba install -c conda-forge \
    numpy \
    scipy \
    matplotlib \
    h5py \
    jupyter \
    ipython \
    cmake \
    make \
    compilers \
    mpich \
    fftw \
    openblas \
    hdf5 \
    netcdf4 \
    -y

# OR Option B: Install with OpenMPI (if you prefer)
# mamba install -c conda-forge \
#     numpy \
#     scipy \
#     matplotlib \
#     h5py \
#     jupyter \
#     ipython \
#     cmake \
#     make \
#     compilers \
#     openmpi \
#     fftw \
#     openblas \
#     hdf5 \
#     netcdf4 \
#     -y

# Then install mpi4py separately
pip install mpi4py

# Verify MPI support in Python
python -c "from mpi4py import MPI; print(f'MPI version: {MPI.Get_version()}, Library: {MPI.get_vendor()}')"
```

### 6) Export text editor and test by running the introduction

```bash
export EDITOR=/usr/bin/nano

#ascot uses jupyter notebooks
pip install jupyter
ipython kernel install --user --name=ascotenv

#this was an issue i dont think i installed it in the venv
pip install -e .

#install jupyterlab because im not doing this in a terminal
pip install jupyterlab ipywidgets plotly jupyter-dash
jupyter lab --ip 0.0.0.0 --port 8889 --no-browser

#look for this: http://127.0.0.1:8889/lab?token=<TOKEN>
#http://<headnode_public_ip>:8889

```
We will be working on files stored in ascot5/doc/tutorials
```
#running the scripts 

```
## Quick reset

```
export PATH="$HOME/miniforge3/bin:$PATH"
source activate ascot5

pip install jupyterlab ipywidgets plotly jupyter-dash
jupyter lab --ip 0.0.0.0 --port 8889 --no-browser

```
