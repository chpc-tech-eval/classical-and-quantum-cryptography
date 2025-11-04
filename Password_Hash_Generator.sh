#!/bin/bash

# Instructions
# ----------------------------------------
# DESCRIPTION:
#   This script generates a specified number of random passwords (length 4–16 characters)
#   and computes a custom hash for each one. The results are written to a file in the format:
#
#       password:            hash
#
#   The colon stays tight to the password, and the hash is aligned neatly in a fixed column.
#
# USAGE:
#   ./BulkHashGenerator.sh <count>
#   <count> = number of password:hash pairs to generate (1 ≤ count ≤ 500000)
#
# EXAMPLES:
#   ./BulkHashGenerator.sh 100
#       → Generates 100 random password:hash pairs and saves them to password_hashes.txt
#
# OUTPUT:
#   - Results are saved to "password_hashes.txt" in the current directory.
#   - Each line contains a password and its hash, aligned for readability.
#   - At the end, the script prints the total runtime in seconds to the console.
#
# PERFORMANCE:
#   - Uses parallel execution across all CPU cores for speed.
#   - Suitable for generating up to ~500,000 entries without overwhelming the system.

# BulkHashGenerator.sh - Generate random passwords (length 4–16) and custom hashes in parallel
#
# Custom Hash Function:
# ----------------------------------------
# 1. Convert each character of the password to its ASCII code.
# 2. Multiply by a sequence of prime numbers (to spread values).
# 3. Use modular arithmetic with a large prime to keep values bounded.
# 4. Mix results with XOR and addition to simulate diffusion.
# 5. Output as a fixed-length hex string.

MAX=500000 # lets not overwhelm the system
COUNT=$1
OUTPUT_FILE="password_hashes.txt"
START=$(date +%s)

# Validate input
if [[ -z "$COUNT" || "$COUNT" -le 0 || "$COUNT" -gt $MAX ]]; then
    echo "Usage: $0 <count>   (1 <= count <= $MAX)"
    exit 1
fi

# Clear output file
> "$OUTPUT_FILE"

# Custom hash function
hash_password()
{
    local input="$1"
    local primes=(31 37 41 43 47 53 59 61 67 71 73 79 83 89 97 101)
    local mod=4294967291   # 32-bit prime
    local h1=0
    local h2=0
    local h3=0
    local h4=0

    for (( i=0; i<${#input}; i++ )); do
        c=$(printf "%d" "'${input:$i:1}")
        p=${primes[$((i % ${#primes[@]}))]}

        # Mix into four accumulators differently
        h1=$(( (h1 + c * p) % mod ))
        h2=$(( (h2 * 131 + c) % mod ))
        h3=$(( (h3 + (c ^ p)) % mod ))
        h4=$(( (h4 * 16777619) ^ c ))

        # Extra diffusion
        h1=$(( h1 ^ (h2 >> 7) ))
        h2=$(( h2 ^ (h3 << 11) ))
        h3=$(( h3 ^ (h4 >> 13) ))
        h4=$(( h4 ^ (h1 << 5) ))
    done

    # Print as 64 hex chars (16 per accumulator)
    printf "%016x%016x%016x%016x" "$h1" "$h2" "$h3" "$h4"
}

# Function to generate one password:hash pair
generate_pair()
{
    # Password length 4–16
    LEN=$(( (RANDOM % 13) + 4 ))
    PASSWORD=$(tr -dc 'A-Za-z0-9!@#$%^&*()-_=+[]{}' < /dev/urandom | head -c"$LEN")
    HASH=$(hash_password "$PASSWORD")
    printf "%-20s %s\n" "$PASSWORD:" "$HASH"
}

export -f generate_pair
export -f hash_password

echo "Generating $COUNT password:hash pairs in parallel..."

# Start timer
START=$(date +%s)

# Parallel execution
seq "$COUNT" | xargs -n1 -P"$(nproc)" bash -c 'generate_pair' _ >> "$OUTPUT_FILE"

# End timer
END=$(date +%s)
DIFF=$((END - START))

echo "Finished! Results saved to $OUTPUT_FILE"
echo "Total runtime: ${DIFF} seconds"