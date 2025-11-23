#!/bin/bash
# batch_generic.sh
# Batch testing for shor_generic.py

echo "======================================================================"
echo "GENERIC SHOR'S ALGORITHM - BATCH RUN"
echo "======================================================================"
echo ""

# Parse arguments
USE_IBM=false
SHOTS=2048
BACKEND=""
GPU=false
N_COUNT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --use_ibm)
            USE_IBM=true
            shift
            ;;
        --backend)
            BACKEND="$2"
            USE_IBM=true
            shift 2
            ;;
        --shots)
            SHOTS="$2"
            shift 2
            ;;
        --n_count)
            N_COUNT="$2"
            shift 2
            ;;
        --gpu)
            GPU=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --use_ibm           Use IBM Quantum hardware"
            echo "  --backend NAME      Specific IBM backend (implies --use_ibm)"
            echo "  --shots N           Number of shots (default: 2048)"
            echo "  --n_count N         Number of counting qubits (default: auto)"
            echo "  --gpu               Use GPU acceleration"
            echo ""
            echo "Test cases: 6, 10, 12, 14, 15, 21"
            echo ""
            echo "Examples:"
            echo "  ./batch_generic.sh                                 # CPU simulation"
            echo "  ./batch_generic.sh --gpu                           # GPU simulation"
            echo "  ./batch_generic.sh --shots 4096                    # Custom shots"
            echo "  ./batch_generic.sh --shots 8192 --n_count 12       # Custom shots + qubits"
            echo "  ./batch_generic.sh --use_ibm                       # Quantum hardware"
            echo "  ./batch_generic.sh --backend ibm_brisbane          # Specific backend"
            exit 1
            ;;
    esac
done

# Determine mode and folder name
if [ "$USE_IBM" = true ]; then
    MODE="quantum"
    MODE_NAME="QUANTUM HARDWARE"
elif [ "$GPU" = true ]; then
    MODE="gpu"
    MODE_NAME="GPU SIMULATION"
else
    MODE="sim"
    MODE_NAME="CPU SIMULATION"
fi

# Find next available results folder
mkdir -p results
n=1
while [ -d "results/generic_${MODE}_${n}" ]; do
    n=$((n + 1))
done

# Create directories
RESULTS_DIR="results/generic_${MODE}_${n}"
CIRCUITS_DIR="$RESULTS_DIR/circuits"
mkdir -p "$RESULTS_DIR"
mkdir -p "$CIRCUITS_DIR"

echo "Created results directory: $RESULTS_DIR"
echo "Mode: $MODE_NAME"
echo ""

# Files
CSV_FILE="$RESULTS_DIR/results.csv"
LOG_FILE="$RESULTS_DIR/batch_log.txt"

# Test cases: 6 (lower), 10, 12, 14, 15 (overlap with actual), 21 (higher)
GENERIC_TEST_CASES=(6 10 12 14 15 21)

# Build command flags
CMD_FLAGS="--shots $SHOTS --max_attempts 1 --csv $CSV_FILE --circuits_dir $CIRCUITS_DIR"

if [ -n "$N_COUNT" ]; then
    CMD_FLAGS="$CMD_FLAGS --n_count $N_COUNT"
fi

if [ "$USE_IBM" = true ]; then
    CMD_FLAGS="$CMD_FLAGS --use_ibm"
    if [ -n "$BACKEND" ]; then
        CMD_FLAGS="$CMD_FLAGS --backend $BACKEND"
    fi
elif [ "$GPU" = true ]; then
    CMD_FLAGS="$CMD_FLAGS --gpu"
fi

# Log configuration
echo "======================================================================" | tee "$LOG_FILE"
echo "GENERIC SHOR'S ALGORITHM - $MODE_NAME" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "Mode: $MODE_NAME" | tee -a "$LOG_FILE"
echo "Shots: $SHOTS" | tee -a "$LOG_FILE"
if [ -n "$N_COUNT" ]; then
    echo "Counting qubits: $N_COUNT" | tee -a "$LOG_FILE"
fi
if [ -n "$BACKEND" ]; then
    echo "Backend: $BACKEND" | tee -a "$LOG_FILE"
fi
echo "Test cases: ${GENERIC_TEST_CASES[@]}" | tee -a "$LOG_FILE"
echo "  • N=6  (lower bound)" | tee -a "$LOG_FILE"
echo "  • N=10, 12, 14, 15 (overlap with actual)" | tee -a "$LOG_FILE"
echo "  • N=21 (upper bound)" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Run tests
TEST_NUM=0
TOTAL_TESTS=${#GENERIC_TEST_CASES[@]}
SUCCESSES=0
FAILURES=0

for N in "${GENERIC_TEST_CASES[@]}"; do
    ((TEST_NUM++))
    
    echo "======================================================================" | tee -a "$LOG_FILE"
    echo "[TEST $TEST_NUM/$TOTAL_TESTS] N=$N" | tee -a "$LOG_FILE"
    echo "======================================================================" | tee -a "$LOG_FILE"
    
    START=$(date +%s)
    
    python3 shor_generic.py --N $N $CMD_FLAGS 2>&1 | tee -a "$LOG_FILE"
    EXIT_CODE=${PIPESTATUS[0]}
    
    if [ $EXIT_CODE -eq 0 ]; then
        ((SUCCESSES++))
        RESULT="✅ SUCCESS"
    else
        ((FAILURES++))
        RESULT="❌ FAILED"
    fi
    
    END=$(date +%s)
    ELAPSED=$((END - START))
    
    echo "" | tee -a "$LOG_FILE"
    echo "⏱️  Test time: ${ELAPSED}s - $RESULT" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
done

# Final summary
echo "======================================================================" | tee -a "$LOG_FILE"
echo "BATCH COMPLETE" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "Total tests: $TOTAL_TESTS" | tee -a "$LOG_FILE"
echo "✅ Successes: $SUCCESSES" | tee -a "$LOG_FILE"
echo "❌ Failures: $FAILURES" | tee -a "$LOG_FILE"
if [ $TOTAL_TESTS -gt 0 ]; then
    echo "Success rate: $(awk "BEGIN {printf \"%.1f\", ($SUCCESSES/$TOTAL_TESTS)*100}")%" | tee -a "$LOG_FILE"
fi
echo "" | tee -a "$LOG_FILE"
echo "Results saved to: $RESULTS_DIR/" | tee -a "$LOG_FILE"
echo "  📊 CSV: $CSV_FILE" | tee -a "$LOG_FILE"
echo "  🔬 Circuits: $CIRCUITS_DIR/" | tee -a "$LOG_FILE"
echo "  📝 Log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"

if [ $FAILURES -gt 0 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "⚠️  FAILED TESTS:" | tee -a "$LOG_FILE"
    echo "See log file for details: $LOG_FILE" | tee -a "$LOG_FILE"
fi