#!/bin/bash

# Instructions
# ----------------------------------------
# DESCRIPTION:
#   This script generates a specified number of random passwords (length 4–16 characters)
#   and computes a custom hash for each one. The results are written to a file in the format:
#
#       password
#           hash_function_used:            hash
#
#   The colon stays tight to the hash_function_used, and the hash is aligned neatly in a fixed column.
#
# USAGE:
#   ./Actual_Password_Hash_Generator.sh <count>
#   <count> = number of passwords to generate (1 ≤ count ≤ 500000)
#   Each password is hashed using a multiple hashing algorithms.
#
# EXAMPLES:
#   ./Actual_Password_Hash_Generator.sh 100
#       → Generates 100 random passwords, hashes each password with each hashing function and saves them to actual_password_hashes.txt
#
# OUTPUT:
#   - Results are saved to "actual_password_hashes.txt" in the current directory.
#   - Each line contains a password and its hash's, aligned for readability.
#   - At the end, the script prints the total runtime in seconds to the console.
#
# PERFORMANCE:
#   - Uses parallel execution across all CPU cores for speed.
#   - Suitable for generating up to ~500,000 entries without overwhelming the system.

# Actual_Password_Hash_Generator.sh - Generate random passwords (length 4–16) and custom hashes in parallel


MAX=500000 # lets not overwhelm the system
COUNT=$1
OUTPUT_FILE="actual_password_hashes.txt"
START=$(date +%s)

# Validate input
if [[ -z "$COUNT" || "$COUNT" -le 0 || "$COUNT" -gt $MAX ]]; then
    echo "Usage: $0 <count>   (1 <= count <= $MAX)"
    exit 1
fi

# Clear output file
> "$OUTPUT_FILE"

# Function to generate one password and hashes it
generate_pair()
{
    LEN=$(( (RANDOM % 13) + 4 ))
    PASSWORD=$(tr -dc 'A-Za-z0-9\!\@\#\$\%\^\&\*\(\)\-\_\=\+\[\]\{\}' < /dev/urandom | head -c"$LEN")

    # CUSTOM_HASH=$(./Hash_Password.sh "$PASSWORD")
    SHA1_HASH=$(echo -n "$PASSWORD" | sha1sum | awk '{print $1}')
    SHA3_HASH=$(echo -n "$PASSWORD" | openssl dgst -sha3-512 | awk '{print $2}')
    SHA256_HASH=$(echo -n "$PASSWORD" | sha256sum | awk '{print $1}')
    SHA512_HASH=$(echo -n "$PASSWORD" | sha512sum | awk '{print $1}')
    SHA512Q_HASH=$(echo -n "$PASSWORD" | openssl dgst -sha512 | awk '{print $2}') # Placeholder for "quantum"

    # printf "%-20s %s\n" "$PASSWORD:" "$CUSTOM_HASH"
    printf "%s\n" "$PASSWORD"
    printf "%-20s %s\n" "  SHA-1:" "$SHA1_HASH"
    printf "%-20s %s\n" "  SHA-3:" "$SHA3_HASH"
    printf "%-20s %s\n" "  SHA-256:" "$SHA256_HASH"
    printf "%-20s %s\n" "  SHA-512:" "$SHA512_HASH"
    printf "%-20s %s\n\n" "  SHA-512Q:" "$SHA512Q_HASH"
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