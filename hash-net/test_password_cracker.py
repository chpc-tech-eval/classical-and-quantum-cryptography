# test_password_cracker.py
#!/usr/bin/env python3
"""
Simple test to hash "password" and try to crack it
"""

from quantum_password_cracker import QuantumPasswordCracker, ComparativeAnalyzer
from generate_training_data_with_hashes import ToyHasher

def test_single_password():
    print(" Testing Password Cracker with 'password'")
    print("=" * 50)
    
    # Initialize the hasher and cracker
    hasher = ToyHasher()
    cracker = QuantumPasswordCracker(hasher)
    
    # Hash the password "password"
    target_password = "password"
    target_hash = hasher.hash_to_hex(target_password)
    
    print(f"Target password: '{target_password}'")
    print(f"Target hash: {target_hash}")
    print("\n" + "=" * 50)
    
    # Try different methods to crack it
    methods = ["dictionary", "qaoa", "genetic", "brute_force"]
    
    for method in methods:
        print(f"\n Trying {method.upper()} method...")
        
        if method == "brute_force":
            result = cracker.classical_brute_force(
                target_hash, 
                charset="abcdefghijklmnopqrstuvwxyz",  # Only lowercase letters
                max_length=10,  # "password" has 8 characters
                timeout=10
            )
        elif method == "dictionary":
            # Common passwords list
            wordlist = ["password", "admin", "test", "user", "hello", "secret", "123456"]
            result = cracker.classical_dictionary_attack(target_hash, wordlist, timeout=10)
        elif method == "qaoa":
            result = cracker.qaoa_optimize(target_hash, num_qubits=24, max_iter=50, timeout=10)
        elif method == "genetic":
            result = cracker.genetic_algorithm_attack(target_hash, timeout=10)
        
        password_found, attempts, time_taken = result
        
        if password_found == target_password:
            status = " CRACKED!"
        elif password_found:
            status = "WRONG PASSWORD"
        else:
            status = " FAILED"
        
        print(f"   {status}")
        print(f"   Password found: '{password_found}'")
        print(f"   Time: {time_taken:.2f}s")
        print(f"   Attempts: {attempts}")

if __name__ == "__main__":
    test_single_password()
