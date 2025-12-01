### 1) HPL setup - install dependencies

```bash
sudo apt update
sudo apt install build-essential openmpi-bin libopenmpi-dev libatlas-base-dev
```

### 2) Download the HPL source files

```bash
# Download the source files
wget http://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz

# Extract the files from the tarball
tar -xzf hpl-2.3.tar.gz

# Move and go into the newly extracted folder
mv hpl-2.3 ~/hpl
cd ~/hpl

# list the contents of the folder
ls
```

### 3) Configure HPL

This is mainly done through a makefile, needs to support our specific system config

```
cp setup/Make.Linux_PII_CBLAS_gm Make.tuksbyters
sudo nano Make.tuksbyters
```

this file will need to be changed:

```
ARCH               = tuksbyters

MPdir              = /usr/lib/x86_64-linux-gnu/openmpi

LAdir              = /usr/lib/x86_64-linux-gnu/atlas/
LAlib              = /usr/lib/x86_64-linux-gnu/libopenblas.so

CC                 = mpicc

LINKER             = mpicc
```
### 4) edit the path variable and compile (this had issues so changed LAlib in prev step)

```
which mpicc

# Temporarily append openmpi binary path to your PATH variable
# These settings will reset after you logout and re-login again.
export PATH=/usr/lib64/openmpi/bin:$PATH

# Rerun the which command to confirm that the `mpicc` binary is found
which mpicc

#compile
make arch=tuksbyters
#check for xhpl and HPL.dat
ls bin/tuksbyters
```

### 5) edit the .dat file and run

```
cd bin/tuksbyters
sudo nano HPL.dat
```
 make these changes

```
1            # of process grids (P x Q)
1            Ps
1            Qs
```

and finally, ```./xhpl```

#This is the most basic way to run hpl, should be enough for a submission, but we need to optimise it, currently only on 1cpu core on 1node.

### Part 2, making it better

edit the hpl.dat file to actually use our CPU properly 

```
22000         Ns
1            # of NBs
164           NBs
```

### Compiling from source - OpenBLAS, OpeMPI

```
#dependencies
sudo apt install build-essential hwloc libhwloc-dev libevent-dev gfortran wget

#compiling openBLAS
git clone https://github.com/xianyi/OpenBLAS.git
cd OpenBLAS

#known to be stable
git checkout v0.3.26

make
make PREFIX=$HOME/opt/openblas install

#OpenMPI download and compile
wget https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-4.1.4.tar.gz
tar xf openmpi-4.1.4.tar.gz
cd openmpi-4.1.4

# Pay careful attention to tuning options here, and ensure they correspond
# to your compute node's processor.
#
# If you are unsure, you can replace the `cascadelake` architecture option
# with `native`, however you are expected to determine your compute node's
# architecture using `lscpu` or similar tools.
#
# Once again you can adjust the --prefix to install to your preferred path.
CFLAGS="-Ofast -march=native -mtune=native" ./configure --prefix=$HOME/opt/openmpi

# Use the maximum number of threads to compile the application
make -j$(nproc)
make install
```


# there were problems with conflicting package MPI and custom compiled MPI, so clanker assisted scripts

HPC Performance Optimization Guide
Custom OpenMPI + OpenBLAS + HPL Setup for Intel Xeon Gold 6448H
📋 Prerequisites
bash

# System updates and dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential gcc g++ gfortran cmake make \
    autoconf automake libtool pkg-config git wget curl \
    libhwloc-dev hwloc numactl environment-modules

🔧 Step 1: Custom OpenBLAS Compilation (Optional, for Max Performance)
bash

# Download and compile OpenBLAS with Sapphire Rapids optimizations
cd /tmp
git clone https://github.com/xianyi/OpenBLAS.git
cd OpenBLAS
git checkout v0.3.26

