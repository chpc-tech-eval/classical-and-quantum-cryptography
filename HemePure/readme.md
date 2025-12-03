
# HemePure Benchmark Submission

**Team:** `TuksByters`   
**Case:** `HemePure Benchmarks`  
**Submission Components:** Build scripts, compiled binary, 5000-step results, 100000-step reports, visualization screenshot

---

## 1. Introduction

This submission contains our work for the CHPC HemePure benchmarking challenge.

HemePure is a high-performance lattice-Boltzmann (LBM) solver originally developed at University College London (UCL) for simulating blood flow in complex vascular geometries. The solver is implemented in C++ and parallelized using MPI.

### This README Explains

- ✔ How HemePure was built
- ✔ The MPI environment used
- ✔ How the simulation was executed for 5000 and 100000 steps
- ✔ The visualization workflow
- ✔ The folder structure of the submission

---

## 2. System Environment & Dependencies

### 2.1 Compilers and MPI

We used the CHPC-provided toolchain:

| Tool | Implementation |
|------|----------------|
| **C Compiler** | `gcc` (GNU Compiler Collection) |
| **C++ Compiler** | `g++` |
| **MPI Implementation** | `OpenMPI` (CHPC module) |
| **CMake** | 3.x (CHPC default module) |

### 2.2 External Libraries

The following external dependencies were used:

- Boost
- TinyXML
- ZLib
- CTemplate
- CPPUnit

### 2.3 Bundled Libraries

These libraries were compiled through the HemePure build system:

- **GKlib**
- **METIS**
- **ParMETIS**

These libraries are required for:

- ✔ Domain decomposition
- ✔ Graph partitioning
- ✔ Mesh communication across MPI ranks

All dependencies were obtained through the HemePure repository or the recommended ParMETIS sources.

---

## 3. Building HemePure

We followed the official `FullBuild.sh` structure, performing a clean build using:
```bash
cd HemePure/src
FOLDER=build_PV
mkdir $FOLDER
cd $FOLDER

cmake -DCMAKE_C_COMPILER=${CC} \
      -DCMAKE_CXX_COMPILER=${CXX} \
      -DHEMELB_USE_GMYPLUS=OFF \
      -DHEMELB_USE_MPI_WIN=OFF \
      -DHEMELB_USE_SSE3=ON \
      -DHEMELB_USE_AVX2=ON ..
```

The build was completed using:
```bash
make -j$(nproc)
```

### Binary Location

The final compiled binary is located at:
```bash
HemePure/src/build_PV/hemepure
```

This binary is included in our submission.

---

## 4. Running the Bifurcation Benchmark

### 4.1 Input Case Directory
```
HemePure/examples/bifurcation/bifurcation_hires/
```

### 4.2 Input Parameters

Only one parameter was changed between runs:

- `<steps>` set to **5000** for initial benchmark + visualization
- `<steps>` set to **100000** for performance tuning

All other parameters remained unchanged.

---

## 5. Execution on CHPC Nodes

### 5.1 MPI Job Command

The solver was executed using:
```bash
mpirun -N <NUM_PROCESSES> ../../../src/build_PV/hemepure -in input.xml -out results_<TIMESTEPS>
```

Where:

- `<NUM_PROCESSES>` was varied to tune performance
- `results_5000/` contains the 5000-step simulation
- `results_100000/` contains the 100000-step optimized run

### 5.2 Output Files Delivered

For both runs, HemePure generated:

- `whole.dat`
- `inlet.dat`
- `report.txt`
- `report.xml`

**Note:**

- The **5000-step results** are submitted in full
- The **100000-step results** were too large to visualize (as instructed), so only the following are included:
  - `report_100000.txt`
  - `report_100000.xml`

---

## 6. Data Extraction and Visualization Workflow

### 6.1 Using hemeXtract

We converted the binary simulation data using:
```bash
chmod +x ../../hemeXtract
../../hemeXtract -X results_5000/whole.dat > readable-output_5000.txt
```

### 6.2 Processing for ParaView

The provided script was used:
```bash
chmod +x paraviewProcessing.sh
./paraviewProcessing.sh readable-output_5000.txt paraview_file_5000
```

This generates grouped timestep files:
```
paraview_file_5000-1.txt
paraview_file_5000-2.txt
...
```

### 6.3 Visualization (ParaView)

In ParaView:

1. **Open** → Group all `paraview_file_5000-*.txt` files

2. **Change field delimiter:**
   - comma → space

3. **Apply Table to Points filter**

4. **Set:**
   - X → `gridX`
   - Y → `gridY`
   - Z → `gridZ`

5. **Color by:**
   - `velZ`

6. **Play through all timesteps** → generate animation

7. **Save final screenshot** (included as `visualization.png`)

---

## 7. Optimized 100000-step Run

The input file was edited:
```xml
<steps units="lattice" value="100000"/>
```

This run was executed on the cluster with performance-tuned MPI parameters.

### Note

As instructed, **visualization was NOT attempted** on 100000-step output due to size constraints.

The following files are included:

- `report_100000.txt`
- `report_100000.xml`

---

## 8. Submission Folder Structure
```
HemePure_Submission/
│
├── README.md
├── build_scripts/
│   ├── FullBuild.sh
│   └── job_submission.sh
│
├── binary/
│   └── hemepure
│
├── results_5000/
│   ├── whole.dat
│   ├── inlet.dat
│   ├── report.txt
│   ├── report.xml
│   ├── readable-output_5000.txt
│   ├── paraview_file_5000-*.txt
│   └── visualization.png
│
└── results_100000/
    ├── report_100000.txt
    └── report_100000.xml
```

---

## 9. Final Notes

- ✔ The simulation was validated visually using ParaView
- ✔ MPI scalability was tested by varying process counts
- ✔ Binary, build files, and all requested outputs are included
- ✔ All work complies with the official competition requirements

---

## 10. Acknowledgements

I acknowledge the CHPC for providing compute resources and the organizers for structuring this benchmark challenge.
