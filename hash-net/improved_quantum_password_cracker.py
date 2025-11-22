# improved_quantum_password_cracker.py
#!/usr/bin/env python3
"""
IMPROVED Quantum Password Cracker with better optimization methods
"""

import numpy as np
import time
import hashlib
import math
import itertools
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
from generate_training_data_with_hashes import ToyHasher

class ImprovedQuantumPasswordCracker:
    def __init__(self, hasher=None):
        self.hasher = hasher or ToyHasher()
        self.password_cache = {}
        
    def improved_brute_force(self, target_hash: str, max_length: int = 8, 
                           timeout: int = 30) -> Tuple[str, int, float]:
        """
        Improved brute force with better character set and early stopping
        """
        print(f"Starting improved brute force (max length: {max_length})")
        start_time = time.time()
        attempts = 0
        
        # More realistic character set (lowercase only for simple passwords)
        charset = "abcdefghijklmnopqrstuvwxyz"
        
        for length in range(1, max_length + 1):
            if time.time() - start_time > timeout:
                break
                
            for candidate in itertools.product(charset, repeat=length):
                if time.time() - start_time > timeout:
                    break
                    
                password = ''.join(candidate)
                attempts += 1
                
                if self.hasher.hash_to_hex(password) == target_hash:
                    elapsed = time.time() - start_time
                    return password, attempts, elapsed
        
        elapsed = time.time() - start_time
        return None, attempts, elapsed
    
    def improved_dictionary_attack(self, target_hash: str, 
                                 timeout: int = 30) -> Tuple[str, int, float]:
        """
        Improved dictionary attack with better wordlist and patterns
        """
        # Expanded wordlist
        wordlist = [
            "password", "admin", "hello", "secret", "test", "user", "login",
            "welcome", "123456", "letmein", "master", "qwerty", "abc123",
            "password1", "admin123", "hello123", "test123", "welcome1"
        ]
        
        print(f"Starting improved dictionary attack ({len(wordlist)} words)")
        start_time = time.time()
        attempts = 0
        
        # More realistic modifications
        suffixes = ['', '1', '12', '123', '1234', '!', '!!', '0', '00', '000']
        prefixes = ['', '!', '#', '$', '1', '12']
        
        for base_word in wordlist:
            if time.time() - start_time > timeout:
                break
                
            # Try the base word first
            attempts += 1
            if self.hasher.hash_to_hex(base_word) == target_hash:
                elapsed = time.time() - start_time
                return base_word, attempts, elapsed
            
            # Then try modifications
            for prefix in prefixes:
                for suffix in suffixes:
                    candidate = prefix + base_word + suffix
                    attempts += 1
                    
                    if self.hasher.hash_to_hex(candidate) == target_hash:
                        elapsed = time.time() - start_time
                        return candidate, attempts, elapsed
        
        elapsed = time.time() - start_time
        return None, attempts, elapsed
    
    def improved_genetic_algorithm(self, target_hash: str, population_size: int = 50,
                                 generations: int = 100, timeout: int = 30) -> Tuple[str, int, float]:
        """
        Vastly improved genetic algorithm with better fitness and operators
        """
        print(f"Starting improved genetic algorithm (pop: {population_size}, gens: {generations})")
        start_time = time.time()
        
        # Character set focused on common passwords
        charset = "abcdefghijklmnopqrstuvwxyz0123456789"
        attempts = 0
        
        def fitness(password):
            """Improved fitness function that rewards exact matches and close hashes"""
            if not password or len(password) < 4 or len(password) > 12:
                return -1000
                
            candidate_hash = self.hasher.hash_password(password)
            target_hash_int = int(target_hash, 16)
            
            # Hash difference (closer to 0 is better)
            hash_diff = abs(candidate_hash - target_hash_int)
            
            # Length bonus (prefer reasonable lengths)
            length_penalty = abs(len(password) - 8) * 1000
            
            # Base fitness
            base_fitness = -hash_diff - length_penalty
            
            # Exact match bonus
            if candidate_hash == target_hash_int:
                base_fitness += 1000000
                
            return base_fitness
        
        # Initialize population with common patterns
        population = []
        common_starts = ["pass", "admin", "hello", "test", "user", "secret"]
        common_ends = ["", "1", "123", "1234", "!", "0", "00"]
        
        for _ in range(population_size):
            if np.random.random() < 0.3 and common_starts:
                # Use common patterns
                base = np.random.choice(common_starts)
                if np.random.random() < 0.7:
                    base += np.random.choice(common_ends)
                password = base
            else:
                # Random password
                length = np.random.randint(4, 10)
                password = ''.join(np.random.choice(list(charset), length))
            population.append(password)
        
        best_fitness = -float('inf')
        best_password = None
        
        for generation in range(generations):
            if time.time() - start_time > timeout:
                break
                
            # Evaluate fitness
            fitness_scores = []
            for pwd in population:
                fitness_val = fitness(pwd)
                fitness_scores.append(fitness_val)
                attempts += 1
                
                # Check for solution
                if self.hasher.hash_to_hex(pwd) == target_hash:
                    elapsed = time.time() - start_time
                    return pwd, attempts, elapsed
                
                # Track best candidate
                if fitness_val > best_fitness:
                    best_fitness = fitness_val
                    best_password = pwd
            
            # Elitism: keep best candidate
            new_population = [population[np.argmax(fitness_scores)]]
            
            # Create new population
            while len(new_population) < population_size:
                # Tournament selection
                tournament_size = 3
                tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
                tournament_fitness = [fitness_scores[i] for i in tournament_indices]
                winner_idx = tournament_indices[np.argmax(tournament_fitness)]
                parent1 = population[winner_idx]
                
                # 70% crossover, 30% mutation
                if np.random.random() < 0.7 and len(new_population) < population_size - 1:
                    # Find second parent
                    tournament_indices2 = np.random.choice(len(population), tournament_size, replace=False)
                    tournament_fitness2 = [fitness_scores[i] for i in tournament_indices2]
                    winner_idx2 = tournament_indices2[np.argmax(tournament_fitness2)]
                    parent2 = population[winner_idx2]
                    
                    # Crossover
                    if len(parent1) > 1 and len(parent2) > 1:
                        cross_point1 = np.random.randint(1, len(parent1))
                        cross_point2 = np.random.randint(1, len(parent2))
                        child1 = parent1[:cross_point1] + parent2[cross_point2:]
                        child2 = parent2[:cross_point2] + parent1[cross_point1:]
                        
                        # Mutation
                        if np.random.random() < 0.3:
                            pos = np.random.randint(len(child1))
                            child1 = child1[:pos] + np.random.choice(list(charset)) + child1[pos+1:]
                        if np.random.random() < 0.3:
                            pos = np.random.randint(len(child2))
                            child2 = child2[:pos] + np.random.choice(list(charset)) + child2[pos+1:]
                        
                        new_population.extend([child1, child2])
                else:
                    # Mutation only
                    child = parent1
                    if np.random.random() < 0.5:
                        # Character mutation
                        pos = np.random.randint(len(child))
                        child = child[:pos] + np.random.choice(list(charset)) + child[pos+1:]
                    elif np.random.random() < 0.3:
                        # Add character
                        pos = np.random.randint(len(child) + 1)
                        child = child[:pos] + np.random.choice(list(charset)) + child[pos:]
                    elif len(child) > 4 and np.random.random() < 0.2:
                        # Remove character
                        pos = np.random.randint(len(child))
                        child = child[:pos] + child[pos+1:]
                    
                    new_population.append(child)
            
            population = new_population[:population_size]
        
        elapsed = time.time() - start_time
        
        # Return best candidate found
        if best_password and self.hasher.hash_to_hex(best_password) == target_hash:
            return best_password, attempts, elapsed
        else:
            return None, attempts, elapsed
    
    def improved_qaoa_approach(self, target_hash: str, max_iter: int = 200,
                             timeout: int = 30) -> Tuple[str, int, float]:
        """
        Improved approach using direct optimization on password characters
        """
        print(f"Starting improved QAOA approach")
        start_time = time.time()
        attempts = 0
        
        charset = "abcdefghijklmnopqrstuvwxyz0123456789"
        
        def evaluate_password(password):
            """Evaluate how close this password's hash is to target"""
            candidate_hash = self.hasher.hash_password(password)
            target_hash_int = int(target_hash, 16)
            return -abs(candidate_hash - target_hash_int)  # Negative because we maximize
        
        # Start with common passwords and mutate
        current_password = np.random.choice(["password", "admin", "hello", "test"])
        current_score = evaluate_password(current_password)
        attempts += 1
        
        if self.hasher.hash_to_hex(current_password) == target_hash:
            elapsed = time.time() - start_time
            return current_password, attempts, elapsed
        
        best_password = current_password
        best_score = current_score
        
        # Local search with restarts
        for iteration in range(max_iter):
            if time.time() - start_time > timeout:
                break
                
            # Mutate current password
            new_password = list(current_password)
            
            # Choose mutation type
            mutation_type = np.random.choice(['replace', 'insert', 'delete', 'swap'])
            
            if mutation_type == 'replace' and len(new_password) > 0:
                pos = np.random.randint(len(new_password))
                new_password[pos] = np.random.choice(list(charset))
            elif mutation_type == 'insert' and len(new_password) < 12:
                pos = np.random.randint(len(new_password) + 1)
                new_password.insert(pos, np.random.choice(list(charset)))
            elif mutation_type == 'delete' and len(new_password) > 4:
                pos = np.random.randint(len(new_password))
                new_password.pop(pos)
            elif mutation_type == 'swap' and len(new_password) >= 2:
                pos1, pos2 = np.random.choice(len(new_password), 2, replace=False)
                new_password[pos1], new_password[pos2] = new_password[pos2], new_password[pos1]
            
            new_password_str = ''.join(new_password)
            attempts += 1
            
            # Evaluate
            new_score = evaluate_password(new_password_str)
            
            # Accept if better, or sometimes accept worse (simulated annealing)
            if (new_score > current_score or 
                np.random.random() < np.exp((new_score - current_score) / (1.0 - iteration/max_iter))):
                current_password = new_password_str
                current_score = new_score
                
                if new_score > best_score:
                    best_password = new_password_str
                    best_score = new_score
            
            # Check for solution
            if self.hasher.hash_to_hex(current_password) == target_hash:
                elapsed = time.time() - start_time
                return current_password, attempts, elapsed
            
            # Random restart occasionally
            if iteration % 20 == 19:
                current_password = np.random.choice(["password", "admin", "hello", "test", "secret"])
                current_score = evaluate_password(current_password)
                attempts += 1
        
        elapsed = time.time() - start_time
        
        # Check best candidate
        if best_password and self.hasher.hash_to_hex(best_password) == target_hash:
            return best_password, attempts, elapsed
        else:
            return None, attempts, elapsed