# Build with AVX-512 optimizations
make TARGET=SAPPHIRERAPIDS USE_OPENMP=1 NUM_THREADS=64
make PREFIX=$HOME/opt/openblas install

# Add to environment
echo 'export OPENBLAS_HOME=$HOME/opt/openblas' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=$OPENBLAS_HOME/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

🚀 Step 2: Custom OpenMPI Compilation
bash

# Clean any previous builds
rm -rf ~/opt/openmpi /tmp/openmpi-*

# Download and build OpenMPI with proper hwloc support
cd /tmp
wget https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-4.1.5.tar.gz
tar -xzf openmpi-4.1.5.tar.gz
cd openmpi-4.1.5

# Configure for Intel Xeon Gold 6448H (Sapphire Rapids)
./configure --prefix=$HOME/opt/openmpi \
    CC=/usr/bin/gcc \
    CXX=/usr/bin/g++ \
    FC=/usr/bin/gfortran \
    --with-hwloc=internal \
    --with-libevent=internal \
    --with-pmix=internal \
    --enable-mpi-cxx \
    CFLAGS="-Ofast -march=sapphirerapids -mtune=sapphirerapids" \
    CXXFLAGS="-Ofast -march=sapphirerapids -mtune=sapphirerapids"

# Compile and install
make -j$(nproc)
make install

# Verify build
$HOME/opt/openmpi/bin/mpicc --version
$HOME/opt/openmpi/bin/mpirun --version

🎯 Step 3: Isolated MPI Environment Setup
bash

# Create environment module (professional approach)
mkdir -p ~/privatemodules/openmpi
cat > ~/privatemodules/openmpi/4.1.5 <<'EOF'
#%Module1.0
proc ModulesHelp { } {
    puts stderr "Custom OpenMPI 4.1.5 optimized for Sapphire Rapids"
}
module-whatis "Custom OpenMPI 4.1.5"
prepend-path PATH /home/tuksbyters/opt/openmpi/bin
prepend-path LD_LIBRARY_PATH /home/tuksbyters/opt/openmpi/lib
setenv MPI_HOME /home/tuksbyters/opt/openmpi
setenv OMPI_DIR /home/tuksbyters/opt/openmpi
EOF

# Alternative: Simple environment script
cat > ~/activate_custom_mpi.sh <<'EOF'
#!/bin/bash
export OMPI_DIR=$HOME/opt/openmpi
export PATH=$OMPI_DIR/bin:$PATH
export LD_LIBRARY_PATH=$OMPI_DIR/lib:$LD_LIBRARY_PATH
export MPI_HOME=$OMPI_DIR
EOF

chmod +x ~/activate_custom_mpi.sh

📦 Step 4: HPL Compilation with Custom Stack
bash

# Download HPL
cd ~
wget https://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz
tar -xzf hpl-2.3.tar.gz
mv hpl-2.3 hpl
cd hpl

# Create optimized Makefile for your system
cp setup/Make.Linux_Intel64 Make.compile_BLAS_MPI

# Edit Make.compile_BLAS_MPI with these key settings:
cat > Make.compile_BLAS_MPI <<'EOF'
ARCH         = compile_BLAS_MPI

# Custom OpenMPI paths
MPdir        = $(HOME)/opt/openmpi
MPinc        = -I$(MPdir)/include
MPlib        = $(MPdir)/lib/libmpi.so

# OpenBLAS paths (system or custom)
LAdir        = /usr  # or $(HOME)/opt/openblas for custom
LAinc        =
LAlib        = $(LAdir)/lib/x86_64-linux-gnu/libopenblas.so -lpthread -lm

# Compiler settings
CC           = mpicc
CCFLAGS      = $(HPL_DEFS) -O3 -march=native -mtune=native -fopenmp -fomit-frame-pointer
LINKER       = $(CC)
LDFLAGS      = $(CCFLAGS)

