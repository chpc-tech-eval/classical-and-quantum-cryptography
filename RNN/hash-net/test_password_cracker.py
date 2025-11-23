# simple_test.py
#!/usr/bin/env python3
"""
Simple test that should work
"""

from quantum_password_cracker import QuantumPasswordCracker
from generate_training_data_with_hashes import ToyHasher

def test_basic():
    print(" Basic Password Cracking Test")
    print("=" * 40)
    
    hasher = ToyHasher()
    cracker = QuantumPasswordCracker(hasher)
    
    # Test password
    password = "password"
    target_hash = hasher.hash_to_hex(password)
    
    print(f"Password: '{password}'")
    print(f"Hash: {target_hash}")
    print()
    
    # Test dictionary attack (should work)
    print(" Testing dictionary attack...")
    wordlist = ["password", "admin", "test", "hello"]
    result = cracker.classical_dictionary_attack(target_hash, wordlist, timeout=10)
    
    found_pwd, attempts, time_taken = result
    
    if found_pwd == password:
        print(f" SUCCESS! Found: '{found_pwd}'")
    else:
        print(f" Failed. Found: '{found_pwd}'")
    
    print(f"Time: {time_taken:.2f}s")
    print(f"Attempts: {attempts}")

if __name__ == "__main__":
    test_basic()
