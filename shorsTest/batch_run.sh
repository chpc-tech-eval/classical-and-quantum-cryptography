#!/bin/bash
# batch_run.sh
# Comprehensive run of BOTH generic and actual implementations
# Passes all arguments to both batch_generic.sh and batch_actual.sh

echo "======================================================================"
echo "SHOR'S ALGORITHM - COMPREHENSIVE BATCH RUN"
echo "======================================================================"
echo ""
echo "This will run BOTH generic and actual implementations with the"
echo "same parameters you provide."
echo ""

# Show usage if --help or -h
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "All options are passed to both batch_generic.sh and batch_actual.sh"
    echo ""
    echo "Common Options:"
    echo "  --use_ibm           Use IBM Quantum hardware"
    echo "  --backend NAME      Specific IBM backend (implies --use_ibm)"
    echo "  --shots N           Number of shots (default: 2048 generic, 4096 actual)"
    echo "  --n_count N         Number of counting qubits (default: auto)"
    echo "  --gpu               Use GPU acceleration"
    echo ""
    echo "Actual-only Options (ignored by generic):"
    echo "  --N VALUE           Test only specific N"
    echo "  --a VALUE           Test only specific base a (requires --N)"
    echo ""
    echo "Examples:"
    echo "  ./batch_run.sh                                 # CPU simulation, all tests"
    echo "  ./batch_run.sh --gpu                           # GPU simulation"
    echo "  ./batch_run.sh --shots 8192                    # Custom shots for both"
    echo "  ./batch_run.sh --shots 8192 --n_count 14       # Custom shots + qubits"
    echo "  ./batch_run.sh --use_ibm                       # Quantum, auto-select backend"
    echo "  ./batch_run.sh --backend ibm_brisbane          # Specific backend"
    echo ""
    echo "Note: --N and --a only affect batch_actual.sh (generic tests all N values)"
    exit 0
fi

# Store all arguments to pass through
ARGS="$@"

# Parse to show configuration (but don't consume args)
MODE="SIMULATION"
SHOTS=""
BACKEND=""
N_COUNT=""
SPECIFIC_N=""
SPECIFIC_A=""
GPU=""

for arg in "$@"; do
    case $arg in
        --use_ibm)
            MODE="QUANTUM"
            ;;
        --gpu)
            GPU="✓"
            MODE="GPU SIMULATION"
            ;;
        --backend)
            MODE="QUANTUM"
            ;;
    esac
done

# Extract values for display (optional, just for logging)
while [[ $# -gt 0 ]]; do
    case $1 in
        --shots)
            SHOTS="$2"
            shift 2
            ;;
        --backend)
            BACKEND="$2"
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
        *)
            shift
            ;;
    esac
done

# Display configuration
echo "Configuration:"
echo "  Mode: $MODE"
if [ -n "$BACKEND" ]; then
    echo "  Backend: $BACKEND"
fi
if [ -n "$SHOTS" ]; then
    echo "  Shots: $SHOTS"
fi
if [ -n "$N_COUNT" ]; then
    echo "  Counting qubits: $N_COUNT"
fi
if [ -n "$GPU" ]; then
    echo "  GPU: Enabled"
fi
if [ -n "$SPECIFIC_N" ]; then
    echo "  Actual tests: N=$SPECIFIC_N"
    if [ -n "$SPECIFIC_A" ]; then
        echo "               a=$SPECIFIC_A"
    fi
fi
echo ""
echo "======================================================================"
echo ""

# Confirmation prompt for quantum hardware
if [[ "$MODE" == "QUANTUM" ]]; then
    echo "⚠️  WARNING: You are about to use REAL QUANTUM HARDWARE"
    echo "This will consume quantum computing time from your allocation."
    echo ""
    read -p "Continue? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "Aborted."
        exit 0
    fi
    echo ""
fi

# Run generic implementation
echo "======================================================================"
echo "PART 1: GENERIC IMPLEMENTATION"
echo "======================================================================"
echo ""
./batch_generic.sh $ARGS

GENERIC_EXIT=$?

echo ""
echo ""
echo "======================================================================"
echo "PART 2: ACTUAL IMPLEMENTATION"
echo "======================================================================"
echo ""
./batch_actual.sh $ARGS

ACTUAL_EXIT=$?

# Final summary
echo ""
echo ""
echo "======================================================================"
echo "✅ ALL BATCH RUNS COMPLETE"
echo "======================================================================"
echo ""
echo "Status:"
if [ $GENERIC_EXIT -eq 0 ]; then
    echo "  ✅ Generic: SUCCESS"
else
    echo "  ❌ Generic: FAILED (exit code: $GENERIC_EXIT)"
fi

if [ $ACTUAL_EXIT -eq 0 ]; then
    echo "  ✅ Actual: SUCCESS"
else
    echo "  ❌ Actual: FAILED (exit code: $ACTUAL_EXIT)"
fi

echo ""
echo "Results are in the results/ directory:"
echo "  results/generic_*/"
echo "  results/actual_*/"
echo ""

# Exit with error if either failed
if [ $GENERIC_EXIT -ne 0 ] || [ $ACTUAL_EXIT -ne 0 ]; then
    exit 1
fi