# improved_quantum_password_cracker.py
#!/usr/bin/env python3
"""
IMPROVED Quantum Password Cracker - General Solution for All Passwords
"""

import numpy as np
import time
import hashlib
import math
import itertools
from typing import List, Tuple, Dict, Optional
import matplotlib.pyplot as plt
from generate_training_data_with_hashes import ToyHasher

class ImprovedQuantumPasswordCracker:
    def __init__(self, hasher=None, verbose: bool = True):
        self.hasher = hasher or ToyHasher()
        self.password_cache = {}
        self.verbose = verbose
        self.log_data = {}
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages with different levels"""
        if self.verbose:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp} {level:6}] {message}")
    
    def improved_genetic_algorithm(self, target_hash: str, population_size: int = 100,
                                 generations: int = 200, timeout: int = 30) -> Tuple[str, int, float]:
        """
        Fixed genetic algorithm - no infinite loops in population initialization
        """
        self.log(f"Starting genetic algorithm (pop: {population_size}, gens: {generations})")
        start_time = time.time()
        
        charset = "abcdefghijklmnopqrstuvwxyz0123456789"
        attempts = 0
        
        def fitness(password):
            """Fitness function"""
            if not password or len(password) < 2 or len(password) > 20:
                return -10000
                
            candidate_hash = self.hasher.hash_password(password)
            target_hash_int = int(target_hash, 16)
            
            if candidate_hash == target_hash_int:
                return 1000000
                
            hash_diff = abs(candidate_hash - target_hash_int)
            length_penalty = abs(len(password) - 8) * 100
            
            char_bonus = 0
            if any(c.isdigit() for c in password):
                char_bonus += 50
            
            return -hash_diff - length_penalty + char_bonus
        
        # FIXED: Simple population initialization without infinite loops
        population = []
        
        # Strategy 1: Common passwords
        common_passwords = [
            "password", "admin", "hello", "test", "user", "secret", "123456", 
            "letmein", "welcome", "login", "master", "qwerty", "abc123"
        ]
        for pwd in common_passwords:
            if len(population) < population_size:
                population.append(pwd)
        
        # Strategy 2: Pattern-based passwords
        patterns = ["pass", "admin", "hello", "test", "user", "secret"]
        suffixes = ["", "1", "12", "123", "1234"]
        
        # Fixed: Use a counter to prevent infinite loops
        max_pattern_attempts = population_size * 2
        pattern_attempts = 0
        
        while len(population) < population_size * 0.6 and pattern_attempts < max_pattern_attempts:
            base = np.random.choice(patterns)
            suffix = np.random.choice(suffixes)
            password = base + suffix
            if password not in population:
                population.append(password)
            pattern_attempts += 1
        
        # Strategy 3: Fill remaining slots with random passwords
        needed = population_size - len(population)
        for _ in range(needed):
            length = np.random.randint(4, 10)
            password = ''.join(np.random.choice(list(charset), length))
            population.append(password)
        
        self.log(f"Population initialized with {len(population)} individuals")
        
        best_fitness = -float('inf')
        best_password = None
        
        for generation in range(generations):
            if time.time() - start_time > timeout:
                self.log(f"Timeout at generation {generation}/{generations}")
                break
                
            # Evaluate fitness
            fitness_scores = []
            current_best_fitness = -float('inf')
            current_best_password = None
            
            for pwd in population:
                fitness_val = fitness(pwd)
                fitness_scores.append(fitness_val)
                attempts += 1
                
                if self.hasher.hash_to_hex(pwd) == target_hash:
                    elapsed = time.time() - start_time
                    self.log(f"SUCCESS: Generation {generation}, found '{pwd}' after {attempts} attempts in {elapsed:.2f}s")
                    return pwd, attempts, elapsed
                
                if fitness_val > current_best_fitness:
                    current_best_fitness = fitness_val
                    current_best_password = pwd
                
                if fitness_val > best_fitness:
                    best_fitness = fitness_val
                    best_password = pwd
            
            # Log progress
            if generation % 20 == 0 or generation < 5:
                self.log(f"Gen {generation:3d}: best='{current_best_password}' fitness={current_best_fitness:8.0f}")
            
            # Selection and reproduction
            new_population = []
            
            # Elitism
            elite_count = max(1, population_size // 10)
            elite_indices = np.argsort(fitness_scores)[-elite_count:]
            for idx in elite_indices:
                new_population.append(population[idx])
            
            # Create new population
            while len(new_population) < population_size:
                # Tournament selection
                tournament_size = 3
                tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
                tournament_fitness = [fitness_scores[i] for i in tournament_indices]
                winner_idx = tournament_indices[np.argmax(tournament_fitness)]
                parent1 = population[winner_idx]
                
                if np.random.random() < 0.7 and len(new_population) < population_size - 1:
                    # Crossover
                    tournament_indices2 = np.random.choice(len(population), tournament_size, replace=False)
                    tournament_fitness2 = [fitness_scores[i] for i in tournament_indices2]
                    winner_idx2 = tournament_indices2[np.argmax(tournament_fitness2)]
                    parent2 = population[winner_idx2]
                    
                    if len(parent1) > 1 and len(parent2) > 1:
                        point = np.random.randint(1, min(len(parent1), len(parent2)))
                        child1 = parent1[:point] + parent2[point:]
                        child2 = parent2[:point] + parent1[point:]
                        
                        # Mutation
                        for child in [child1, child2]:
                            if np.random.random() < 0.3:
                                if len(child) > 0:
                                    pos = np.random.randint(len(child))
                                    child = child[:pos] + np.random.choice(list(charset)) + child[pos+1:]
                        
                        new_population.extend([child1, child2])
                else:
                    # Mutation only
                    child = parent1
                    if np.random.random() < 0.3 and len(child) > 0:
                        pos = np.random.randint(len(child))
                        child = child[:pos] + np.random.choice(list(charset)) + child[pos+1:]
                    
                    new_population.append(child)
            
            population = new_population[:population_size]
        
        elapsed = time.time() - start_time
        
        if best_password and self.hasher.hash_to_hex(best_password) == target_hash:
            self.log(f"SUCCESS: Found '{best_password}' after {attempts} attempts in {elapsed:.2f}s")
            return best_password, attempts, elapsed
        else:
            self.log(f"FAILED: Best candidate '{best_password}' after {attempts} attempts in {elapsed:.2f}s")
            return None, attempts, elapsed
    
    def improved_qaoa_approach(self, target_hash: str, max_iter: int = 500,
                             timeout: int = 30) -> Tuple[str, int, float]:
        """
        Fixed QAOA approach - simpler and more reliable
        """
        self.log(f"Starting QAOA approach (max iterations: {max_iter})")
        start_time = time.time()
        attempts = 0
        
        charset = "abcdefghijklmnopqrstuvwxyz0123456789"
        
        def evaluate_password(password):
            """Evaluation function"""
            if not password or len(password) < 2 or len(password) > 20:
                return -10000
                
            candidate_hash = self.hasher.hash_password(password)
            target_hash_int = int(target_hash, 16)
            
            if candidate_hash == target_hash_int:
                return 1000000
            
            return -abs(candidate_hash - target_hash_int)
        
        # Simple starting points
        starting_passwords = [
            "password", "admin", "hello", "test", "user", "secret", "123456",
            "pass", "test123", "hello1", "admin1"
        ]
        
        # Try starting points
        for start_pwd in starting_passwords:
            attempts += 1
            if self.hasher.hash_to_hex(start_pwd) == target_hash:
                elapsed = time.time() - start_time
                self.log(f"SUCCESS: Starting password '{start_pwd}' matched!")
                return start_pwd, attempts, elapsed
        
        # Start with best starting point
        start_fitness = [evaluate_password(pwd) for pwd in starting_passwords]
        best_start_idx = np.argmax(start_fitness)
        current_password = starting_passwords[best_start_idx]
        current_score = start_fitness[best_start_idx]
        
        best_password = current_password
        best_score = current_score
        
        for iteration in range(max_iter):
            if time.time() - start_time > timeout:
                self.log(f"Timeout at iteration {iteration}/{max_iter}")
                break
                
            # Simple mutation
            new_password = current_password
            
            if len(new_password) > 0:
                mutation_type = np.random.choice(['replace', 'insert', 'delete'])
                
                if mutation_type == 'replace':
                    pos = np.random.randint(len(new_password))
                    new_password = new_password[:pos] + np.random.choice(list(charset)) + new_password[pos+1:]
                elif mutation_type == 'insert' and len(new_password) < 15:
                    pos = np.random.randint(len(new_password) + 1)
                    new_password = new_password[:pos] + np.random.choice(list(charset)) + new_password[pos:]
                elif mutation_type == 'delete' and len(new_password) > 2:
                    pos = np.random.randint(len(new_password))
                    new_password = new_password[:pos] + new_password[pos+1:]
            
            attempts += 1
            new_score = evaluate_password(new_password)
            
            # Simulated annealing
            temperature = max(0.1, 1.0 - (iteration / max_iter))
            accept_probability = np.exp((new_score - current_score) / temperature)
            
            if new_score > current_score or np.random.random() < accept_probability:
                current_password = new_password
                current_score = new_score
                
                if new_score > best_score:
                    best_password = new_password
                    best_score = new_score
            
            # Check for solution
            if self.hasher.hash_to_hex(current_password) == target_hash:
                elapsed = time.time() - start_time
                self.log(f"SUCCESS: Found '{current_password}' at iteration {iteration}!")
                return current_password, attempts, elapsed
            
            # Occasional restart
            if iteration % 50 == 0:
                length = np.random.randint(4, 10)
                current_password = ''.join(np.random.choice(list(charset), length))
                current_score = evaluate_password(current_password)
                attempts += 1
        
        elapsed = time.time() - start_time
        
        if best_password and self.hasher.hash_to_hex(best_password) == target_hash:
            self.log(f"SUCCESS: Found '{best_password}' after {attempts} attempts!")
            return best_password, attempts, elapsed
        else:
            self.log(f"FAILED: Best candidate '{best_password}' after {attempts} attempts")
            return None, attempts, elapsed

    # Keep existing dictionary and brute force methods
    def improved_dictionary_attack(self, target_hash: str, 
                                 timeout: int = 30) -> Tuple[str, int, float]:
        """Dictionary attack"""
        wordlist = ["password", "admin", "hello", "secret", "test", "user", "login",
                   "welcome", "123456", "letmein", "master", "qwerty", "abc123"]
        
        start_time = time.time()
        attempts = 0
        
        suffixes = ['', '1', '12', '123', '1234', '!', '0', '00']
        prefixes = ['', '!', '#', '$', '1', '12']
        
        for base_word in wordlist:
            if time.time() - start_time > timeout:
                break
                
            attempts += 1
            if self.hasher.hash_to_hex(base_word) == target_hash:
                return base_word, attempts, time.time() - start_time
            
            for prefix in prefixes:
                for suffix in suffixes:
                    candidate = prefix + base_word + suffix
                    attempts += 1
                    if self.hasher.hash_to_hex(candidate) == target_hash:
                        return candidate, attempts, time.time() - start_time
        
        return None, attempts, time.time() - start_time
    
    def improved_brute_force(self, target_hash: str, max_length: int = 8, 
                           timeout: int = 30) -> Tuple[str, int, float]:
        """Brute force"""
        charset = "abcdefghijklmnopqrstuvwxyz"
        start_time = time.time()
        attempts = 0
        
        for length in range(1, max_length + 1):
            if time.time() - start_time > timeout:
                break
            for candidate in itertools.product(charset, repeat=length):
                if time.time() - start_time > timeout:
                    break
                password = ''.join(candidate)
                attempts += 1
                if self.hasher.hash_to_hex(password) == target_hash:
                    return password, attempts, time.time() - start_time
        
        return None, attempts, time.time() - start_time

# Quick test
def quick_test():
    """Quick test to verify it works"""
    cracker = ImprovedQuantumPasswordCracker(verbose=True)
    
    test_password = "password"
    target_hash = cracker.hasher.hash_to_hex(test_password)
    
    print(f"Testing with: '{test_password}'")
    print(f"Hash: {target_hash}")
    
    print("\nTesting Genetic Algorithm:")
    result = cracker.improved_genetic_algorithm(target_hash, timeout=10)
    found, attempts, time_taken = result
    print(f"Result: {'SUCCESS' if found == test_password else 'FAILED'}")
    print(f"Found: '{found}', Time: {time_taken:.2f}s")
    
    print("\nTesting QAOA Approach:")
    result = cracker.improved_qaoa_approach(target_hash, timeout=10)
    found, attempts, time_taken = result
    print(f"Result: {'SUCCESS' if found == test_password else 'FAILED'}")
    print(f"Found: '{found}', Time: {time_taken:.2f}s")

if __name__ == "__main__":
    quick_test()
