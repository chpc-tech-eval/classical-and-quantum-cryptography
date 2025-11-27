# DFTB+ - Installation and setup

## What is it? 

"DFTB+ is a software package for carrying out fast quantum mechanical atomistic calculations based on the Density Functional Tight Binding method"
It can be used as a standalone application or integrated as a library. Needs parameterisation data (Slater-Koster files) in order to perform calculations.

## GitHub repo and website:

![Repo](https://github.com/dftbplus/dftbplus/tree/24.1)

![Website](https://dftbplus.org)

## Prerequisites and setup 

We will install:
 * Miniforge (user-level Conda distribution)
 * Mamba (fast environment solver)
 * Compilers: gcc, gfortran, cmake
 * Math libs: OpenBLAS / LAPACK
 * MPI: OpenMPI
 * DFTB+ (24.1 branch)
 * Optional: GPU-accelerated Hamiltonian builder (if needed later)

All installations are user-local, meaning nothing is written to /usr, and root access is not required

1) Before anything else, ensure compiler toolchains and basic utilities are installed:

   ```
    sudo dnf groupinstall -y "Development Tools"
    sudo dnf install -y \
    cmake \
    git \
    wget \
    curl \
    openssl-devel \
    zlib-devel \
    openblas-devel \
    lapack-devel \
    fftw-devel \
    openmpi openmpi-devel
   ```
$$\color{Red}Add\ more\ prereqs\ here\ as\ needed$$

Enable MPI in the shell, and test that its present:

  ```
  echo "export PATH=/usr/lib64/openmpi/bin:\$PATH" >> ~/.bashrc
  echo "export LD_LIBRARY_PATH=/usr/lib64/openmpi/lib:\$LD_LIBRARY_PATH" >> ~/.bashrc
  source ~/.bashrc
  mpirun --version
  ```

2) Conda installation, remove the weird read-only Conda that comes stock with Rocky

  ```
  sed -i '/>>> conda initialize >>>/,/<<< conda initialize <<</d' ~/.bashrc
  exec bash
  #check if conda is gone, should outut nothing
  #didnt work for me though
  which conda
  ```

3) install Miniforge, Conda/Mamba on the user level

```
  cd ~
  curl -LO https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
  bash Miniforge3-Linux-x86_64.sh
  #accept default values in installers, install to ~/miniforge3 and 'yes' to conda init
  #reload shell and test, should output paths under ~/miniforge3/bin
  exec bash
  which conda
  which mamba
  conda --version
  mamba --version
```

4) Actually set up the DFTB+ build environment, we will use a mamba environment with some common libraries and dependencies

```
mamba create -y -n dftbplus \
    python=3.11 \
    numpy \
    fftw \
    cmake \
    openmpi \
    openblas \
    lapack \
    scalapack \
    make \
    gcc \
    gxx \
    gfortran

#if we get issues here, check package names, they are different on different distros. for instance i has scalapack-mpi at first which threw a fit

mamba activate dftbplus
```

5) Now within our environment, clone the DFTB+ repo

```
mkdir -p ~/src && cd ~/src
git clone https://github.com/dftbplus/dftbplus.git
cd dftbplus
git checkout 24.1

#24.1 is the latest stable release 
```
6) Build DFTB+ from source

```
mkdir build && cd build
cmake .. \
    -DWITH_MPI=ON \
    -DWITH_OPENMP=ON \
    -DWITH_SCALAPACK=ON \
    -DSCALAPACK_LIBRARY=$CONDA_PREFIX/lib/libscalapack.so \
    -DBLAS_LIBRARIES="$CONDA_PREFIX/lib/libopenblas.so" \
    -DLAPACK_LIBRARIES="$CONDA_PREFIX/lib/libopenblas.so" \
    -DCMAKE_BUILD_TYPE=Release

make -j$(nproc)

```

7) Next, we need to choose parameterization files to perform the tests, these can be found at ![dftb.org](dftb.org), for this we are trying out PTBP, as this is a general test that covers quite a bit:

The PTBP download link takes us to a page where we select options for thee file we want to download. Now I have no idea how to do this on the node, so I did everything on my laptop and did an SCP to get the files on the node.
It might be a good idea to pregenerate a few of these and add them to the repo.

*Added under folder ~/dftb_data on the A100

```

```



  
