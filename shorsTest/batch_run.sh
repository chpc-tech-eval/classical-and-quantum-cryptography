#!/bin/bash
# run_experiments.sh
# Run Shor's algorithm on multiple numbers to gather data for analysis

echo "======================================================================"
echo "SHOR'S ALGORITHM EXPERIMENTAL BATCH RUN"
echo "======================================================================"
echo ""

# Output files
CSV_FILE="shor_results.csv"
LOG_FILE="experiment_log.txt"

# Remove old results
if [ -f "$CSV_FILE" ]; then
    echo "Removing old results file: $CSV_FILE"
    rm "$CSV_FILE"
fi

echo "Running experiments..." | tee "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Test cases: various composite numbers
TEST_CASES=(
    "15"   # 3 × 5 (classic demo)
    "21"   # 3 × 7
    "33"   # 3 × 11
    "35"   # 5 × 7
    "51"   # 3 × 17
    "55"   # 5 × 11
    "77"   # 7 × 11
    "91"   # 7 × 13
    "143"  # 11 × 13
)

# Run each test case
for N in "${TEST_CASES[@]}"; do
    echo "----------------------------------------------------------------------" | tee -a "$LOG_FILE"
    echo "Testing N=$N (3 attempts with different parameters)" | tee -a "$LOG_FILE"
    echo "----------------------------------------------------------------------" | tee -a "$LOG_FILE"
    
    # Run with different shot counts
    python3 shor_generic.py --N $N --shots 1024 --max_attempts 1 2>&1 | tee -a "$LOG_FILE"
    python3 shor_generic.py --N $N --shots 2048 --max_attempts 1 2>&1 | tee -a "$LOG_FILE"
    python3 shor_generic.py --N $N --shots 4096 --max_attempts 1 2>&1 | tee -a "$LOG_FILE"
    
    echo "" | tee -a "$LOG_FILE"
done

echo "======================================================================"  | tee -a "$LOG_FILE"
echo "EXPERIMENTS COMPLETE" | tee -a "$LOG_FILE"
echo "======================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Analyzing results..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Run analysis
python3 analyze.py "$CSV_FILE" --graphs all

echo "" | tee -a "$LOG_FILE"
echo "Done! Check:"
echo "  - $CSV_FILE for raw data"
echo "  - plots/ for visualizations"
echo "  - shor_report.txt for summary"
