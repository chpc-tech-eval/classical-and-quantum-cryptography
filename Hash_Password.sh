#!/bin/bash

# Instructions
# ----------------------------------------
# DESCRIPTION:
#   This script computes a custom hash for a given password using a multi-accumulator prime-based algorithm.
#   The hash is printed as a 64-character hexadecimal string.
#
# USAGE:
#   ./HashPassword.sh "<password>"
#   <password> = the password to hash (quoted if it contains special characters)
#
# IMPORTANT:
#   If your password contains special characters (especially `!`, `$`, `&`, etc.), wrap it in single quotes:
#     ./HashPassword.sh 'MyP@ssw0rd!'
#   This prevents Bash from misinterpreting characters like `!` (used for history expansion).
#
# EXAMPLES:
#   ./HashPassword.sh 'Secure123!'
#       → Hashes the password and prints the result
#
# OUTPUT:
#   - Displays the original password and its hashed value.
#   - Hash is a fixed-length 64-character hexadecimal string.


# Custom Hash Function:
# ----------------------------------------
# 1. Convert each character of the password to its ASCII code.
# 2. Multiply by a sequence of prime numbers (to spread values).
# 3. Use modular arithmetic with a large prime to keep values bounded.
# 4. Mix results with XOR and addition to simulate diffusion.
# 5. Output as a fixed-length hex string.

PASSWORD=$1

# Validate input
if [[ -z "$PASSWORD" ]]; then
    echo "Error: No password provided."
    echo "Usage: $0 \"<password>\""
    exit 1
fi

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

HASH=$(hash_password "$PASSWORD")

printf "%-20s %s\n" "$PASSWORD:" "$HASH"

# echo "Password: $PASSWORD"
# echo "Hashed Password: $HASH"
