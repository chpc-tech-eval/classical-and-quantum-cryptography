#!/bin/bash
# batch_run.sh
# Comprehensive run of BOTH generic and actual implementations

echo "======================================================================"
echo "SHOR'S ALGORITHM - COMPREHENSIVE BATCH RUN"
echo "======================================================================"
echo ""

# Parse arguments and pass them through
ARGS="$@"

echo "Running GENERIC implementation..."
echo "======================================================================"
./batch_generic.sh $ARGS

echo ""
echo ""
echo "Running ACTUAL implementation..."
echo "======================================================================"
./batch_actual.sh $ARGS

echo ""
echo ""
echo "======================================================================"
echo "✅ ALL BATCH RUNS COMPLETE"
echo "======================================================================"
echo ""
echo "Results are in the results/ directory:"
echo "  results/generic_*/"
echo "  results/actual_*/"
echo ""