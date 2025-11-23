#!/bin/bash
# batch_parallel.sh
# Parallel execution of Shor's algorithm tests using GNU Parallel
# Optimized for multi-core systems (e.g., AMD EPYC 64-core)

set -e

echo "======================================================================"
echo "SHOR'S ALGORITHM - PARALLEL BATCH EXECUTION"
echo "======================================================================"
echo ""

# Check if GNU parallel is available
if ! command -v parallel &> /dev/null; then
    echo "[ERROR] GNU Parallel not found. Install with:"
    echo "  Ubuntu/Debian: sudo apt-get install parallel"
    echo "  RHEL/CentOS:   sudo yum install parallel"
    echo "  macOS:         brew install parallel"
    exit 1
fi

# Parse arguments
USE_GPU=false
USE_IBM=false
JOBS=$(nproc)  # Default to number of CPU cores
SHOTS=4096

while [[ $# -gt 0 ]]; do
    case $1 in
        --gpu)
            USE_GPU=true
            shift
            ;;
        --use_ibm)
            USE_IBM=true
            shift
            ;;
        --jobs|-j)
            JOBS="$2"
            shift 2
            ;;
        --shots)
            SHOTS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--gpu] [--use_ibm] [--jobs N] [--shots N]"
            exit 1
            ;;
    esac
done

# Validation
if [ "$USE_IBM" = true ] && [ "$JOBS" -gt 4 ]; then
    echo "[WARNING] Running many parallel quantum jobs may hit IBM rate limits"
    echo "[WARNING] Reducing parallel jobs to 4 for IBM Quantum"
    JOBS=4
fi

# Find next available results folder
n=1
while [ -d "results_parallel_${n}" ]; do
    n=$((n + 1))
done

RESULTS_DIR="results_parallel_${n}"
CIRCUITS_DIR="$RESULTS_DIR/circuits"
mkdir -p "$RESULTS_DIR"
mkdir -p "$CIRCUITS_DIR"

echo "Results directory: $RESULTS_DIR"
echo "Circuits directory: $CIRCUITS_DIR"
echo ""

# Determine mode
if [ "$USE_IBM" = true ]; then
    MODE="QUANTUM"
    IBM_FLAG="--use_ibm"
else
    MODE="SIMULATION"
    IBM_FLAG=""
fi

GPU_FLAG=""
if [ "$USE_GPU" = true ]; then
    GPU_FLAG="--gpu"
fi

# CSV files
GENERIC_CSV="$RESULTS_DIR/generic_results.csv"
ACTUAL_CSV="$RESULTS_DIR/actual_results.csv"
LOG_FILE="$RESULTS_DIR/parallel_log.txt"

echo "======================================================================" | tee "$LOG_FILE"
echo "PARALLEL BATCH CONFIGURATION" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "Mode: $MODE" | tee -a "$LOG_FILE"
echo "Parallel jobs: $JOBS" | tee -a "$LOG_FILE"
echo "CPU cores available: $(nproc)" | tee -a "$LOG_FILE"
echo "Shots per test: $SHOTS" | tee -a "$LOG_FILE"
if [ "$USE_GPU" = true ]; then
    echo "GPU acceleration: ENABLED" | tee -a "$LOG_FILE"
else
    echo "GPU acceleration: DISABLED" | tee -a "$LOG_FILE"
fi
echo "Generic CSV: $GENERIC_CSV" | tee -a "$LOG_FILE"
echo "Actual CSV: $ACTUAL_CSV" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# =============================================================================
# PART 1: GENERIC IMPLEMENTATION
# =============================================================================
echo "======================================================================" | tee -a "$LOG_FILE"
echo "PART 1: GENERIC SHOR'S ALGORITHM (PARALLEL)" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Test cases for generic
GENERIC_TESTS=(15 21 33 35 51 55 77 91)

echo "Running ${#GENERIC_TESTS[@]} generic tests in parallel (max $JOBS jobs)..." | tee -a "$LOG_FILE"
START_TIME=$(date +%s)

# Use GNU Parallel to run tests
parallel --jobs $JOBS --line-buffer \
    "python3 shor_generic.py --N {} --shots $SHOTS --max_attempts 1 \
    --csv $GENERIC_CSV --circuits_dir $CIRCUITS_DIR $IBM_FLAG $GPU_FLAG 2>&1 | \
    sed 's/^/[N={}] /'" ::: "${GENERIC_TESTS[@]}" | tee -a "$LOG_FILE"

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo "" | tee -a "$LOG_FILE"
echo "Generic tests completed in ${ELAPSED}s" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# =============================================================================
# PART 2: ACTUAL IMPLEMENTATION
# =============================================================================
echo "======================================================================" | tee -a "$LOG_FILE"
echo "PART 2: ACTUAL SHOR'S ALGORITHM (PARALLEL)" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Generate all N,a combinations for actual tests
ACTUAL_TESTS=()
ACTUAL_TESTS+=("6 5")
ACTUAL_TESTS+=("10 3" "10 7" "10 9")
ACTUAL_TESTS+=("12 5" "12 7" "12 11")
ACTUAL_TESTS+=("14 3" "14 5" "14 9" "14 11" "14 13")
ACTUAL_TESTS+=("15 2" "15 4" "15 7" "15 8" "15 11" "15 13")

echo "Running ${#ACTUAL_TESTS[@]} actual tests in parallel (max $JOBS jobs)..." | tee -a "$LOG_FILE"
START_TIME=$(date +%s)

# Run actual tests in parallel
printf '%s\n' "${ACTUAL_TESTS[@]}" | \
parallel --jobs $JOBS --line-buffer --colsep ' ' \
    "python3 shor_actual.py --N {1} --a {2} --shots $SHOTS \
    --csv $ACTUAL_CSV --circuits_dir $CIRCUITS_DIR $IBM_FLAG $GPU_FLAG 2>&1 | \
    sed 's/^/[N={1},a={2}] /'" | tee -a "$LOG_FILE"

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo "" | tee -a "$LOG_FILE"
echo "Actual tests completed in ${ELAPSED}s" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# =============================================================================
# SUMMARY
# =============================================================================
echo "======================================================================" | tee -a "$LOG_FILE"
echo "PARALLEL BATCH COMPLETE" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Count results
GENERIC_COUNT=$(tail -n +2 "$GENERIC_CSV" 2>/dev/null | wc -l || echo "0")
ACTUAL_COUNT=$(tail -n +2 "$ACTUAL_CSV" 2>/dev/null | wc -l || echo "0")

echo "Results:" | tee -a "$LOG_FILE"
echo "  Generic tests: $GENERIC_COUNT" | tee -a "$LOG_FILE"
echo "  Actual tests: $ACTUAL_COUNT" | tee -a "$LOG_FILE"
echo "  Total: $((GENERIC_COUNT + ACTUAL_COUNT))" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "📊 CSV FILES:" | tee -a "$LOG_FILE"
echo "  - $GENERIC_CSV" | tee -a "$LOG_FILE"
echo "  - $ACTUAL_CSV" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "🔬 CIRCUITS:" | tee -a "$LOG_FILE"
echo "  - $CIRCUITS_DIR/" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "📝 LOG:" | tee -a "$LOG_FILE"
echo "  - $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "✅ DONE!" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
