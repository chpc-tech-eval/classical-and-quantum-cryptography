# performance_comparison.py
#!/usr/bin/env python3
"""
Compare original vs improved methods
"""

from quantum_password_cracker import QuantumPasswordCracker
from improved_quantum_password_cracker import ImprovedQuantumPasswordCracker
from generate_training_data_with_hashes import ToyHasher
import time

def compare_methods():
    print("🔍 PERFORMANCE COMPARISON: ORIGINAL vs IMPROVED")
    print("=" * 60)
    
    hasher = ToyHasher()
    original_cracker = QuantumPasswordCracker(hasher)
    improved_cracker = ImprovedQuantumPasswordCracker(hasher)
    
    test_cases = [
        ("password", "Easy"),
        ("admin", "Easy"), 
        ("hello123", "Medium"),
        ("test", "Easy")
    ]
    
    for password, difficulty in test_cases:
        print(f"\n🎯 {difficulty}: '{password}'")
        target_hash = hasher.hash_to_hex(password)
        
        # Test genetic algorithms
        print("   Genetic Algorithm:")
        start = time.time()
        orig_result = original_cracker.genetic_algorithm_attack(target_hash, timeout=5)
        orig_time = time.time() - start
        
        start = time.time()
        imp_result = improved_cracker.improved_genetic_algorithm(target_hash, timeout=5)
        imp_time = time.time() - start
        
        orig_success = orig_result[0] == password
        imp_success = imp_result[0] == password
        
        print(f"     Original: {'✅' if orig_success else '❌'} {orig_time:.2f}s")
        print(f"     Improved: {'✅' if imp_success else '❌'} {imp_time:.2f}s")
        
        # Test QAOA approaches
        print("   QAOA Approach:")
        start = time.time()
        orig_result = original_cracker.qaoa_optimize(target_hash, timeout=5)
        orig_time = time.time() - start
        
        start = time.time()
        imp_result = improved_cracker.improved_qaoa_approach(target_hash, timeout=5)
        imp_time = time.time() - start
        
        orig_success = orig_result[0] == password
        imp_success = imp_result[0] == password
        
        print(f"     Original: {'✅' if orig_success else '❌'} {orig_time:.2f}s")
        print(f"     Improved: {'✅' if imp_success else '❌'} {imp_time:.2f}s")

if __name__ == "__main__":
    compare_methods()

