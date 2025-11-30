#!/bin/bash

# HPCG Benchmark Automation Script - Simplified and Robust
set -e

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
WORK_DIR="$PWD"
HPCG_DIR="$WORK_DIR/hpcg"
RESULTS_DIR="$WORK_DIR/hpcg_results_$TIMESTAMP"
LOG_FILE="$RESULTS_DIR/benchmark.log"

# Problem sizes (adjust based on your RAM)
PROBLEM_SIZES=("64 64 64" "104 104 104")
RUNTIME=120  # seconds

# Initialize
init() {
    echo "=== HPCG Benchmark Setup ==="
    mkdir -p "$RESULTS_DIR"
    echo "Results: $RESULTS_DIR"
    echo "Log: $LOG_FILE"
    
    # Record basic system info
    echo "System: $(uname -a)" > "$RESULTS_DIR/system_info.txt"
    echo "CPU: $(grep "model name" /proc/cpuinfo | head -1)" >> "$RESULTS_DIR/system_info.txt"
    echo "Cores: $(nproc)" >> "$RESULTS_DIR/system_info.txt"
    echo "Memory: $(free -h | grep Mem)" >> "$RESULTS_DIR/system_info.txt"
}

# Install dependencies
install_deps() {
    echo "Installing dependencies..."
    sudo apt update && \
    sudo apt install -y \
        build-essential \
        gcc g++ gfortran \
        openmpi-bin libopenmpi-dev \
        mpich \
        libopenblas-dev \
        wget git cmake \
        >> "$LOG_FILE" 2>&1
}

# Download HPCG
get_hpcg() {
    echo "Downloading HPCG..."
    if [ ! -d "$HPCG_DIR" ]; then
        git clone https://github.com/hpcg-benchmark/hpcg.git >> "$LOG_FILE" 2>&1
    else
        echo "HPCG already exists, updating..."
        cd "$HPCG_DIR" && git pull >> "$LOG_FILE" 2>&1 && cd "$WORK_DIR"
    fi
}

# Build HPCG
build_hpcg() {
    local build_name=$1
    local build_dir="$HPCG_DIR/build_$build_name"
    
    echo "Building HPCG ($build_name)..."
    
    cd "$HPCG_DIR"
    rm -rf "$build_dir"
    mkdir -p "$build_dir"
    cd "$build_dir"
    
    # Simple build approach
    if [ -f "../configure" ]; then
        ../configure Linux_MPI >> "$LOG_FILE" 2>&1
    else
        cp ../setup/Make.Linux_MPI .
        cp Make.Linux_MPI Makefile
    fi
    
    make -j$(nproc) >> "$LOG_FILE" 2>&1
    
    if [ ! -f "bin/xhpcg" ]; then
        echo "ERROR: Build failed - no xhpcg executable"
        return 1
    fi
    
    echo "Build successful: $build_dir/bin/xhpcg"
    cd "$WORK_DIR"
}

# Run benchmark
run_benchmark() {
    local build_name=$1
    local problem_size=$2
    local mpi_procs=$3
    
    local build_dir="$HPCG_DIR/build_$build_name"
    local size_label=$(echo "$problem_size" | tr ' ' 'x')
    local test_name="${build_name}_${mpi_procs}proc_${size_label}"
    
    echo "Running: $test_name"
    
    cd "$build_dir"
    
    # Create input file
    cat > "hpcg_$test_name.dat" << EOF
HPCG benchmark input file
Sandia National Laboratories; University of Tennessee, Knoxville
$problem_size
$RUNTIME
EOF
    
    cp "hpcg_$test_name.dat" hpcg.dat
    
    # Run benchmark
    if [ "$mpi_procs" -eq 1 ]; then
        ./bin/xhpcg > "$RESULTS_DIR/${test_name}.out" 2>&1
    else
        mpirun -np "$mpi_procs" --oversubscribe ./bin/xhpcg > "$RESULTS_DIR/${test_name}.out" 2>&1
    fi
    
    # Collect results
    local result_file=$(ls -t HPCG-Benchmark_*.txt 2>/dev/null | head -1)
    if [ -n "$result_file" ]; then
        cp "$result_file" "$RESULTS_DIR/${test_name}_results.txt"
        
        # Extract performance
        local gflops=$(grep "GFLOP/s rating" "$result_file" 2>/dev/null | awk -F'=' '{print $2}' | tr -d ' ' || echo "N/A")
        local valid=$(grep "HPCG result is" "$result_file" 2>/dev/null | grep -o "VALID" || echo "INVALID")
        
        echo "$test_name | $gflops GFLOP/s | $valid" >> "$RESULTS_DIR/summary.txt"
        echo "  Result: $gflops GFLOP/s ($valid)"
    else
        echo "  No results file found"
    fi
    
    cd "$WORK_DIR"
}

# Main execution
main() {
    echo "Starting HPCG Benchmark Automation"
    
    init
    install_deps
    get_hpcg
    
    # Build with GCC
    build_hpcg "gcc"
    
    # Test different configurations
    for size in "${PROBLEM_SIZES[@]}"; do
        # Single process
        run_benchmark "gcc" "$size" 1
        
        # MPI tests (adjust based on your cores)
        local cores=$(nproc)
        if [ "$cores" -ge 2 ]; then
            run_benchmark "gcc" "$size" 2
        fi
        if [ "$cores" -ge 4 ]; then
            run_benchmark "gcc" "$size" 4  
        fi
    done
    
    # Create final report
    echo "=== Benchmark Complete ==="
    echo "Results summary:"
    cat "$RESULTS_DIR/summary.txt" 2>/dev/null || echo "No results collected"
    echo ""
    echo "Full results in: $RESULTS_DIR"
    echo "Check *.txt files for detailed results"
}

# Run main
main "$@"