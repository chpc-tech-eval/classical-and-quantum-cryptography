
## Expected Success Rates

| Condition | Success Rate |
|-----------|-------------|
| Single attempt | 50-67% |
| 2 attempts | 75-89% |
| 3 attempts | 88-96% |
| 5 attempts | >97% |

## Scaling Laws

| Metric | Formula | Example (N=35) |
|--------|---------|----------------|
| Qubits | 3⌈log₂N⌉ | 18 |
| Depth | O(n²) | ~400-500 |
| Classical time | O(n³) | instant |
| Quantum time | O(n²) gates | polynomial |
| Simulation time | O(2^n) | exponential! |

## Red Flags 🚩

**Uniform distribution:**
- All measurements equally likely
- → Bug in modular exponentiation or QFT

**Single peak at zero:**
- Only measure 00000000
- → Initial state wrong or gates not applied

**Wrong period:**
- Quantum ≠ Classical period
- → Increase n_count or shots

**0% success rate:**
- Never finds factors
- → Major implementation bug

## Quick Validation

```bash
# Run experiment
python3 shor_generic_with_logging.py --N 21

# Validate results
python3 validate_results.py shor_results.csv
