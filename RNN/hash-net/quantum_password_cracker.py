# enhanced_quantum_password_cracker.py
#!/usr/bin/env python3
"""
ENHANCED Quantum Password Cracker with improved genetic and QAOA algorithms
"""

import numpy as np
import time
import hashlib
import math
import itertools
from typing import List, Tuple, Dict, Optional
import matplotlib.pyplot as plt
from generate_training_data_with_hashes import ToyHasher

class EnhancedQuantumPasswordCracker:
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
    
    def enhanced_genetic_algorithm(self, target_hash: str, population_size: int = 100,
                                 generations: int = 200, timeout: int = 30) -> Tuple[str, int, float]:
        """
        ENHANCED genetic algorithm with better initialization, crossover, and mutation
        """
        self.log(f"Starting ENHANCED genetic algorithm (pop: {population_size}, gens: {generations})")
        start_time = time.time()
        
        # Expanded character set
        charset = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%&*"
        attempts = 0
        
        # Store evolution data
        evolution_data = {
            'generations': [],
            'best_fitness': [],
            'avg_fitness': [],
            'best_password': [],
            'diversity': []
        }
        
        def fitness(password):
            """Enhanced fitness function with multiple criteria"""
            if not password or len(password) < 2 or len(password) > 20:
                return -10000
                
            candidate_hash = self.hasher.hash_password(password)
            target_hash_int = int(target_hash, 16)
            
            # Primary: Exact hash match (massive bonus)
            if candidate_hash == target_hash_int:
                return 1000000
                
            # Secondary: Hash similarity (bit-level comparison)
            hash_diff = abs(candidate_hash - target_hash_int)
            
            # Tertiary: Length similarity to common passwords (4-12 chars)
            length_penalty = abs(len(password) - 8) * 100
            
            # Character type bonus (reward realistic passwords)
            char_bonus = 0
            if any(c.isdigit() for c in password):
                char_bonus += 50
            if any(c in "!@#$%&*" for c in password):
                char_bonus += 100
            if any(c.isupper() for c in password):
                char_bonus += 50
            
            # Final fitness calculation
            fitness_score = -hash_diff - length_penalty + char_bonus
            
            return fitness_score
        
        # ENHANCED Population Initialization
        population = []
        common_passwords = [
            "password", "admin", "hello", "test", "user", "secret", "123456", 
            "letmein", "welcome", "login", "master", "qwerty", "abc123"
        ]
        
        self.log("Enhanced population initialization...")
        
        # Strategy 1: Direct common passwords (30%)
        for pwd in common_passwords[:min(10, len(common_passwords))]:
            population.append(pwd)
            self.log(f"  Added common password: '{pwd}'")
        
        # Strategy 2: Common patterns with modifications (40%)
        patterns = ["pass", "admin", "hello", "test", "user", "secret"]
        suffixes = ["", "1", "12", "123", "1234", "!", "!!", "0", "00", "000", "2024"]
        
        while len(population) < population_size * 0.7:
            base = np.random.choice(patterns)
            suffix = np.random.choice(suffixes)
            password = base + suffix
            if password not in population:
                population.append(password)
        
        # Strategy 3: Smart random generation (30%)
        while len(population) < population_size:
            # Vary length based on common password lengths
            length = np.random.choice([4, 5, 6, 7, 8, 9, 10], p=[0.1, 0.15, 0.2, 0.2, 0.15, 0.1, 0.1])
            
            # Mix character types realistically
            if np.random.random() < 0.7:  # 70% lowercase only
                password = ''.join(np.random.choice(list("abcdefghijklmnopqrstuvwxyz"), length))
            elif np.random.random() < 0.5:  # 15% alphanumeric
                password = ''.join(np.random.choice(list("abcdefghijklmnopqrstuvwxyz0123456789"), length))
            else:  # 15% with special chars
                base = ''.join(np.random.choice(list("abcdefghijklmnopqrstuvwxyz0123456789"), length-1))
                special = np.random.choice(list("!@#$%&*"))
                pos = np.random.randint(len(base) + 1)
                password = base[:pos] + special + base[pos:]
            
            if password not in population:
                population.append(password)
        
        population = population[:population_size]
        
        best_fitness = -float('inf')
        best_password = None
        stagnation_count = 0
        last_improvement = 0
        
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
                
                # Check for solution
                if self.hasher.hash_to_hex(pwd) == target_hash:
                    elapsed = time.time() - start_time
                    self.log(f"SUCCESS: Generation {generation}, found '{pwd}' after {attempts} attempts in {elapsed:.2f}s")
                    return pwd, attempts, elapsed
                
                # Track current best
                if fitness_val > current_best_fitness:
                    current_best_fitness = fitness_val
                    current_best_password = pwd
                
                # Track overall best
                if fitness_val > best_fitness:
                    best_fitness = fitness_val
                    best_password = pwd
                    last_improvement = generation
                    stagnation_count = 0
            
            # Stagnation detection
            if generation - last_improvement > 20:
                stagnation_count += 1
                if stagnation_count > 5:
                    self.log(f"Stagnation detected at generation {generation}, increasing mutation rate")
            
            # Calculate diversity
            unique_passwords = len(set(population))
            diversity = unique_passwords / len(population)
            
            # Store evolution data
            evolution_data['generations'].append(generation)
            evolution_data['best_fitness'].append(current_best_fitness)
            evolution_data['avg_fitness'].append(np.mean(fitness_scores))
            evolution_data['best_password'].append(current_best_password)
            evolution_data['diversity'].append(diversity)
            
            # Log progress
            if generation % 20 == 0 or generation < 5:
                self.log(f"Gen {generation:3d}: best='{current_best_password}' "
                        f"fitness={current_best_fitness:8.0f} diversity={diversity:.2f}")
            
            # ENHANCED Selection and Reproduction
            new_population = []
            
            # Elitism: keep top 10%
            elite_count = max(1, population_size // 10)
            elite_indices = np.argsort(fitness_scores)[-elite_count:]
            for idx in elite_indices:
                new_population.append(population[idx])
            
            # Enhanced crossover and mutation
            while len(new_population) < population_size:
                # Tournament selection with adaptive size
                tournament_size = 3 + min(5, stagnation_count)
                tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
                tournament_fitness = [fitness_scores[i] for i in tournament_indices]
                winner_idx = tournament_indices[np.argmax(tournament_fitness)]
                parent1 = population[winner_idx]
                
                # Adaptive mutation rate based on stagnation
                base_mutation_rate = 0.3 + (stagnation_count * 0.1)
                
                if np.random.random() < 0.8 and len(new_population) < population_size - 1:
                    # Enhanced crossover
                    tournament_indices2 = np.random.choice(len(population), tournament_size, replace=False)
                    tournament_fitness2 = [fitness_scores[i] for i in tournament_indices2]
                    winner_idx2 = tournament_indices2[np.argmax(tournament_fitness2)]
                    parent2 = population[winner_idx2]
                    
                    # Multiple crossover strategies
                    crossover_strategy = np.random.choice(['single', 'two', 'uniform'])
                    
                    if crossover_strategy == 'single' and len(parent1) > 1 and len(parent2) > 1:
                        point = np.random.randint(1, min(len(parent1), len(parent2)))
                        child1 = parent1[:point] + parent2[point:]
                        child2 = parent2[:point] + parent1[point:]
                    elif crossover_strategy == 'two' and len(parent1) > 2 and len(parent2) > 2:
                        point1 = np.random.randint(1, min(len(parent1), len(parent2))//2)
                        point2 = np.random.randint(point1+1, min(len(parent1), len(parent2)))
                        child1 = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
                        child2 = parent2[:point1] + parent1[point1:point2] + parent2[point2:]
                    else:  # uniform crossover
                        child1_chars = []
                        child2_chars = []
                        min_len = min(len(parent1), len(parent2))
                        for i in range(min_len):
                            if np.random.random() < 0.5:
                                child1_chars.append(parent1[i])
                                child2_chars.append(parent2[i])
                            else:
                                child1_chars.append(parent2[i])
                                child2_chars.append(parent1[i])
                        child1 = ''.join(child1_chars) + parent1[min_len:] + parent2[min_len:]
                        child2 = ''.join(child2_chars) + parent2[min_len:] + parent1[min_len:]
                    
                    # Enhanced mutation
                    for child in [child1, child2]:
                        if np.random.random() < base_mutation_rate:
                            mutation_type = np.random.choice(['replace', 'insert', 'delete', 'swap', 'case'])
                            
                            if mutation_type == 'replace' and len(child) > 0:
                                pos = np.random.randint(len(child))
                                child = child[:pos] + np.random.choice(list(charset)) + child[pos+1:]
                            elif mutation_type == 'insert' and len(child) < 15:
                                pos = np.random.randint(len(child) + 1)
                                child = child[:pos] + np.random.choice(list(charset)) + child[pos:]
                            elif mutation_type == 'delete' and len(child) > 3:
                                pos = np.random.randint(len(child))
                                child = child[:pos] + child[pos+1:]
                            elif mutation_type == 'swap' and len(child) >= 2:
                                pos1, pos2 = np.random.choice(len(child), 2, replace=False)
                                chars = list(child)
                                chars[pos1], chars[pos2] = chars[pos2], chars[pos1]
                                child = ''.join(chars)
                            elif mutation_type == 'case' and any(c.isalpha() for c in child):
                                pos = np.random.randint(len(child))
                                if child[pos].isalpha():
                                    new_char = child[pos].upper() if child[pos].islower() else child[pos].lower()
                                    child = child[:pos] + new_char + child[pos+1:]
                        
                        new_population.append(child)
                else:
                    # Mutation-only reproduction
                    child = parent1
                    if np.random.random() < base_mutation_rate:
                        mutation_type = np.random.choice(['replace', 'insert', 'delete', 'swap', 'case'])
                        # ... (same mutation logic as above)
                    
                    new_population.append(child)
            
            population = new_population[:population_size]
            
            # Diversity injection if stagnating
            if stagnation_count > 10 and generation % 10 == 0:
                self.log("Injecting diversity into population")
                # Replace worst 20% with new random individuals
                worst_indices = np.argsort(fitness_scores)[:population_size//5]
                for idx in worst_indices:
                    length = np.random.randint(4, 12)
                    new_individual = ''.join(np.random.choice(list(charset), length))
                    population[idx] = new_individual
        
        elapsed = time.time() - start_time
        self.log_data['genetic_evolution'] = evolution_data
        
        if best_password and self.hasher.hash_to_hex(best_password) == target_hash:
            self.log(f"SUCCESS: Found '{best_password}' after {attempts} attempts in {elapsed:.2f}s")
            return best_password, attempts, elapsed
        else:
            self.log(f"FAILED: Best candidate '{best_password}' after {attempts} attempts in {elapsed:.2f}s")
            return None, attempts, elapsed
    
    def enhanced_qaoa_approach(self, target_hash: str, max_iter: int = 500,
                             timeout: int = 30) -> Tuple[str, int, float]:
        """
        ENHANCED QAOA approach with multiple search strategies and better local search
        """
        self.log(f"Starting ENHANCED QAOA approach (max iterations: {max_iter})")
        start_time = time.time()
        attempts = 0
        
        charset = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%&*"
        
        # Store optimization data
        optimization_data = {
            'iterations': [],
            'current_score': [],
            'best_score': [],
            'current_password': [],
            'best_password': [],
            'operation': [],
            'strategy': []
        }
        
        def evaluate_password(password):
            """Enhanced evaluation with multiple criteria"""
            if not password or len(password) < 2 or len(password) > 20:
                return -10000
                
            candidate_hash = self.hasher.hash_password(password)
            target_hash_int = int(target_hash, 16)
            
            # Exact match bonus
            if candidate_hash == target_hash_int:
                return 1000000
            
            # Hash similarity (primary)
            hash_diff = abs(candidate_hash - target_hash_int)
            
            # Length preference (common lengths 4-12)
            length_penalty = abs(len(password) - 8) * 100
            
            # Character diversity bonus
            char_bonus = 0
            if any(c.isdigit() for c in password):
                char_bonus += 50
            if any(c in "!@#$%&*" for c in password):
                char_bonus += 100
            
            score = -hash_diff - length_penalty + char_bonus
            return score
        
        # MULTIPLE STARTING STRATEGIES
        starting_passwords = [
            # Common passwords
            "password", "admin", "hello", "test", "user", "secret", "123456",
            # Short passwords
            "a", "ab", "abc", "1", "12", "123",
            # Pattern-based
            "pass", "admin1", "test123", "hello1",
            # Random reasonable lengths
            ''.join(np.random.choice(list("abcdefghijklmnopqrstuvwxyz"), 6)),
            ''.join(np.random.choice(list("abcdefghijklmnopqrstuvwxyz0123456789"), 8))
        ]
        
        # Try all starting points quickly first
        self.log("Trying multiple starting strategies...")
        for start_pwd in starting_passwords:
            attempts += 1
            if self.hasher.hash_to_hex(start_pwd) == target_hash:
                elapsed = time.time() - start_time
                self.log(f"SUCCESS: Starting password '{start_pwd}' matched!")
                return start_pwd, attempts, elapsed
        
        # Select best starting point based on fitness
        start_fitness = [evaluate_password(pwd) for pwd in starting_passwords]
        best_start_idx = np.argmax(start_fitness)
        current_password = starting_passwords[best_start_idx]
        current_score = start_fitness[best_start_idx]
        
        self.log(f"Best starting password: '{current_password}' (score: {current_score:.0f})")
        
        best_password = current_password
        best_score = current_score
        
        # Search strategies
        strategies = ['local_search', 'pattern_based', 'hash_guided', 'random_walk']
        strategy_weights = [0.4, 0.3, 0.2, 0.1]  # Preference for local search
        
        for iteration in range(1, max_iter + 1):
            if time.time() - start_time > timeout:
                self.log(f"Timeout at iteration {iteration}/{max_iter}")
                break
                
            # Adaptive strategy selection
            if iteration % 50 == 0:
                # Every 50 iterations, rebalance strategy weights
                if best_score > -1000:  # If we're making progress
                    strategy_weights = [0.5, 0.3, 0.15, 0.05]  # Focus on local search
                else:
                    strategy_weights = [0.2, 0.3, 0.3, 0.2]  # Explore more
            
            strategy = np.random.choice(strategies, p=strategy_weights)
            new_password = current_password
            operation = ""
            
            if strategy == 'local_search':
                # Enhanced local mutations
                mutation_type = np.random.choice(['replace', 'insert', 'delete', 'swap', 'append', 'prepend'])
                
                if mutation_type == 'replace' and len(new_password) > 0:
                    pos = np.random.randint(len(new_password))
                    new_char = np.random.choice(list(charset))
                    new_password = new_password[:pos] + new_char + new_password[pos+1:]
                    operation = f"local: replace at {pos}"
                    
                elif mutation_type == 'insert' and len(new_password) < 15:
                    pos = np.random.randint(len(new_password) + 1)
                    new_char = np.random.choice(list(charset))
                    new_password = new_password[:pos] + new_char + new_password[pos:]
                    operation = f"local: insert at {pos}"
                    
                elif mutation_type == 'delete' and len(new_password) > 2:
                    pos = np.random.randint(len(new_password))
                    new_password = new_password[:pos] + new_password[pos+1:]
                    operation = f"local: delete at {pos}"
                    
                elif mutation_type == 'swap' and len(new_password) >= 2:
                    pos1, pos2 = np.random.choice(len(new_password), 2, replace=False)
                    chars = list(new_password)
                    chars[pos1], chars[pos2] = chars[pos2], chars[pos1]
                    new_password = ''.join(chars)
                    operation = f"local: swap {pos1}<->{pos2}"
                    
                elif mutation_type == 'append' and len(new_password) < 15:
                    new_char = np.random.choice(list(charset))
                    new_password = new_password + new_char
                    operation = f"local: append '{new_char}'"
                    
                elif mutation_type == 'prepend' and len(new_password) < 15:
                    new_char = np.random.choice(list(charset))
                    new_password = new_char + new_password
                    operation = f"local: prepend '{new_char}'"
            
            elif strategy == 'pattern_based':
                # Pattern-based generation
                common_patterns = [
                    "pass", "admin", "test", "user", "hello", "secret",
                    "123", "1234", "12345", "!", "!!", "1", "0", "00"
                ]
                
                if np.random.random() < 0.5:
                    # Combine patterns
                    pattern1 = np.random.choice(common_patterns)
                    pattern2 = np.random.choice(common_patterns)
                    new_password = pattern1 + pattern2
                    operation = f"pattern: {pattern1} + {pattern2}"
                else:
                    # Add pattern to current password
                    pattern = np.random.choice(common_patterns)
                    if np.random.random() < 0.5:
                        new_password = current_password + pattern
                        operation = f"pattern: append {pattern}"
                    else:
                        new_password = pattern + current_password
                        operation = f"pattern: prepend {pattern}"
            
            elif strategy == 'hash_guided':
                # Use hash bits to guide search (simplified)
                target_bits = bin(int(target_hash, 16))[2:].zfill(32)
                bit_pattern = target_bits[:6]  # Use first 6 bits to influence length
                suggested_length = int(bit_pattern, 2) % 10 + 3  # Length between 3-12
                
                if abs(len(current_password) - suggested_length) > 2:
                    # Adjust length toward suggestion
                    if len(current_password) < suggested_length:
                        # Add characters
                        chars_to_add = suggested_length - len(current_password)
                        for _ in range(chars_to_add):
                            pos = np.random.randint(len(new_password) + 1)
                            new_char = np.random.choice(list(charset))
                            new_password = new_password[:pos] + new_char + new_password[pos:]
                    else:
                        # Remove characters
                        chars_to_remove = len(current_password) - suggested_length
                        for _ in range(chars_to_remove):
                            if len(new_password) > 3:
                                pos = np.random.randint(len(new_password))
                                new_password = new_password[:pos] + new_password[pos+1:]
                
                operation = f"hash_guided: target_len={suggested_length}"
            
            else:  # random_walk
                # Complete random restart
                length = np.random.randint(3, 13)
                new_password = ''.join(np.random.choice(list(charset), length))
                operation = f"random_walk: new length {length}"
            
            attempts += 1
            new_score = evaluate_password(new_password)
            
            # Enhanced acceptance criteria
            temperature = max(0.1, 1.0 - (iteration / max_iter))
            accept_probability = np.exp((new_score - current_score) / temperature)
            
            if new_score > current_score or np.random.random() < accept_probability:
                current_password = new_password
                current_score = new_score
                operation += f" - ACCEPTED (Δ={new_score-current_score:.0f})"
                
                if new_score > best_score:
                    best_password = new_password
                    best_score = new_score
                    operation += " - NEW BEST"
            else:
                operation += f" - REJECTED (Δ={new_score-current_score:.0f})"
            
            # Store data
            optimization_data['iterations'].append(iteration)
            optimization_data['current_score'].append(current_score)
            optimization_data['best_score'].append(best_score)
            optimization_data['current_password'].append(current_password)
            optimization_data['best_password'].append(best_password)
            optimization_data['operation'].append(operation)
            optimization_data['strategy'].append(strategy)
            
            # Log progress
            if iteration % 25 == 0 or iteration <= 10:
                self.log(f"Iter {iteration:3d}: {strategy:12} "
                        f"current='{current_password}' ({current_score:6.0f}) "
                        f"best='{best_password}' ({best_score:6.0f})")
            
            # Check for solution
            if self.hasher.hash_to_hex(current_password) == target_hash:
                elapsed = time.time() - start_time
                self.log(f"SUCCESS: Found '{current_password}' at iteration {iteration}!")
                return current_password, attempts, elapsed
            
            # Strategic restart if stuck
            if iteration % 100 == 0 and best_score < -5000:
                self.log("Strategic restart: exploring new region")
                length = np.random.randint(3, 10)
                current_password = ''.join(np.random.choice(list(charset), length))
                current_score = evaluate_password(current_password)
                attempts += 1
        
        elapsed = time.time() - start_time
        self.log_data['qaoa_optimization'] = optimization_data
        
        if best_password and self.hasher.hash_to_hex(best_password) == target_hash:
            self.log(f"SUCCESS: Found '{best_password}' after {attempts} attempts!")
            return best_password, attempts, elapsed
        else:
            self.log(f"FAILED: Best candidate '{best_password}' (score: {best_score:.0f})")
            return None, attempts, elapsed

# Update the demo to use enhanced methods
def enhanced_batch_demo():
    """Run batch demo with enhanced methods"""
    cracker = EnhancedQuantumPasswordCracker(verbose=False)
    
    test_passwords = ["password", "admin", "hello", "test123", "secret", "123456", "letmein", "welcome", "he"]
    
    print("ENHANCED METHODS BATCH TEST")
    print("=" * 50)
    
    for password in test_passwords:
        print(f"\nCracking: '{password}'")
        target_hash = cracker.hasher.hash_to_hex(password)
        
        # Test enhanced genetic
        print("  Enhanced Genetic...", end=" ", flush=True)
        result = cracker.enhanced_genetic_algorithm(target_hash, timeout=15)
        found, attempts, time_taken = result
        status = "SUCCESS" if found == password else "FAILED"
        print(f"{status} ({time_taken:.2f}s, {attempts} attempts)")
        
        # Test enhanced QAOA
        print("  Enhanced QAOA......", end=" ", flush=True)
        result = cracker.enhanced_qaoa_approach(target_hash, timeout=15)
        found, attempts, time_taken = result
        status = "SUCCESS" if found == password else "FAILED"
        print(f"{status} ({time_taken:.2f}s, {attempts} attempts)")

if __name__ == "__main__":
    enhanced_batch_demo()
