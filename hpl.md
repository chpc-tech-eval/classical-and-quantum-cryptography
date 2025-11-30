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






