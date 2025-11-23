#!/bin/bash
# batch_actual.sh
# Comprehensive batch testing for shor_actual.py
# Tests all valid numbers (6, 10, 12, 14, 15) with all valid bases

echo "======================================================================"
echo "ACTUAL SHOR'S ALGORITHM - COMPREHENSIVE BATCH RUN"
echo "======================================================================"
echo ""

# Parse arguments
USE_IBM=false
SHOTS=4096
CIRCUITS_DIR=""
BACKEND=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --use_ibm)
            USE_IBM=true
            shift
            ;;
        --backend)
            BACKEND="$2"
            USE_IBM=true  # Automatically enable IBM if backend specified
            shift 2
            ;;
        --shots)
            SHOTS="$2"
            shift 2
            ;;
        --circuits_dir)
            CIRCUITS_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--use_ibm] [--backend NAME] [--shots N] [--circuits_dir DIR]"
            echo ""
            echo "Options:"
            echo "  --use_ibm           Use IBM Quantum hardware"
            echo "  --backend NAME      Specific IBM backend (implies --use_ibm)"
            echo "  --shots N           Number of shots (default: 4096)"
            echo "  --circuits_dir DIR  Directory to save circuit PNGs"
            echo ""
            echo "Examples:"
            echo "  ./batch_actual.sh                                    # Simulation only"
            echo "  ./batch_actual.sh --use_ibm                          # Auto-select backend"
            echo "  ./batch_actual.sh --backend ibm_brisbane             # Use specific backend"
            echo "  ./batch_actual.sh --backend ibm_kyoto --shots 8192   # Custom backend + shots"
            exit 1
            ;;
    esac
done

# Find next available results folder
n=1
while [ -d "results_actual_${n}" ]; do
    n=$((n + 1))
done

# Create directories
RESULTS_DIR="results_actual_${n}"
mkdir -p "$RESULTS_DIR"

if [ -n "$CIRCUITS_DIR" ]; then
    CIRCUITS_DIR="$RESULTS_DIR/circuits"
    mkdir -p "$CIRCUITS_DIR"
    echo "Created circuits directory: $CIRCUITS_DIR"
fi

echo "Created results directory: $RESULTS_DIR"
echo ""

# Determine mode and CSV file
if [ "$USE_IBM" = true ]; then
    MODE="QUANTUM"
    CSV_FILE="$RESULTS_DIR/shor_actual_quantum_results.csv"
    IBM_FLAG="--use_ibm"
else
    MODE="SIMULATION"
    CSV_FILE="$RESULTS_DIR/shor_actual_results.csv"
    IBM_FLAG=""
fi

LOG_FILE="$RESULTS_DIR/batch_log.txt"

# Test configuration
declare -A TEST_CASES=(
    [10]="3 7 9"
    [12]="5 7 11"
    [14]="3 5 9 11 13"
    [15]="2 4 7 8 11 13"
)

# Count total tests
TOTAL_TESTS=0
for N in "${!TEST_CASES[@]}"; do
    for a in ${TEST_CASES[$N]}; do
        ((TOTAL_TESTS++))
    done
done

echo "======================================================================" | tee "$LOG_FILE"
echo "BATCH CONFIGURATION" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "Mode: $MODE" | tee -a "$LOG_FILE"
if [ -n "$BACKEND" ]; then
    echo "Backend: $BACKEND" | tee -a "$LOG_FILE"
fi
echo "Shots: $SHOTS" | tee -a "$LOG_FILE"
echo "Total tests: $TOTAL_TESTS" | tee -a "$LOG_FILE"
echo "Output CSV: $CSV_FILE" | tee -a "$LOG_FILE"
if [ -n "$CIRCUITS_DIR" ]; then
    echo "Circuits: $CIRCUITS_DIR/" | tee -a "$LOG_FILE"
fi
echo "======================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Build backend flag
BACKEND_FLAG=""
if [ -n "$BACKEND" ]; then
    BACKEND_FLAG="--backend $BACKEND"
fi

# Run all tests
TEST_NUM=0
SUCCESSES=0
FAILURES=0

for N in $(echo "${!TEST_CASES[@]}" | tr ' ' '\n' | sort -n); do
    for a in ${TEST_CASES[$N]}; do
        ((TEST_NUM++))
        
        echo "======================================================================" | tee -a "$LOG_FILE"
        echo "[TEST $TEST_NUM/$TOTAL_TESTS] N=$N, a=$a" | tee -a "$LOG_FILE"
        echo "======================================================================" | tee -a "$LOG_FILE"
        
        START=$(date +%s)
        
        # Build command
        CMD="python3 shor_actual.py --N $N --a $a --shots $SHOTS --csv $CSV_FILE"
        
        if [ "$USE_IBM" = true ]; then
            CMD="$CMD --use_ibm"
        fi
        
        if [ -n "$BACKEND" ]; then
            CMD="$CMD --backend $BACKEND"
        fi
        
        if [ -n "$CIRCUITS_DIR" ]; then
            CMD="$CMD --circuits_dir $CIRCUITS_DIR"
        fi
        
        # Run test and capture exit code BEFORE pipe
        $CMD 2>&1 | tee -a "$LOG_FILE"
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
if [ -n "$CIRCUITS_DIR" ]; then
    echo "  🔬 Circuits: $CIRCUITS_DIR/" | tee -a "$LOG_FILE"
fi
echo "  📝 Log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"

# Optional: List failed tests if any
if [ $FAILURES -gt 0 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "⚠️  FAILED TESTS:" | tee -a "$LOG_FILE"
    echo "See log file for details: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "Or check CSV for 'success=False' entries" | tee -a "$LOG_FILE"
fi

# Run validation
echo "" | tee -a "$LOG_FILE"
echo "Running validation checks..." | tee -a "$LOG_FILE"
python3 validate.py "$CSV_FILE" | tee -a "$LOG_FILE"
