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

# Function to generate one password:hash pair
generate_pair()
{
    # Password length 4–16
    LEN=$(( (RANDOM % 13) + 4 ))
    PASSWORD=$(tr -dc 'A-Za-z0-9\!\@\#\$\%\^\&\*\(\)\-\_\=\+\[\]\{\}' < /dev/urandom | head -c"$LEN")
    HASH=$(./Hash_Password.sh "$PASSWORD")
    printf "%s\n" "$HASH"
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