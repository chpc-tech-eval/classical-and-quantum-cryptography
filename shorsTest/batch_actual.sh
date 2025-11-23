#!/bin/bash
# batch_actual.sh
# Comprehensive batch testing for shor_actual.py
# Tests all valid numbers (10, 12, 14, 15) with all valid bases

echo "======================================================================"
echo "ACTUAL SHOR'S ALGORITHM - COMPREHENSIVE BATCH RUN"
echo "======================================================================"
echo ""

# Parse arguments
USE_IBM=false
SHOTS=4096
BACKEND=""
GPU=false
N_COUNT=""
SPECIFIC_N=""
SPECIFIC_A=""

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
        --N)
            SPECIFIC_N="$2"
            shift 2
            ;;
        --a)
            SPECIFIC_A="$2"
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
            echo "  --shots N           Number of shots (default: 4096)"
            echo "  --n_count N         Number of counting qubits (default: 12)"
            echo "  --N VALUE           Test only specific N (default: all)"
            echo "  --a VALUE           Test only specific base a (requires --N)"
            echo "  --gpu               Use GPU acceleration"
            echo ""
            echo "Examples:"
            echo "  ./batch_actual.sh                                    # CPU simulation, all tests"
            echo "  ./batch_actual.sh --gpu                              # GPU simulation"
            echo "  ./batch_actual.sh --shots 8192                       # Custom shots"
            echo "  ./batch_actual.sh --N 15                             # Only N=15, all bases"
            echo "  ./batch_actual.sh --N 15 --a 2                       # Only N=15, a=2"
            echo "  ./batch_actual.sh --N 15 --a 2 --shots 8192          # Custom everything"
            echo "  ./batch_actual.sh --use_ibm                          # Auto-select backend"
            echo "  ./batch_actual.sh --backend ibm_brisbane             # Use specific backend"
            echo "  ./batch_actual.sh --backend ibm_kyoto --shots 8192   # Custom backend + shots"
            exit 1
            ;;
    esac
done

# Validate --a requires --N
if [ -n "$SPECIFIC_A" ] && [ -z "$SPECIFIC_N" ]; then
    echo "[ERROR] --a requires --N to be specified"
    exit 1
fi

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
while [ -d "results/actual_${MODE}_${n}" ]; do
    n=$((n + 1))
done

# Create directories
RESULTS_DIR="results/actual_${MODE}_${n}"
CIRCUITS_DIR="$RESULTS_DIR/circuits"
mkdir -p "$RESULTS_DIR"
mkdir -p "$CIRCUITS_DIR"

echo "Created results directory: $RESULTS_DIR"
echo "Mode: $MODE_NAME"
echo ""

# Files
CSV_FILE="$RESULTS_DIR/results.csv"
LOG_FILE="$RESULTS_DIR/batch_log.txt"

# Test configuration (removed N=6)
declare -A TEST_CASES=(
    [10]="3 7 9"
    [12]="5 7 11"
    [14]="3 5 9 11 13"
    [15]="2 4 7 8 11 13"
)

# Filter test cases if --N or --a specified
if [ -n "$SPECIFIC_N" ]; then
    if [ -z "${TEST_CASES[$SPECIFIC_N]}" ]; then
        echo "[ERROR] Invalid N=$SPECIFIC_N. Valid values: ${!TEST_CASES[@]}"
        exit 1
    fi
    
    if [ -n "$SPECIFIC_A" ]; then
        # Check if a is valid for this N
        if [[ ! " ${TEST_CASES[$SPECIFIC_N]} " =~ " $SPECIFIC_A " ]]; then
            echo "[ERROR] Invalid a=$SPECIFIC_A for N=$SPECIFIC_N"
            echo "Valid bases for N=$SPECIFIC_N: ${TEST_CASES[$SPECIFIC_N]}"
            exit 1
        fi
        # Only test this specific (N, a) pair
        FILTERED_TESTS=( "$SPECIFIC_N:$SPECIFIC_A" )
    else
        # Test all bases for this N
        FILTERED_TESTS=()
        for a in ${TEST_CASES[$SPECIFIC_N]}; do
            FILTERED_TESTS+=( "$SPECIFIC_N:$a" )
        done
    fi
else
    # Test all (N, a) pairs
    FILTERED_TESTS=()
    for N in $(echo "${!TEST_CASES[@]}" | tr ' ' '\n' | sort -n); do
        for a in ${TEST_CASES[$N]}; do
            FILTERED_TESTS+=( "$N:$a" )
        done
    done
fi

TOTAL_TESTS=${#FILTERED_TESTS[@]}

# Build command flags
CMD_FLAGS="--shots $SHOTS --csv $CSV_FILE --circuits_dir $CIRCUITS_DIR"

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
echo "BATCH CONFIGURATION" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "Mode: $MODE_NAME" | tee -a "$LOG_FILE"
if [ -n "$BACKEND" ]; then
    echo "Backend: $BACKEND" | tee -a "$LOG_FILE"
fi
echo "Shots: $SHOTS" | tee -a "$LOG_FILE"
if [ -n "$N_COUNT" ]; then
    echo "Counting qubits: $N_COUNT" | tee -a "$LOG_FILE"
fi
if [ -n "$SPECIFIC_N" ]; then
    if [ -n "$SPECIFIC_A" ]; then
        echo "Testing: N=$SPECIFIC_N, a=$SPECIFIC_A" | tee -a "$LOG_FILE"
    else
        echo "Testing: N=$SPECIFIC_N (all bases)" | tee -a "$LOG_FILE"
    fi
else
    echo "Testing: All N values (all bases)" | tee -a "$LOG_FILE"
fi
echo "Total tests: $TOTAL_TESTS" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Run all tests
TEST_NUM=0
SUCCESSES=0
FAILURES=0

for test_pair in "${FILTERED_TESTS[@]}"; do
    ((TEST_NUM++))
    
    N="${test_pair%%:*}"
    a="${test_pair##*:}"
    
    echo "======================================================================" | tee -a "$LOG_FILE"
    echo "[TEST $TEST_NUM/$TOTAL_TESTS] N=$N, a=$a" | tee -a "$LOG_FILE"
    echo "======================================================================" | tee -a "$LOG_FILE"
    
    START=$(date +%s)
    
    python3 shor_actual.py --N $N --a $a $CMD_FLAGS 2>&1 | tee -a "$LOG_FILE"
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
    echo "Or check CSV for 'success=False' entries" | tee -a "$LOG_FILE"
fi