#!/bin/bash
# batch_run.sh
# Comprehensive run of BOTH generic and actual implementations

echo "======================================================================"
echo "SHOR'S ALGORITHM - COMPREHENSIVE BATCH RUN"
echo "======================================================================"
echo ""

# Parse arguments
USE_IBM=false
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
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--use_ibm] [--backend NAME]"
            echo ""
            echo "Options:"
            echo "  --use_ibm           Use IBM Quantum hardware"
            echo "  --backend NAME      Specific IBM backend (implies --use_ibm)"
            echo ""
            echo "Examples:"
            echo "  ./batch_run.sh                         # Simulation only"
            echo "  ./batch_run.sh --use_ibm               # Auto-select backend"
            echo "  ./batch_run.sh --backend ibm_brisbane  # Use specific backend"
            exit 1
            ;;
    esac
done

# Find next available results folder
n=1
while [ -d "results_combined_${n}" ]; do
    n=$((n + 1))
done

# Create the results directory
RESULTS_DIR="results_combined_${n}"
CIRCUITS_DIR="$RESULTS_DIR/circuits"
mkdir -p "$RESULTS_DIR"
mkdir -p "$CIRCUITS_DIR"

echo "Created results directory: $RESULTS_DIR"
echo "Created circuits directory: $CIRCUITS_DIR"
echo ""

LOG_FILE="$RESULTS_DIR/batch_log.txt"

# CSV files
GENERIC_SIM_CSV="$RESULTS_DIR/generic_sim.csv"
ACTUAL_SIM_CSV="$RESULTS_DIR/actual_sim.csv"

# Build backend flags
BACKEND_FLAG=""
if [ -n "$BACKEND" ]; then
    BACKEND_FLAG="--backend $BACKEND"
    echo "Using backend: $BACKEND" | tee "$LOG_FILE"
else
    echo "Running experiments..." | tee "$LOG_FILE"
fi
echo "" | tee -a "$LOG_FILE"

# =============================================================================
# PART 1: GENERIC IMPLEMENTATION (SIMULATION)
# =============================================================================
echo "======================================================================" | tee -a "$LOG_FILE"
echo "PART 1: GENERIC SHOR'S ALGORITHM - SIMULATION" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

GENERIC_TEST_CASES=(15 21 33 35)

for N in "${GENERIC_TEST_CASES[@]}"; do
    echo "[GENERIC-SIM] Testing N=$N" | tee -a "$LOG_FILE"
    echo "----------------------------------------------------------------------" | tee -a "$LOG_FILE"
    START=$(date +%s)
    
    python3 shor_generic.py --N $N --shots 2048 --max_attempts 1 \
        --csv "$GENERIC_SIM_CSV" \
        --circuits_dir "$CIRCUITS_DIR" 2>&1 | tee -a "$LOG_FILE"
    
    END=$(date +%s)
    ELAPSED=$((END - START))
    echo "⏱️  Time: ${ELAPSED}s" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
done

# =============================================================================
# PART 2: ACTUAL IMPLEMENTATION (SIMULATION) - All numbers, all bases
# =============================================================================
echo "======================================================================" | tee -a "$LOG_FILE"
echo "PART 2: ACTUAL SHOR'S ALGORITHM - SIMULATION (COMPREHENSIVE)" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Define test cases with all bases
declare -A ACTUAL_TESTS=(
    [6]="5"
    [10]="3 7 9"
    [12]="5 7 11"
    [14]="3 5 9 11 13"
    [15]="2 4 7 8 11 13"
)

ACTUAL_TEST_NUM=0
for N in 6 10 12 14 15; do
    for a in ${ACTUAL_TESTS[$N]}; do
        ((ACTUAL_TEST_NUM++))
        echo "[ACTUAL-SIM $ACTUAL_TEST_NUM] N=$N, a=$a" | tee -a "$LOG_FILE"
        echo "----------------------------------------------------------------------" | tee -a "$LOG_FILE"
        START=$(date +%s)
        
        python3 shor_actual.py --N $N --a $a --shots 4096 \
            --csv "$ACTUAL_SIM_CSV" \
            --circuits_dir "$CIRCUITS_DIR" 2>&1 | tee -a "$LOG_FILE"
        
        END=$(date +%s)
        ELAPSED=$((END - START))
        echo "⏱️  Time: ${ELAPSED}s" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
    done
