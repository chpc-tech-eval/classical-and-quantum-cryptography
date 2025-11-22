# improved_quantum_password_cracker.py
#!/usr/bin/env python3
"""
IMPROVED Quantum Password Cracker with better optimization methods and detailed logging
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
    
    def improved_brute_force(self, target_hash: str, max_length: int = 8, 
                           timeout: int = 30) -> Tuple[str, int, float]:
        """
        Improved brute force with better character set and early stopping
        """
        self.log(f"Starting improved brute force (max length: {max_length})")
        start_time = time.time()
        attempts = 0
        last_log_time = start_time
        
        # More realistic character set (lowercase only for simple passwords)
        charset = "abcdefghijklmnopqrstuvwxyz"
        
        for length in range(1, max_length + 1):
            if time.time() - start_time > timeout:
                self.log(f"Timeout reached at length {length}")
                break
                
            self.log(f"Trying passwords of length {length}...")
            
            for candidate in itertools.product(charset, repeat=length):
                current_time = time.time()
                if current_time - start_time > timeout:
                    self.log(f"Timeout during length {length}")
                    break
                    
                # Progress logging every 2 seconds
                if current_time - last_log_time > 2.0:
                    password = ''.join(candidate)
                    self.log(f"Progress: length {length}, current: '{password}', attempts: {attempts}")
                    last_log_time = current_time
                    
                password = ''.join(candidate)
                attempts += 1
                
                if self.hasher.hash_to_hex(password) == target_hash:
                    elapsed = time.time() - start_time
                    self.log(f"SUCCESS: Found '{password}' after {attempts} attempts in {elapsed:.2f}s")
                    return password, attempts, elapsed
        
        elapsed = time.time() - start_time
        self.log(f"FAILED: No match found after {attempts} attempts in {elapsed:.2f}s")
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
        
        self.log(f"Starting improved dictionary attack ({len(wordlist)} base words)")
        start_time = time.time()
        attempts = 0
        
        # More realistic modifications
        suffixes = ['', '1', '12', '123', '1234', '!', '!!', '0', '00', '000']
        prefixes = ['', '!', '#', '$', '1', '12']
        
        total_combinations = len(wordlist) * (1 + len(prefixes) * len(suffixes))
        self.log(f"Total possible combinations: {total_combinations}")
        
        for i, base_word in enumerate(wordlist):
            if time.time() - start_time > timeout:
                self.log(f"Timeout after testing {i+1}/{len(wordlist)} base words")
                break
                
            self.log(f"Testing base word: '{base_word}' ({i+1}/{len(wordlist)})")
            
            # Try the base word first
            attempts += 1
            if self.hasher.hash_to_hex(base_word) == target_hash:
                elapsed = time.time() - start_time
                self.log(f"SUCCESS: Found '{base_word}' (base word) after {attempts} attempts in {elapsed:.2f}s")
                return base_word, attempts, elapsed
            
            # Then try modifications
            modification_count = 0
            for prefix in prefixes:
                for suffix in suffixes:
                    if modification_count > 0 and modification_count % 50 == 0:
                        self.log(f"  Tested {modification_count} modifications for '{base_word}'")
                    
                    candidate = prefix + base_word + suffix
                    attempts += 1
                    modification_count += 1
                    
                    if self.hasher.hash_to_hex(candidate) == target_hash:
                        elapsed = time.time() - start_time
                        self.log(f"SUCCESS: Found '{candidate}' (modified) after {attempts} attempts in {elapsed:.2f}s")
                        return candidate, attempts, elapsed
        
        elapsed = time.time() - start_time
        self.log(f"FAILED: No match found after {attempts} attempts in {elapsed:.2f}s")
        return None, attempts, elapsed
    
    def improved_genetic_algorithm(self, target_hash: str, population_size: int = 50,
                                 generations: int = 100, timeout: int = 30) -> Tuple[str, int, float]:
        """
        Vastly improved genetic algorithm with better fitness and operators
        """
        self.log(f"Starting improved genetic algorithm (pop: {population_size}, gens: {generations})")
        start_time = time.time()
        
        # Character set focused on common passwords
        charset = "abcdefghijklmnopqrstuvwxyz0123456789"
        attempts = 0
        
        # Store evolution data for analysis
        evolution_data = {
            'generations': [],
            'best_fitness': [],
            'avg_fitness': [],
            'best_password': [],
            'diversity': []
        }
        
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
        
        self.log("Initializing population...")
        for i in range(population_size):
            if np.random.random() < 0.3 and common_starts:
                # Use common patterns
                base = np.random.choice(common_starts)
                if np.random.random() < 0.7:
                    base += np.random.choice(common_ends)
                password = base
                self.log(f"  Individual {i+1}: '{password}' (pattern-based)")
            else:
                # Random password
                length = np.random.randint(4, 10)
                password = ''.join(np.random.choice(list(charset), length))
                self.log(f"  Individual {i+1}: '{password}' (random)")
            population.append(password)
        
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
            
            # Calculate diversity (unique passwords)
            unique_passwords = len(set(population))
            diversity = unique_passwords / len(population)
            
            # Store evolution data
            evolution_data['generations'].append(generation)
            evolution_data['best_fitness'].append(current_best_fitness)
            evolution_data['avg_fitness'].append(np.mean(fitness_scores))
            evolution_data['best_password'].append(current_best_password)
            evolution_data['diversity'].append(diversity)
            
            # Log generation progress
            if generation % 10 == 0 or generation < 5:
                self.log(f"Generation {generation:3d}: best='{current_best_password}' "
                        f"fitness={current_best_fitness:8.0f} "
                        f"avg={np.mean(fitness_scores):8.0f} "
                        f"diversity={diversity:.2f}")
            
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
                            self.log(f"  Mutation: replaced char in '{child1}'")
                        if np.random.random() < 0.3:
                            pos = np.random.randint(len(child2))
                            child2 = child2[:pos] + np.random.choice(list(charset)) + child2[pos+1:]
                            self.log(f"  Mutation: replaced char in '{child2}'")
                        
                        new_population.extend([child1, child2])
                else:
                    # Mutation only
                    child = parent1
                    if np.random.random() < 0.5:
                        # Character mutation
                        pos = np.random.randint(len(child))
                        old_char = child[pos]
                        new_char = np.random.choice(list(charset))
                        child = child[:pos] + new_char + child[pos+1:]
                        self.log(f"  Mutation: '{parent1}' -> '{child}' (replaced '{old_char}' with '{new_char}')")
                    elif np.random.random() < 0.3:
                        # Add character
                        pos = np.random.randint(len(child) + 1)
                        new_char = np.random.choice(list(charset))
                        child = child[:pos] + new_char + child[pos:]
                        self.log(f"  Mutation: '{parent1}' -> '{child}' (added '{new_char}')")
                    elif len(child) > 4 and np.random.random() < 0.2:
                        # Remove character
                        pos = np.random.randint(len(child))
                        removed_char = child[pos]
                        child = child[:pos] + child[pos+1:]
                        self.log(f"  Mutation: '{parent1}' -> '{child}' (removed '{removed_char}')")
                    
                    new_population.append(child)
            
            population = new_population[:population_size]
        
        elapsed = time.time() - start_time
        
        # Store evolution data for analysis
        self.log_data['genetic_evolution'] = evolution_data
        
        # Return best candidate found
        if best_password and self.hasher.hash_to_hex(best_password) == target_hash:
            self.log(f"SUCCESS: Found '{best_password}' after {attempts} attempts in {elapsed:.2f}s")
            return best_password, attempts, elapsed
        else:
            self.log(f"FAILED: Best candidate '{best_password}' after {attempts} attempts in {elapsed:.2f}s")
            return None, attempts, elapsed
    
    def improved_qaoa_approach(self, target_hash: str, max_iter: int = 200,
                             timeout: int = 30) -> Tuple[str, int, float]:
        """
        Improved approach using direct optimization on password characters
        """
        self.log(f"Starting improved QAOA approach (max iterations: {max_iter})")
        start_time = time.time()
        attempts = 0
        
        charset = "abcdefghijklmnopqrstuvwxyz0123456789"
        
        # Store optimization data
        optimization_data = {
            'iterations': [],
            'current_score': [],
            'best_score': [],
            'current_password': [],
            'best_password': [],
            'operation': []
        }
        
        def evaluate_password(password):
            """Evaluate how close this password's hash is to target"""
            candidate_hash = self.hasher.hash_password(password)
            target_hash_int = int(target_hash, 16)
            score = -abs(candidate_hash - target_hash_int)  # Negative because we maximize
            return score
        
        # Start with common passwords and mutate
        common_passwords = ["password", "admin", "hello", "test", "secret"]
        current_password = np.random.choice(common_passwords)
        current_score = evaluate_password(current_password)
        attempts += 1
        
        self.log(f"Initial password: '{current_password}' (score: {current_score:.0f})")
        
        if self.hasher.hash_to_hex(current_password) == target_hash:
            elapsed = time.time() - start_time
            self.log(f"SUCCESS: Initial password matched after {attempts} attempts in {elapsed:.2f}s")
            return current_password, attempts, elapsed
        
        best_password = current_password
        best_score = current_score
        
        # Store initial state
        optimization_data['iterations'].append(0)
        optimization_data['current_score'].append(current_score)
        optimization_data['best_score'].append(best_score)
        optimization_data['current_password'].append(current_password)
        optimization_data['best_password'].append(best_password)
        optimization_data['operation'].append("initial")
        
        # Local search with restarts
        for iteration in range(1, max_iter + 1):
            if time.time() - start_time > timeout:
                self.log(f"Timeout at iteration {iteration}/{max_iter}")
                break
                
            # Mutate current password
            new_password = list(current_password)
            operation = ""
            
            # Choose mutation type
            mutation_type = np.random.choice(['replace', 'insert', 'delete', 'swap'])
            
            if mutation_type == 'replace' and len(new_password) > 0:
                pos = np.random.randint(len(new_password))
                old_char = new_password[pos]
                new_char = np.random.choice(list(charset))
                new_password[pos] = new_char
                operation = f"replace '{old_char}' with '{new_char}' at position {pos}"
                
            elif mutation_type == 'insert' and len(new_password) < 12:
                pos = np.random.randint(len(new_password) + 1)
                new_char = np.random.choice(list(charset))
                new_password.insert(pos, new_char)
                operation = f"insert '{new_char}' at position {pos}"
                
            elif mutation_type == 'delete' and len(new_password) > 4:
                pos = np.random.randint(len(new_password))
                removed_char = new_password.pop(pos)
                operation = f"delete '{removed_char}' at position {pos}"
                
            elif mutation_type == 'swap' and len(new_password) >= 2:
                pos1, pos2 = np.random.choice(len(new_password), 2, replace=False)
                new_password[pos1], new_password[pos2] = new_password[pos2], new_password[pos1]
                operation = f"swap positions {pos1} and {pos2}"
            
            new_password_str = ''.join(new_password)
            attempts += 1
            
            # Evaluate
            new_score = evaluate_password(new_password_str)
            
            # Accept if better, or sometimes accept worse (simulated annealing)
            temperature = 1.0 - (iteration / max_iter)  # Cooling schedule
            accept_probability = np.exp((new_score - current_score) / max(0.1, temperature))
            
            accepted = new_score > current_score or np.random.random() < accept_probability
            
            if accepted:
                old_password = current_password
                current_password = new_password_str
                current_score = new_score
                operation += f" - ACCEPTED (score: {new_score:.0f})"
                
                if new_score > best_score:
                    best_password = new_password_str
                    best_score = new_score
                    operation += " - NEW BEST"
            else:
                operation += f" - REJECTED (score: {new_score:.0f})"
            
            # Store iteration data
            optimization_data['iterations'].append(iteration)
            optimization_data['current_score'].append(current_score)
            optimization_data['best_score'].append(best_score)
            optimization_data['current_password'].append(current_password)
            optimization_data['best_password'].append(best_password)
            optimization_data['operation'].append(operation)
            
            # Log progress
            if iteration % 20 == 0 or iteration <= 5:
                self.log(f"Iteration {iteration:3d}: current='{current_password}' "
                        f"(score: {current_score:6.0f}) best='{best_password}' "
                        f"(score: {best_score:6.0f}) - {operation.split(' - ')[0]}")
            
            # Check for solution
            if self.hasher.hash_to_hex(current_password) == target_hash:
                elapsed = time.time() - start_time
                self.log(f"SUCCESS: Found '{current_password}' at iteration {iteration} after {attempts} attempts in {elapsed:.2f}s")
                return current_password, attempts, elapsed
            
            # Random restart occasionally
            if iteration % 25 == 0:
                old_password = current_password
                current_password = np.random.choice(common_passwords)
                current_score = evaluate_password(current_password)
                attempts += 1
                self.log(f"RESTART: '{old_password}' -> '{current_password}' (score: {current_score:.0f})")
        
        elapsed = time.time() - start_time
        
        # Store optimization data for analysis
        self.log_data['qaoa_optimization'] = optimization_data
        
        # Check best candidate
        if best_password and self.hasher.hash_to_hex(best_password) == target_hash:
            self.log(f"SUCCESS: Found '{best_password}' after {attempts} attempts in {elapsed:.2f}s")
            return best_password, attempts, elapsed
        else:
            self.log(f"FAILED: Best candidate '{best_password}' (score: {best_score:.0f}) after {attempts} attempts in {elapsed:.2f}s")
            return None, attempts, elapsed

    def plot_evolution(self, method: str = "genetic"):
        """Plot the evolution of the optimization process"""
        if method not in self.log_data:
            print(f"No evolution data available for {method}")
            return
        
        data = self.log_data[method]
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'{method.upper()} Optimization Evolution', fontsize=16)
        
        if method == "genetic":
            # Genetic algorithm plots
            axes[0, 0].plot(data['generations'], data['best_fitness'], 'b-', label='Best Fitness')
            axes[0, 0].plot(data['generations'], data['avg_fitness'], 'r--', label='Average Fitness')
            axes[0, 0].set_xlabel('Generation')
            axes[0, 0].set_ylabel('Fitness')
            axes[0, 0].set_title('Fitness Evolution')
            axes[0, 0].legend()
            axes[0, 0].grid(True)
            
            axes[0, 1].plot(data['generations'], data['diversity'], 'g-')
            axes[0, 1].set_xlabel('Generation')
            axes[0, 1].set_ylabel('Diversity')
            axes[0, 1].set_title('Population Diversity')
            axes[0, 1].grid(True)
            
            # Password length evolution
            password_lengths = [len(pwd) for pwd in data['best_password']]
            axes[1, 0].plot(data['generations'], password_lengths, 'purple', marker='o')
            axes[1, 0].set_xlabel('Generation')
            axes[1, 0].set_ylabel('Password Length')
            axes[1, 0].set_title('Best Password Length Evolution')
            axes[1, 0].grid(True)
            
            # Show some best passwords
            axes[1, 1].axis('off')
            best_passwords_text = "Best Passwords by Generation:\n"
            for i in range(0, len(data['generations']), max(1, len(data['generations'])//10)):
                gen = data['generations'][i]
                pwd = data['best_password'][i]
                fitness_val = data['best_fitness'][i]
                best_passwords_text += f"Gen {gen:3d}: '{pwd}' (fitness: {fitness_val:.0f})\n"
            axes[1, 1].text(0.1, 0.9, best_passwords_text, transform=axes[1, 1].transAxes, 
                           fontfamily='monospace', verticalalignment='top')
        
        elif method == "qaoa":
            # QAOA optimization plots
            axes[0, 0].plot(data['iterations'], data['best_score'], 'b-', label='Best Score')
            axes[0, 0].plot(data['iterations'], data['current_score'], 'r--', label='Current Score')
            axes[0, 0].set_xlabel('Iteration')
            axes[0, 0].set_ylabel('Score')
            axes[0, 0].set_title('Score Evolution')
            axes[0, 0].legend()
            axes[0, 0].grid(True)
            
            # Password length evolution
            password_lengths = [len(pwd) for pwd in data['current_password']]
            axes[0, 1].plot(data['iterations'], password_lengths, 'purple', marker='o')
            axes[0, 1].set_xlabel('Iteration')
            axes[0, 1].set_ylabel('Password Length')
            axes[0, 1].set_title('Current Password Length')
            axes[0, 1].grid(True)
            
            # Show operations
            axes[1, 0].axis('off')
            operations_text = "Recent Operations:\n"
            start_idx = max(0, len(data['operations']) - 15)
            for i in range(start_idx, len(data['operations'])):
                op = data['operations'][i]
                if op:  # Only show non-empty operations
                    operations_text += f"Iter {data['iterations'][i]:3d}: {op}\n"
            axes[1, 0].text(0.1, 0.9, operations_text, transform=axes[1, 0].transAxes, 
                           fontfamily='monospace', fontsize=8, verticalalignment='top')
            
            # Show best passwords
            axes[1, 1].axis('off')
            best_passwords_text = "Best Passwords by Iteration:\n"
            for i in range(0, len(data['iterations']), max(1, len(data['iterations'])//10)):
                iter_num = data['iterations'][i]
                pwd = data['best_password'][i]
                score = data['best_score'][i]
                best_passwords_text += f"Iter {iter_num:3d}: '{pwd}' (score: {score:.0f})\n"
            axes[1, 1].text(0.1, 0.9, best_passwords_text, transform=axes[1, 1].transAxes, 
                           fontfamily='monospace', verticalalignment='top')
        
        plt.tight_layout()
        plt.savefig(f'{method}_evolution.png', dpi=150, bbox_inches='tight')
        plt.show()

# Test function to demonstrate the logging
def test_with_logging():
    """Test the enhanced cracker with detailed logging"""
    cracker = ImprovedQuantumPasswordCracker(verbose=True)
    
    test_password = "admin"
    target_hash = cracker.hasher.hash_to_hex(test_password)
    
    print(f"Testing password: '{test_password}'")
    print(f"Target hash: {target_hash}")
    print("\n" + "="*60)
    
    # Test genetic algorithm with logging
    print("\nGENETIC ALGORITHM (with detailed logging):")
    print("-" * 40)
    result = cracker.improved_genetic_algorithm(target_hash, timeout=10)
    password_found, attempts, time_taken = result
    
    if password_found == test_password:
        print(f"SUCCESS: Found '{password_found}'")
    else:
        print(f"FAILED: Found '{password_found}'")
    
    # Plot evolution if data is available
    if 'genetic_evolution' in cracker.log_data:
        cracker.plot_evolution("genetic")
    
    print("\n" + "="*60)
    
    # Test QAOA with logging
    print("\nQAOA OPTIMIZATION (with detailed logging):")
    print("-" * 40)
    result = cracker.improved_qaoa_approach(target_hash, timeout=10)
    password_found, attempts, time_taken = result
    
    if password_found == test_password:
        print(f"SUCCESS: Found '{password_found}'")
    else:
        print(f"FAILED: Found '{password_found}'")
    
    # Plot evolution if data is available
    if 'qaoa_optimization' in cracker.log_data:
        cracker.plot_evolution("qaoa")

if __name__ == "__main__":
    test_with_logging()