# Shell commands (CRITICAL)
SHELL        = /bin/sh
CD           = cd
CP           = cp
LN_S         = ln -s
MKDIR        = mkdir
RM           = /bin/rm -f
TOUCH        = touch
EOF

# Activate custom MPI and build
source ~/activate_custom_mpi.sh
make arch=compile_BLAS_MPI

⚡ Step 5: Running HPL on All Cores
bash

cd ~/hpl/bin/compile_BLAS_MPI

# Create optimal HPL.dat for 64 cores (2×32)
cat > HPL.dat <<'EOF'
HPLinpack benchmark input file
Innovative Computing Laboratory, University of Tennessee
HPL.out      output file name (if any)
6            device out (6=stdout,7=stderr,file)
1            # of problems sizes (N)
100000       Ns  # Adjust based on memory: ~80% of system RAM
1            # of NBs
256          NBs  # Try 192, 224, 256, 384 for best performance
0            PMAP process mapping (0=Row-,1=Column-major)
1            # of process grids (P x Q)
8            Ps   # 8×8 = 64 processes
8            Qs
16.0         threshold
1            # of panel fact
2            PFACTs (0=left, 1=Crout, 2=Right)
1            # of recursive stopping criterium
4            NBMINs (>= 1)
1            # of panels in recursion
2            NDIVs
1            # of recursive panel fact.
1            RFACTs (0=left, 1=Crout, 2=Right)
1            # of broadcast
1            BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)
1            # of lookahead depth
1            DEPTHs (>=0)
2            SWAP (0=bin-exch,1=long,2=mix)
64           swapping threshold
0            L1 in (0=transposed,1=no-transposed) form
0            U  in (0=transposed,1=no-transposed) form
1            Equilibration (0=no,1=yes)
8            memory alignment in double (> 0)
EOF

# Run HPL with optimal binding for 2-socket system
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1

# Pure MPI approach (64 processes, 1 thread each)
mpirun -np 64 --map-by socket:PE=32 --bind-to core ./xhpl 2>&1 | tee hpl_results.log

# Or hybrid approach (32 MPI × 2 OpenBLAS threads)
# export OPENBLAS_NUM_THREADS=2
# mpirun -np 32 --map-by socket:PE=16 --bind-to core ./xhpl

📊 Step 6: Performance Tuning & Validation
bash

# Monitor during run (in separate terminal)
watch -n 1 'ps -eo psr,pcpu,cmd | grep xhpl | sort -n'

# Extract performance results
grep -A2 "WR00C2C2\|Gflops" hpl_results.log

# Calculate efficiency
# Expected peak: ~2.4 GHz × 64 cores × 16 DP FLOPS/cycle = ~2457 Gflops
# Your result ÷ 2457 = efficiency percentage

# Tune NB parameter
for NB in 128 192 224 256 384; do
    sed -i "s/^256          NBs/$NB          NBs/" HPL.dat
    echo "Testing NB=$NB"
    mpirun -np 64 ./xhpl 2>&1 | grep "Gflops"
done

🔧 Troubleshooting Table
Issue	Solution
Permission denied on directories	Add CD = cd to Makefile
mpicc not found	Run source ~/activate_custom_mpi.sh
Only 2 cores utilized	Ensure P×Q = total MPI processes
OpenBLAS conflicts	Use export OPENBLAS_NUM_THREADS=1
Memory errors	Reduce N in HPL.dat
Binding errors	Use --map-by socket:PE=32 --bind-to core
🎯 Quick Start Script

Save as setup_hpc_stack.sh:
bash

#!/bin/bash
# Complete HPC stack setup script
set -e

echo "1. Building OpenMPI..."
# [Insert OpenMPI build commands from Step 2]

echo "2. Setting up environment..."
# [Insert environment setup from Step 3]

echo "3. Building HPL..."
# [Insert HPL build from Step 4]

echo "4. Running benchmark..."
# [Insert run commands from Step 5]

echo "Done! Check hpl_results.log for performance metrics."