done

# =============================================================================
# PART 3: QUANTUM TESTS (if credentials available and --use_ibm specified)
# =============================================================================
if [ -f "my_credentials.py" ]; then
    if [ "$USE_IBM" = true ]; then
        echo "======================================================================" | tee -a "$LOG_FILE"
        echo "⚡ QUANTUM HARDWARE TESTS" | tee -a "$LOG_FILE"
        echo "======================================================================" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        
        # Generic quantum tests
        echo "[GENERIC-QUANTUM] Starting tests..." | tee -a "$LOG_FILE"
        GENERIC_QUANTUM_CSV="$RESULTS_DIR/generic_quantum.csv"
        
        for N in "${GENERIC_TEST_CASES[@]}"; do
            echo "[GENERIC-QUANTUM] Testing N=$N" | tee -a "$LOG_FILE"
            echo "----------------------------------------------------------------------" | tee -a "$LOG_FILE"
            START=$(date +%s)
            
            python3 shor_generic.py --N $N --shots 2048 --max_attempts 1 \
                --csv "$GENERIC_QUANTUM_CSV" \
                --circuits_dir "$CIRCUITS_DIR" \
                --use_ibm $BACKEND_FLAG 2>&1 | tee -a "$LOG_FILE"
            
            END=$(date +%s)
            ELAPSED=$((END - START))
            echo "⏱️  Time: ${ELAPSED}s" | tee -a "$LOG_FILE"
            echo "" | tee -a "$LOG_FILE"
        done
        
        # Actual quantum tests
        echo "[ACTUAL-QUANTUM] Starting tests..." | tee -a "$LOG_FILE"
        ACTUAL_QUANTUM_CSV="$RESULTS_DIR/actual_quantum.csv"
        
        ACTUAL_TEST_NUM=0
        for N in 6 10 12 14 15; do
            for a in ${ACTUAL_TESTS[$N]}; do
                ((ACTUAL_TEST_NUM++))
                echo "[ACTUAL-QUANTUM $ACTUAL_TEST_NUM] N=$N, a=$a" | tee -a "$LOG_FILE"
                echo "----------------------------------------------------------------------" | tee -a "$LOG_FILE"
                START=$(date +%s)
                
                CMD="python3 shor_actual.py --N $N --a $a --shots 4096 \
                    --csv $ACTUAL_QUANTUM_CSV \
                    --circuits_dir $CIRCUITS_DIR \
                    --use_ibm $BACKEND_FLAG"
                
                if $CMD 2>&1 | tee -a "$LOG_FILE"; then
                    echo "✅ SUCCESS" | tee -a "$LOG_FILE"
                else
                    echo "❌ FAILED" | tee -a "$LOG_FILE"
                fi
                
                END=$(date +%s)
                ELAPSED=$((END - START))
                echo "⏱️  Time: ${ELAPSED}s" | tee -a "$LOG_FILE"
                echo "" | tee -a "$LOG_FILE"
            done
        done
    else
        echo "======================================================================" | tee -a "$LOG_FILE"
        echo "⚠️  QUANTUM HARDWARE TESTS AVAILABLE" | tee -a "$LOG_FILE"
        echo "======================================================================" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo "To run quantum tests, use:" | tee -a "$LOG_FILE"
        echo "  ./batch_run.sh --use_ibm" | tee -a "$LOG_FILE"
        echo "  ./batch_run.sh --backend ibm_brisbane" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo "⚠️  Quantum tests NOT run to conserve quantum time!" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
    fi
else
    echo "[INFO] No IBM credentials found. Quantum tests not available." | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
fi

# =============================================================================
# SUMMARY
# =============================================================================
echo "======================================================================" | tee -a "$LOG_FILE"
echo "BATCH COMPLETE" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Results saved to: $RESULTS_DIR/" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "📊 CSV FILES:" | tee -a "$LOG_FILE"
echo "  - $GENERIC_SIM_CSV" | tee -a "$LOG_FILE"
echo "  - $ACTUAL_SIM_CSV" | tee -a "$LOG_FILE"
if [ "$USE_IBM" = true ]; then
    echo "  - $GENERIC_QUANTUM_CSV" | tee -a "$LOG_FILE"
    echo "  - $ACTUAL_QUANTUM_CSV" | tee -a "$LOG_FILE"
fi
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