def run_improved_test():
    """Test the improved methods"""
    print("🚀 IMPROVED PASSWORD CRACKER TEST")
    print("=" * 50)
    
    hasher = ToyHasher()
    cracker = ImprovedQuantumPasswordCracker(hasher)
    
    test_passwords = ["password", "admin", "hello", "test123", "secret"]
    
    for password in test_passwords:
        print(f"\n🎯 Cracking: '{password}'")
        target_hash = hasher.hash_to_hex(password)
        print(f"   Hash: {target_hash}")
        
        methods = [
            ("DICTIONARY", cracker.improved_dictionary_attack),
            ("GENETIC", lambda h: cracker.improved_genetic_algorithm(h, timeout=10)),
            ("QAOA", lambda h: cracker.improved_qaoa_approach(h, timeout=10)),
            ("BRUTE_FORCE", lambda h: cracker.improved_brute_force(h, timeout=10))
        ]
        
        for method_name, method_func in methods:
            print(f"   ⚡ {method_name:12}... ", end="", flush=True)
            
            start_time = time.time()
            try:
                result = method_func(target_hash)
                found_pwd, attempts, time_taken = result
                
                if found_pwd == password:
                    status = "✅ CRACKED"
                elif found_pwd:
                    status = "⚠️  WRONG"
                else:
                    status = "❌ FAILED"
                
                print(f"{status} | {time_taken:5.2f}s | {attempts:6} attempts")
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)[:20]}...")

if __name__ == "__main__":
    run_improved_test()
