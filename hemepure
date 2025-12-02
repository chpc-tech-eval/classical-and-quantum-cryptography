# 1. Install System Dependencies (Ubuntu 24)
Run this first on all nodes (or at least the build/login node):

code:
sudo apt update
sudo apt install -y \
    build-essential cmake git g++ gcc \
    openmpi-bin libopenmpi-dev \
    libboost-all-dev \
    libtinyxml2-dev \
    zlib1g-dev \
    libtbb-dev \
    python3 python3-pip \
    libcppunit-dev \
    libctemplate-dev \
    libxml2-dev


# 2. Clone HemePure

code:
cd ~
git clone https://github.com/UCL-CCS/HemePure.git
cd HemePure

# 3. Build GKlib, METIS, ParMETIS (Dependencies)
These are in dep/.

code:
cd dep
mkdir build
cd build
cmake ..

# Side note if errors show:
code:

# list prefixes (which external projects were configured)
ls -1

# find any .log or build output files created by ExternalProject
for p in *-prefix; do
  echo "=== $p ==="
  find "$p" -maxdepth 3 -type f -iname '*.log' -o -iname '*.txt' -o -iname '*.out' -print 2>/dev/null
done

Then to quickly peek at the last 200 lines of the most likely logs:
code:
# show tail of common logs (try these)
tail -n 200 ALL-prefix/*.log 2>/dev/null || true
tail -n 200 ParMETIS-prefix/*.log 2>/dev/null || true
tail -n 200 TinyXML-prefix/*.log 2>/dev/null || true
tail -n 200 TIRPC-prefix/*.log 2>/dev/null || true

# Install libtirpc system package (recommended)

code:
sudo apt update
sudo apt install -y libtirpc-dev libtirpc3 pkg-config
sudo apt install -y build-essential cmake git wget

Then re-run cmake & make:

code:

cmake ..
make -j$(nproc)

# After make succeeds
You should see install files / built libs under the *-prefix directories or an install folder. Then proceed to the HemePure source build:

code:
cd ~/HemePure/src
mkdir -p build
cd build
cmake .. \
  -DHEMELB_USE_GMYPLUS=OFF \
  -DHEMELB_USE_MPI_WIN=OFF \
  -DHEMELB_USE_SSE3=ON \
  -DHEMELB_USE_AVX2=ON \
  -DCMAKE_C_COMPILER=mpicc \
  -DCMAKE_CXX_COMPILER=mpicxx

make -j$(nproc)

# TL;DR / What to run now
Copy–paste these three commands (they will either finish the build or give useful errors we can read):

code:
cd ~/HemePure/dep/build
sudo apt update && sudo apt install -y libtirpc-dev pkg-config
cmake ..
make -j$(nproc) 2>&1 | tee dep-build.log

After this, you should have:
dep/build/GKlib
dep/build/metis
dep/build/parmetis


# 4. Build HemePure (CPU version)
Create build directory:

code:
cd ~/HemePure/src
mkdir build
cd build

# Configure with CMake:
Recommended baseline flags (safe & works everywhere):

code:
cmake .. \
  -DHEMELB_USE_GMYPLUS=OFF \
  -DHEMELB_USE_MPI_WIN=OFF \
  -DHEMELB_USE_SSE3=ON \
  -DHEMELB_USE_AVX2=ON \
  -DCMAKE_C_COMPILER=mpicc \
  -DCMAKE_CXX_COMPILER=mpicxx


If your CPU supports AVX-512:
code:
-DHEMELB_USE_AVX512=ON

# Build:
code:
make -j$(nproc)

# After success, the binary will be:
~/HemePure/src/build/hemepure


# 5. Run the Bifurcation Benchmark

code: 
cd ~/HemePure/cases/bifurcation/bifurcation_hires
mpirun -np 4 ~/HemePure/src/build/hemepure -in input.xml -out results
