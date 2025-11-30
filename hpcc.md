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

3) Configure HPL

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
4) edit the path variable for the MPI C compiler to be recognized

```
which mpicc

# Temporarily append openmpi binary path to your PATH variable
# These settings will reset after you logout and re-login again.
export PATH=/usr/lib64/openmpi/bin:$PATH

# Rerun the which command to confirm that the `mpicc` binary is found
which mpicc
```
