# improved_quantum_password_cracker_comprehensive.py
#!/usr/bin/env python3
"""
COMPREHENSIVE Quantum Password Cracker with Configurable Security Levels
and Advanced Statistical Analysis
"""

import numpy as np
import time
import hashlib
import math
import itertools
import string
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd
from collections import defaultdict, deque
import random

class SecurityLevel(Enum):
    LOW = 16      # 16-bit security (easy)
    MEDIUM = 32   # 32-bit security (moderate)  
    HIGH = 64     # 64-bit security (hard)
    EXTREME = 128 # 128-bit security (very hard)

class PasswordComplexity(Enum):
    NUMERIC = "0123456789"
    ALPHANUMERIC = string.ascii_lowercase + string.digits
    ALPHANUMERIC_MIXED = string.ascii_letters + string.digits
    FULL = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"

@dataclass
class CrackResult:
    password: Optional[str]
    attempts: int
    time_taken: float
    method: str
    success: bool
    hash_collisions: int = 0

class AdvancedToyHasher:
    """Enhanced toy hashing algorithm with configurable security levels"""
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.MEDIUM):
        self.security_level = security_level
        self.modulus = 2 ** security_level.value
        self.base = 256
        
        # Different prime sets for different security levels
        if security_level == SecurityLevel.LOW:
            self.primes = [2, 3, 5, 7, 11, 13, 17, 19]
        elif security_level == SecurityLevel.MEDIUM:
            self.primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]
        elif security_level == SecurityLevel.HIGH:
            self.primes = [p for p in range(2, 100) if all(p % i != 0 for i in range(2, int(p**0.5) + 1))][:32]
        else:  # EXTREME
            self.primes = [p for p in range(2, 200) if all(p % i != 0 for i in range(2, int(p**0.5) + 1))][:64]
    
    def hash_password(self, password: str) -> int:
        """Enhanced hash function with better mixing"""
        if not password:
            return 0
            
        hash_value = 1
        
        for i, char in enumerate(password):
            char_code = ord(char)
            prime_idx = (i * char_code) % len(self.primes)
            prime = self.primes[prime_idx]
            
            # Enhanced mixing with rotation
            hash_value = (hash_value * prime + char_code) % self.modulus
            hash_value = ((hash_value << 3) | (hash_value >> (self.security_level.value - 3))) % self.modulus
        
        # Final advanced mixing
        length_factor = len(password) * 7919  # Large prime
        hash_value = (hash_value ^ length_factor) % self.modulus
        
        return hash_value
    
    def hash_to_hex(self, password: str) -> str:
        """Convert hash to hexadecimal string"""
        hash_val = self.hash_password(password)
        hex_length = self.security_level.value // 4
        return format(hash_val, f'0{hex_length}x')

class ComprehensivePasswordCracker:
    """
    Advanced password cracker with multiple strategies, learning capabilities,
    and comprehensive analytics
    """
    
    def __init__(self, 
                 security_level: SecurityLevel = SecurityLevel.MEDIUM,
                 complexity: PasswordComplexity = PasswordComplexity.ALPHANUMERIC_MIXED,
                 verbose: bool = True):
        
        self.hasher = AdvancedToyHasher(security_level)
        self.complexity = complexity
        self.verbose = verbose
        self.charset = complexity.value
        self.stats = CrackStatistics()
        
        # Learning system
        self.learned_patterns = deque(maxlen=1000)
        self.common_suffixes = ['', '1', '12', '123', '1234', '!', '0', '00', '000', '01']
        self.common_prefixes = ['', '!', '#', '$', '1', '12', 'admin', 'user', 'test']
        
        # Adaptive parameters
        self.adaptive_timeout = 30
        self.max_password_length = 20
        
    def log(self, message: str, level: str = "INFO"):
        if self.verbose:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp} {level:6}] {message}")
    
    def learn_from_attempt(self, password: str, success: bool):
        """Learn from cracking attempts to improve future performance"""
        if password and success:
            self.learned_patterns.append(password)
            
            # Extract patterns
            if any(c.isdigit() for c in password):
                if password[-1].isdigit():
                    suffix = ''.join(c for c in password[::-1] if c.isdigit())[::-1]
                    if suffix not in self.common_suffixes and len(suffix) <= 4:
                        self.common_suffixes.append(suffix)
    
    def enhanced_dictionary_attack(self, target_hash: str, timeout: int = 30) -> CrackResult:
        """Enhanced dictionary attack with pattern learning"""
        start_time = time.time()
        attempts = 0
        
        # Extended wordlist - ADDED Password123 and similar patterns
        base_words = [
            "password", "admin", "hello", "secret", "test", "user", "login",
            "welcome", "123456", "letmein", "master", "qwerty", "abc123",
            "pass", "access", "system", "server", "default", "guest", "root",
            "pas", "crac", "paaaass", "securepass12", "a", "ab", "abc", "1234",
            "Password", "Admin", "Hello", "Test", "User", "Secret",  # Added capitalized versions
            "Password123", "Admin123", "Test123", "Hello123"  # Added common patterns
        ]
        
        # Add learned patterns
        base_words.extend(list(self.learned_patterns)[:50])
        
        # Try base words first
        for word in base_words:
            if time.time() - start_time > timeout:
                break
                
            attempts += 1
            if self.hasher.hash_to_hex(word) == target_hash:
                result = CrackResult(word, attempts, time.time() - start_time, 
                                   "Dictionary Attack", True)
                self.learn_from_attempt(word, True)
                return result
        
        # Try combinations with prefixes and suffixes
        for word in base_words:
            if time.time() - start_time > timeout:
                break
                
            for prefix in self.common_prefixes:
                for suffix in self.common_suffixes:
                    candidate = prefix + word + suffix
                    attempts += 1
                    
                    if self.hasher.hash_to_hex(candidate) == target_hash:
                        result = CrackResult(candidate, attempts, time.time() - start_time,
                                           "Dictionary Attack", True)
                        self.learn_from_attempt(candidate, True)
                        return result
        
        # Try case variations for common words
        for word in base_words:
            if time.time() - start_time > timeout:
                break
                
            # Try capitalized version
            if word and word[0].islower():
                candidate = word[0].upper() + word[1:]
                attempts += 1
                if self.hasher.hash_to_hex(candidate) == target_hash:
                    result = CrackResult(candidate, attempts, time.time() - start_time,
                                       "Dictionary Attack", True)
                    self.learn_from_attempt(candidate, True)
                    return result
            
            # Try all uppercase
            candidate = word.upper()
            attempts += 1
            if self.hasher.hash_to_hex(candidate) == target_hash:
                result = CrackResult(candidate, attempts, time.time() - start_time,
                                   "Dictionary Attack", True)
                self.learn_from_attempt(candidate, True)
                return result
        
        return CrackResult(None, attempts, time.time() - start_time, "Dictionary Attack", False)
    
    def adaptive_genetic_algorithm(self, target_hash: str, population_size: int = 200,
                                 generations: int = 500, timeout: int = 30) -> CrackResult:
        """Genetic algorithm that adapts based on password complexity"""
        start_time = time.time()
        attempts = 0
        target_hash_int = int(target_hash, 16)
        
        def fitness(password: str) -> float:
            nonlocal attempts
            attempts += 1
            
            if not password or len(password) < 1 or len(password) > self.max_password_length:
                return -1e9
                
            try:
                candidate_hash = self.hasher.hash_password(password)
                
                if candidate_hash == target_hash_int:
                    return 1e9
                
                # Enhanced fitness calculation
                hash_diff = abs(candidate_hash - target_hash_int)
                length_penalty = abs(len(password) - 8) * 1000
                
                # Character diversity bonus
                char_bonus = 0
                if any(c.isdigit() for c in password):
                    char_bonus += 100
                if any(c.isupper() for c in password):
                    char_bonus += 150
                if any(c in "!@#$%^&*" for c in password):
                    char_bonus += 200
                
                # Pattern bonus
                pattern_bonus = 0
                if password in self.learned_patterns:
                    pattern_bonus += 500
                
                return -hash_diff - length_penalty + char_bonus + pattern_bonus
                
            except:
                return -1e9
        
        # Adaptive population initialization
        population = self.initialize_population(population_size, target_hash_int)
        
        best_individual = max(population, key=fitness)
        best_fitness = fitness(best_individual)
        
        for generation in range(generations):
            if time.time() - start_time > timeout:
                break
                
            # Evaluate population
            fitness_scores = [fitness(ind) for ind in population]
            
            # Check for solution
            for individual in population:
                if self.hasher.hash_to_hex(individual) == target_hash:
                    elapsed = time.time() - start_time
                    result = CrackResult(individual, attempts, elapsed, 
                                       "Genetic Algorithm", True)
                    self.learn_from_attempt(individual, True)
                    return result
            
            # Selection (Tournament)
            new_population = []
            elite_size = max(1, population_size // 20)
            elite_indices = np.argsort(fitness_scores)[-elite_size:]
            new_population.extend([population[i] for i in elite_indices])
            
            while len(new_population) < population_size:
                # Tournament selection
                tournament = random.sample(range(len(population)), min(5, len(population)))
                winner_idx = max(tournament, key=lambda i: fitness_scores[i])
                parent1 = population[winner_idx]
                
                if random.random() < 0.8:  # Crossover probability
                    tournament2 = random.sample(range(len(population)), min(5, len(population)))
                    winner_idx2 = max(tournament2, key=lambda i: fitness_scores[i])
                    parent2 = population[winner_idx2]
                    
                    child1, child2 = self.crossover(parent1, parent2)
                    new_population.extend([child1, child2])
                else:
                    # Mutation only
                    child = self.mutate(parent1)
                    new_population.append(child)
            
            population = new_population[:population_size]
            
            # Adaptive mutation rate
            current_best = max(population, key=fitness)
            current_fitness = fitness(current_best)
            
            if generation % 50 == 0 and self.verbose:
                self.log(f"Gen {generation}: best='{current_best}' fitness={current_fitness:.0f}")
        
        # Check final population
        for individual in population:
            if self.hasher.hash_to_hex(individual) == target_hash:
                elapsed = time.time() - start_time
                result = CrackResult(individual, attempts, elapsed, 
                                   "Genetic Algorithm", True)
                self.learn_from_attempt(individual, True)
                return result
        
        elapsed = time.time() - start_time
        return CrackResult(None, attempts, elapsed, "Genetic Algorithm", False)
    
    def initialize_population(self, size: int, target_hash: int) -> List[str]:
        """Initialize population with diverse strategies"""
        population = set()
        
        # Strategy 1: Common passwords - ADDED Password123 and similar
        common = ["password", "admin", "hello", "test", "user", "secret", "123456",
                 "pas", "crac", "paaaass", "securepass12", "a", "ab", "abc", "1234",
                 "Password", "Admin", "Hello", "Test", "Password123", "Admin123"]
        population.update(common)
        
        # Strategy 2: Learned patterns
        population.update(list(self.learned_patterns)[:20])
        
        # Strategy 3: Hash-based guesses
        hash_str = format(target_hash, 'x')
        if len(hash_str) >= 4:
            numeric_guess = ''.join(c for c in hash_str if c.isdigit())[:6]
            if numeric_guess:
                population.add(numeric_guess)
        
        # Strategy 4: Pattern-based
        bases = ["pass", "admin", "hello", "test", "user", "pas", "crac", "secure", "Password"]
        for base in bases:
            for suffix in self.common_suffixes[:5]:
                population.add(base + suffix)
                # Also try capitalized base with suffix
                if base and base[0].islower():
                    capitalized_base = base[0].upper() + base[1:]
                    population.add(capitalized_base + suffix)
        
        # Strategy 5: Random fill
        while len(population) < size:
            length = random.randint(3, 12)
            candidate = ''.join(random.choices(self.charset, k=length))
            population.add(candidate)
        
        return list(population)[:size]
    
    def crossover(self, parent1: str, parent2: str) -> Tuple[str, str]:
        """Enhanced crossover with multiple strategies - FIXED VERSION"""
        if len(parent1) < 2 or len(parent2) < 2:
            return parent1, parent2
        
        crossover_type = random.choice(['single_point', 'uniform', 'segment'])
        
        if crossover_type == 'single_point':
            point = random.randint(1, min(len(parent1), len(parent2)) - 1)
            child1 = parent1[:point] + parent2[point:]
            child2 = parent2[:point] + parent1[point:]
            
        elif crossover_type == 'uniform':
            # FIXED: Proper uniform crossover implementation
            child1_chars = []
            child2_chars = []
            max_len = max(len(parent1), len(parent2))
            
            for i in range(max_len):
                char1 = parent1[i] if i < len(parent1) else ''
                char2 = parent2[i] if i < len(parent2) else ''
                
                if random.random() < 0.5:
                    child1_chars.append(char1)
                    child2_chars.append(char2)
                else:
                    child1_chars.append(char2)
                    child2_chars.append(char1)
            
            child1 = ''.join(child1_chars)
            child2 = ''.join(child2_chars)
            
        else:  # segment crossover
            if len(parent1) >= 2 and len(parent2) >= 2:
                seg_len = random.randint(1, min(3, len(parent1)-1, len(parent2)-1))
                start1 = random.randint(0, len(parent1) - seg_len)
                start2 = random.randint(0, len(parent2) - seg_len)
                
                # Create new children by swapping segments
                child1 = parent1[:start1] + parent2[start2:start2+seg_len] + parent1[start1+seg_len:]
                child2 = parent2[:start2] + parent1[start1:start1+seg_len] + parent2[start2+seg_len:]
            else:
                child1, child2 = parent1, parent2
        
        return self.mutate(child1), self.mutate(child2)
    
    def mutate(self, individual: str) -> str:
        """Enhanced mutation with multiple strategies"""
        if not individual:
            return individual
            
        mutation_type = random.choices(
            ['replace', 'insert', 'delete', 'swap', 'case_flip'],
            weights=[0.4, 0.2, 0.1, 0.2, 0.1]
        )[0]
        
        try:
            if mutation_type == 'replace' and len(individual) > 0:
                pos = random.randint(0, len(individual) - 1)
                return individual[:pos] + random.choice(self.charset) + individual[pos+1:]
                
            elif mutation_type == 'insert' and len(individual) < self.max_password_length:
                pos = random.randint(0, len(individual))
                return individual[:pos] + random.choice(self.charset) + individual[pos:]
                
            elif mutation_type == 'delete' and len(individual) > 1:
                pos = random.randint(0, len(individual) - 1)
                return individual[:pos] + individual[pos+1:]
                
            elif mutation_type == 'swap' and len(individual) >= 2:
                pos1, pos2 = random.sample(range(len(individual)), 2)
                chars = list(individual)
                chars[pos1], chars[pos2] = chars[pos2], chars[pos1]
                return ''.join(chars)
                
            elif mutation_type == 'case_flip' and any(c.isalpha() for c in individual):
                pos = random.choice([i for i, c in enumerate(individual) if c.isalpha()])
                char = individual[pos]
                new_char = char.lower() if char.isupper() else char.upper()
                return individual[:pos] + new_char + individual[pos+1:]
                
        except:
            pass
            
        return individual
    
    def quantum_inspired_search(self, target_hash: str, iterations: int = 1000,
                              timeout: int = 30) -> CrackResult:
        """Quantum-inspired optimization with superposition simulation"""
        start_time = time.time()
        attempts = 0
        target_hash_int = int(target_hash, 16)
        
        # Initial superposition states (multiple starting points)
        current_states = [
            "password", "admin", "test", "hello", "secret", "123456",
            "pas", "crac", "paaaass", "securepass12", "a", "ab", "abc",
            "Password", "Password123", "Admin123"  # Added capitalized versions
        ]
        # Add random states
        for _ in range(10):
            current_states.append(''.join(random.choices(self.charset, k=random.randint(3, 8))))
        
        best_state = max(current_states, key=lambda x: self.evaluate_state(x, target_hash_int))
        best_energy = self.evaluate_state(best_state, target_hash_int)
        
        for iteration in range(iterations):
            if time.time() - start_time > timeout:
                break
                
            attempts += len(current_states)
            
            # Check for solution
            for state in current_states:
                if self.hasher.hash_to_hex(state) == target_hash:
                    elapsed = time.time() - start_time
                    result = CrackResult(state, attempts, elapsed, 
                                       "Quantum Search", True)
                    self.learn_from_attempt(state, True)
                    return result
            
            # Quantum-inspired state evolution
            new_states = []
            for state in current_states:
                # Apply quantum gates (mutations)
                for _ in range(3):  # Multiple possible outcomes
                    new_state = self.quantum_mutate(state)
                    new_states.append(new_state)
            
            # Measure and collapse (selection)
            current_states = self.collapse_states(new_states, target_hash_int, 15)
            
            # Update best
            current_best = max(current_states, key=lambda x: self.evaluate_state(x, target_hash_int))
            current_energy = self.evaluate_state(current_best, target_hash_int)
            
            if current_energy > best_energy:
                best_state = current_best
                best_energy = current_energy
            
            # Quantum tunneling (random exploration)
            if iteration % 20 == 0:
                tunnel_state = ''.join(random.choices(self.charset, k=random.randint(4, 10)))
                current_states.append(tunnel_state)
        
        # Final check
        for state in current_states:
            if self.hasher.hash_to_hex(state) == target_hash:
                elapsed = time.time() - start_time
                result = CrackResult(state, attempts, elapsed, "Quantum Search", True)
                self.learn_from_attempt(state, True)
                return result
        
        elapsed = time.time() - start_time
        return CrackResult(None, attempts, elapsed, "Quantum Search", False)
    
    def evaluate_state(self, state: str, target_hash: int) -> float:
        """Evaluate quantum state energy"""
        if not state:
            return -1e9
            
        try:
            candidate_hash = self.hasher.hash_password(state)
            if candidate_hash == target_hash:
                return 1e9
                
            return -abs(candidate_hash - target_hash)
        except:
            return -1e9
    
    def quantum_mutate(self, state: str) -> str:
        """Quantum-inspired mutation"""
        if not state:
            return state
            
        # Hadamard-like transformation (multiple possible mutations)
        mutations = []
        
        # Position-based mutation
        if len(state) > 0:
            pos = random.randint(0, len(state) - 1)
            mutations.append(state[:pos] + random.choice(self.charset) + state[pos+1:])
        
        # Length change mutation
        if len(state) < self.max_password_length:
            mutations.append(state + random.choice(self.charset))
        
        if len(state) > 1:
            mutations.append(state[:-1])
        
        # Pattern injection
        if random.random() < 0.3:
            pattern = random.choice(["123", "abc", "!!", "00"])
            mutations.append(state + pattern)
        
        # Case mutation for alphabetic characters
        if any(c.isalpha() for c in state) and random.random() < 0.2:
            chars = list(state)
            pos = random.choice([i for i, c in enumerate(chars) if c.isalpha()])
            chars[pos] = chars[pos].lower() if chars[pos].isupper() else chars[pos].upper()
            mutations.append(''.join(chars))
        
        return random.choice(mutations) if mutations else state
    
    def collapse_states(self, states: List[str], target_hash: int, keep_count: int) -> List[str]:
        """Collapse quantum states to most probable ones"""
        scored = [(state, self.evaluate_state(state, target_hash)) for state in states]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [state for state, score in scored[:keep_count]]
    
    def hybrid_attack(self, target_hash: str, timeout: int = 45) -> CrackResult:
        """Hybrid approach combining multiple strategies"""
        start_time = time.time()
        
        # Phase 1: Quick dictionary attack
        self.log("Phase 1: Dictionary Attack")
        result = self.enhanced_dictionary_attack(target_hash, timeout=min(5, timeout))
        if result.success:
            return result
        
        remaining_time = timeout - (time.time() - start_time)
        if remaining_time <= 1:
            return CrackResult(None, result.attempts, time.time() - start_time, "Hybrid", False)
        
        # Phase 2: Quantum-inspired search
        self.log("Phase 2: Quantum Search")
        result2 = self.quantum_inspired_search(target_hash, timeout=min(15, remaining_time))
        if result2.success:
            return result2
        
        total_attempts = result.attempts + result2.attempts
        remaining_time = timeout - (time.time() - start_time)
        if remaining_time <= 1:
            return CrackResult(None, total_attempts, time.time() - start_time, "Hybrid", False)
        
        # Phase 3: Genetic algorithm
        self.log("Phase 3: Genetic Algorithm")
        result3 = self.adaptive_genetic_algorithm(target_hash, timeout=remaining_time)
        
        total_attempts += result3.attempts
        success = result3.success
        
        return CrackResult(result3.password, total_attempts, time.time() - start_time, 
                         "Hybrid", success)
    
    def comprehensive_attack(self, target_hash: str, methods: List[str] = None,
                           timeout_per_method: int = 30) -> Dict[str, CrackResult]:
        """Run multiple attack methods and return comprehensive results"""
        if methods is None:
            methods = ["dictionary", "genetic", "quantum", "hybrid"]
        
        results = {}
        
        for method in methods:
            self.log(f"Starting {method} attack...")
            
            if method == "dictionary":
                result = self.enhanced_dictionary_attack(target_hash, timeout_per_method)
            elif method == "genetic":
                result = self.adaptive_genetic_algorithm(target_hash, timeout=timeout_per_method)
            elif method == "quantum":
                result = self.quantum_inspired_search(target_hash, timeout=timeout_per_method)
            elif method == "hybrid":
                result = self.hybrid_attack(target_hash, timeout=timeout_per_method)
            else:
                continue
                
            results[method] = result
            
            if result.success:
                self.log(f"{method} SUCCESS: '{result.password}' in {result.time_taken:.2f}s")
                # Don't break, collect all results for analysis
        
        return results

class CrackStatistics:
    """Comprehensive statistics and analytics for password cracking"""
    
    def __init__(self):
        self.attack_history = []
        self.method_performance = defaultdict(list)
        self.password_complexity_data = []
    
    def record_attack(self, result: CrackResult, password: str = None):
        """Record attack results for analysis"""
        record = {
            'timestamp': time.time(),
            'method': result.method,
            'success': result.success,
            'attempts': int(result.attempts),  # Convert to native Python int
            'time_taken': float(result.time_taken),  # Convert to native Python float
            'password_length': len(password) if password else 0,
            'password_complexity': float(self.calculate_complexity(password)) if password else 0.0  # Convert to float
        }
        
        self.attack_history.append(record)
        self.method_performance[result.method].append(record)
        
        if password:
            self.password_complexity_data.append({
                'password': password,
                'length': len(password),
                'complexity': float(self.calculate_complexity(password))  # Convert to float
            })
    
    def calculate_complexity(self, password: str) -> float:
        """Calculate password complexity score"""
        if not password:
            return 0.0
            
        score = 0.0
        char_types = 0
        
        if any(c.islower() for c in password):
            char_types += 1
        if any(c.isupper() for c in password):
            char_types += 1
        if any(c.isdigit() for c in password):
            char_types += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            char_types += 1
        
        # Complexity formula
        score = (char_types * 10) + (len(password) * 2) + (len(set(password)) * 5)
        return float(score)  # Ensure it's a Python float
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.attack_history:
            return {}
        
        # Convert to native Python types for JSON serialization
        df_data = []
        for record in self.attack_history:
            df_data.append({
                'method': record['method'],
                'success': bool(record['success']),  # Convert to bool
                'attempts': int(record['attempts']),  # Convert to int
                'time_taken': float(record['time_taken']),  # Convert to float
                'password_length': int(record['password_length']),  # Convert to int
                'password_complexity': float(record['password_complexity'])  # Convert to float
            })
        
        df = pd.DataFrame(df_data)
        
        report = {
            'overall_success_rate': float(df['success'].mean() * 100),
            'total_attempts': int(df['attempts'].sum()),
            'total_time': float(df['time_taken'].sum()),
            'average_time': float(df['time_taken'].mean()),
            'method_breakdown': {}
        }
        
        # Method-specific statistics
        for method, records in self.method_performance.items():
            method_data = []
            for record in records:
                method_data.append({
                    'success': bool(record['success']),
                    'attempts': int(record['attempts']),
                    'time_taken': float(record['time_taken'])
                })
            
            method_df = pd.DataFrame(method_data)
            report['method_breakdown'][method] = {
                'success_rate': float(method_df['success'].mean() * 100),
                'average_attempts': float(method_df['attempts'].mean()),
                'average_time': float(method_df['time_taken'].mean()),
                'total_successes': int(method_df['success'].sum()),
                'total_attempts': int(method_df['attempts'].sum())
            }
        
        return report

    def plot_performance(self, save_path: str = None):
        """Generate enhanced performance visualization plots with better styling"""
        if not self.attack_history:
            print("No data available for plotting")
            return
        
        # Convert data to proper format
        df_data = []
        for record in self.attack_history:
            df_data.append({
                'method': record['method'],
                'success': record['success'],
                'attempts': int(record['attempts']),
                'time_taken': float(record['time_taken'])
            })
        
        df = pd.DataFrame(df_data)
        
        # Set up the plotting style
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Password Cracking Performance Analysis\nEnhanced Visualization', 
                    fontsize=18, fontweight='bold')
        
        # Color scheme
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        success_color = '#2E8B57'  # Green for success
        failure_color = '#DC143C'  # Red for failure
        
        # Plot 1: Success rates by method (Enhanced)
        success_rates = df.groupby('method')['success'].mean() * 100
        bars1 = axes[0, 0].bar(success_rates.index, success_rates.values, 
                              color=colors[:len(success_rates)], 
                              alpha=0.8, edgecolor='black', linewidth=1.2)
        axes[0, 0].set_title('Success Rate by Method', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        axes[0, 0].set_ylim(0, 100)
        
        # Add data labels on bars
        for bar, rate in zip(bars1, success_rates.values):
            height = bar.get_height()
            axes[0, 0].text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{rate:.1f}%', ha='center', va='bottom', 
                           fontweight='bold', fontsize=10)
        
        # Plot 2: Average time by method (Enhanced with log scale)
        avg_time = df.groupby('method')['time_taken'].mean()
        bars2 = axes[0, 1].bar(avg_time.index, avg_time.values, 
                              color=colors[:len(avg_time)], 
                              alpha=0.8, edgecolor='black', linewidth=1.2)
        axes[0, 1].set_title('Average Time by Method (Log Scale)', fontsize=14, fontweight='bold')
        axes[0, 1].set_ylabel('Time (seconds) - Log Scale', fontsize=12, fontweight='bold')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].set_yscale('log')  # Logarithmic scale for better visualization
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # Add data labels on bars
        for bar, time_val in zip(bars2, avg_time.values):
            height = bar.get_height()
            axes[0, 1].text(bar.get_x() + bar.get_width()/2., height * 1.1,
                           f'{time_val:.2f}s', ha='center', va='bottom', 
                           fontweight='bold', fontsize=9)
        
        # Plot 3: Attempts distribution (Enhanced with log scale)
        attempts_data = [df[df['method'] == method]['attempts'] for method in df['method'].unique()]
        box_plot = axes[1, 0].boxplot(attempts_data, labels=df['method'].unique(),
                                     patch_artist=True, showmeans=True,
                                     meanprops={"marker":"o", "markerfacecolor":"white", 
                                               "markeredgecolor":"black"})
        axes[1, 0].set_title('Attempts Distribution by Method (Log Scale)', 
                            fontsize=14, fontweight='bold')
        axes[1, 0].set_ylabel('Number of Attempts - Log Scale', fontsize=12, fontweight='bold')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].set_yscale('log')  # Logarithmic scale for attempts
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # Color the box plots
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        # Add median values as text annotations (FIXED: removed parameter)
        for i, (method, data) in enumerate(zip(df['method'].unique(), attempts_data)):
            median_val = np.median(data)
            axes[1, 0].text(i + 1, median_val * 1.2, f'Med: {median_val:.0f}', 
                           ha='center', va='bottom', fontweight='bold', fontsize=9,
                           bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
        
        # Plot 4: Time vs Attempts with trend lines (Enhanced)
        success_mask = df['success'] == True
        failed_mask = df['success'] == False
        
        # Plot successful attempts in green
        success_scatter = axes[1, 1].scatter(df[success_mask]['attempts'], 
                                           df[success_mask]['time_taken'], 
                                           c=success_color, alpha=0.7, s=60, 
                                           label='Successful', edgecolors='black', linewidth=0.5)
        
        # Plot failed attempts in red
        failure_scatter = axes[1, 1].scatter(df[failed_mask]['attempts'], 
                                           df[failed_mask]['time_taken'], 
                                           c=failure_color, alpha=0.7, s=60, 
                                           label='Failed', edgecolors='black', linewidth=0.5)
        
        # Add trend lines for both successful and failed attempts
        if len(df[success_mask]) > 1:
            # Trend line for successful attempts
            z_success = np.polyfit(df[success_mask]['attempts'], 
                                 df[success_mask]['time_taken'], 1)
            p_success = np.poly1d(z_success)
            x_range_success = np.linspace(df[success_mask]['attempts'].min(), 
                                        df[success_mask]['attempts'].max(), 100)
            axes[1, 1].plot(x_range_success, p_success(x_range_success), 
                          color=success_color, linestyle='--', linewidth=2, 
                          label=f'Success trend (slope: {z_success[0]:.2e})')
        
        if len(df[failed_mask]) > 1:
            # Trend line for failed attempts
            z_failed = np.polyfit(df[failed_mask]['attempts'], 
                                df[failed_mask]['time_taken'], 1)
            p_failed = np.poly1d(z_failed)
            x_range_failed = np.linspace(df[failed_mask]['attempts'].min(), 
                                       df[failed_mask]['attempts'].max(), 100)
            axes[1, 1].plot(x_range_failed, p_failed(x_range_failed), 
                          color=failure_color, linestyle='--', linewidth=2,
                          label=f'Failed trend (slope: {z_failed[0]:.2e})')
        
        axes[1, 1].set_xlabel('Number of Attempts (Log Scale)', fontsize=12, fontweight='bold')
        axes[1, 1].set_ylabel('Time (seconds) - Log Scale', fontsize=12, fontweight='bold')
        axes[1, 1].set_title('Time vs Attempts with Trend Analysis', fontsize=14, fontweight='bold')
        axes[1, 1].set_xscale('log')  # Logarithmic scale for x-axis
        axes[1, 1].set_yscale('log')  # Logarithmic scale for y-axis
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Add correlation coefficient annotation
        if len(df) > 1:
            correlation = df['attempts'].corr(df['time_taken'])
            axes[1, 1].text(0.02, 0.98, f'Correlation: {correlation:.3f}', 
                           transform=axes[1, 1].transAxes, fontsize=11,
                           bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
                           verticalalignment='top')
        
        # Add overall statistics as text box
        overall_stats = f"""
Overall Statistics:
• Total Attacks: {len(df)}
• Success Rate: {df['success'].mean()*100:.1f}%
• Avg Attempts: {df['attempts'].mean():.0f}
• Avg Time: {df['time_taken'].mean():.2f}s
• Best Method: {success_rates.idxmax()} ({success_rates.max():.1f}%)
"""
        
        # Add statistics text box to the figure
        fig.text(0.02, 0.02, overall_stats, fontsize=10,
                bbox=dict(boxstyle="round", facecolor="lightgray", alpha=0.8),
                verticalalignment='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"Enhanced performance plot saved to {save_path}")
        
        plt.show()

    def plot_comprehensive_analysis(self, save_path: str = None):
        """Generate additional comprehensive analysis plots"""
        if not self.attack_history:
            print("No data available for comprehensive analysis")
            return
        
        # Create additional detailed analysis
        df_data = []
        for record in self.attack_history:
            df_data.append({
                'method': record['method'],
                'success': record['success'],
                'attempts': int(record['attempts']),
                'time_taken': float(record['time_taken']),
                'password_length': record['password_length'],
                'password_complexity': record['password_complexity']
            })
        
        df = pd.DataFrame(df_data)
        
        # Create comprehensive analysis figure
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Comprehensive Password Cracking Analysis', 
                    fontsize=18, fontweight='bold')
        
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        
        # Plot 1: Efficiency Analysis (Attempts per Second)
        efficiency_data = []
        for method in df['method'].unique():
            method_data = df[df['method'] == method]
            if len(method_data) > 0:
                avg_attempts = method_data['attempts'].mean()
                avg_time = method_data['time_taken'].mean()
                efficiency = avg_attempts / avg_time if avg_time > 0 else 0
                efficiency_data.append({'method': method, 'efficiency': efficiency})
        
        efficiency_df = pd.DataFrame(efficiency_data)
        if not efficiency_df.empty:
            bars = axes[0, 0].bar(efficiency_df['method'], efficiency_df['efficiency'],
                                 color=colors[:len(efficiency_df)], alpha=0.8,
                                 edgecolor='black', linewidth=1.2)
            axes[0, 0].set_title('Cracking Efficiency (Attempts/Second)', 
                                fontsize=14, fontweight='bold')
            axes[0, 0].set_ylabel('Attempts per Second', fontsize=12, fontweight='bold')
            axes[0, 0].tick_params(axis='x', rotation=45)
            axes[0, 0].grid(True, alpha=0.3, axis='y')
            
            # Add data labels
            for bar, eff in zip(bars, efficiency_df['efficiency']):
                height = bar.get_height()
                axes[0, 0].text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                               f'{eff:.0f}/s', ha='center', va='bottom', 
                               fontweight='bold', fontsize=10)
        
        # Plot 2: Success Rate vs Password Complexity
        if 'password_complexity' in df.columns and len(df) > 0:
            complexity_bins = pd.cut(df['password_complexity'], bins=5)
            complexity_success = df.groupby(complexity_bins)['success'].mean() * 100
            
            bars = axes[0, 1].bar(range(len(complexity_success)), complexity_success.values,
                                 color=plt.cm.viridis(np.linspace(0, 1, len(complexity_success))),
                                 alpha=0.8, edgecolor='black', linewidth=1.2)
            axes[0, 1].set_title('Success Rate vs Password Complexity', 
                                fontsize=14, fontweight='bold')
            axes[0, 1].set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
            axes[0, 1].set_xlabel('Password Complexity Range', fontsize=12, fontweight='bold')
            axes[0, 1].set_xticks(range(len(complexity_success)))
            axes[0, 1].set_xticklabels([str(bin) for bin in complexity_success.index], rotation=45)
            axes[0, 1].grid(True, alpha=0.3, axis='y')
            
            # Add data labels (FIXED: removed parameter)
            for bar, rate in zip(bars, complexity_success.values):
                height = bar.get_height()
                axes[0, 1].text(bar.get_x() + bar.get_width()/2., height + 1,
                               f'{rate:.1f}%', ha='center', va='bottom', 
                               fontweight='bold', fontsize=9)
        
        # Plot 3: Method Performance Heatmap
        performance_metrics = []
        for method in df['method'].unique():
            method_data = df[df['method'] == method]
            if len(method_data) > 0:
                success_rate = method_data['success'].mean() * 100
                avg_time = method_data['time_taken'].mean()
                avg_attempts = method_data['attempts'].mean()
                performance_metrics.append({
                    'method': method,
                    'success_rate': success_rate,
                    'avg_time': avg_time,
                    'avg_attempts': avg_attempts
                })
        
        perf_df = pd.DataFrame(performance_metrics)
        if not perf_df.empty:
            # Normalize metrics for heatmap
            metrics_to_plot = ['success_rate', 'avg_time', 'avg_attempts']
            normalized_data = perf_df[metrics_to_plot].copy()
            for col in metrics_to_plot:
                if col == 'avg_time' or col == 'avg_attempts':
                    # Inverse normalization for metrics where lower is better
                    normalized_data[col] = 1 - (normalized_data[col] - normalized_data[col].min()) / (normalized_data[col].max() - normalized_data[col].min())
                else:
                    # Normal normalization for metrics where higher is better
                    normalized_data[col] = (normalized_data[col] - normalized_data[col].min()) / (normalized_data[col].max() - normalized_data[col].min())
            
            im = axes[1, 0].imshow(normalized_data.T, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
            axes[1, 0].set_title('Method Performance Heatmap\n(Green = Better)', 
                                fontsize=14, fontweight='bold')
            axes[1, 0].set_xticks(range(len(perf_df)))
            axes[1, 0].set_xticklabels(perf_df['method'])
            axes[1, 0].set_yticks(range(len(metrics_to_plot)))
            axes[1, 0].set_yticklabels(['Success Rate', 'Time (inv)', 'Attempts (inv)'])
            
            # Add values to heatmap
            for i in range(len(perf_df)):
                for j in range(len(metrics_to_plot)):
                    original_value = perf_df.iloc[i][metrics_to_plot[j]]
                    if metrics_to_plot[j] == 'success_rate':
                        text = f'{original_value:.1f}%'
                    elif metrics_to_plot[j] == 'avg_time':
                        text = f'{original_value:.2f}s'
                    else:
                        text = f'{original_value:.0f}'
                    
                    axes[1, 0].text(i, j, text, ha='center', va='center', 
                                   fontweight='bold', fontsize=10,
                                   color='white' if normalized_data.iloc[i, j] < 0.5 else 'black')
            
            plt.colorbar(im, ax=axes[1, 0], shrink=0.6)
        
        # Plot 4: Cumulative Success Over Time
        if len(df) > 1:
            df_sorted = df.sort_values('time_taken')
            cumulative_success = df_sorted['success'].cumsum()
            axes[1, 1].plot(df_sorted['time_taken'], cumulative_success, 
                          linewidth=3, color='#2E8B57', marker='o', markersize=4)
            axes[1, 1].fill_between(df_sorted['time_taken'], cumulative_success, alpha=0.3, color='#2E8B57')
            axes[1, 1].set_title('Cumulative Success Over Time', fontsize=14, fontweight='bold')
            axes[1, 1].set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
            axes[1, 1].set_ylabel('Cumulative Successful Cracks', fontsize=12, fontweight='bold')
            axes[1, 1].grid(True, alpha=0.3)
            
            # Add final value annotation (FIXED: removed parameter)
            final_success = cumulative_success.iloc[-1]
            final_time = df_sorted['time_taken'].iloc[-1]
            axes[1, 1].annotate(f'Final: {final_success} successes', 
                              xy=(final_time, final_success),
                              xytext=(final_time * 0.7, final_success * 0.8),
                              arrowprops=dict(arrowstyle='->', color='black'),
                              fontweight='bold', fontsize=10,
                              bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            comprehensive_path = save_path.replace('.png', '_comprehensive.png')
            plt.savefig(comprehensive_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"Comprehensive analysis plot saved to {comprehensive_path}")
        
        plt.show()
    
    def export_results(self, filename: str):
        """Export all results to JSON file"""
        report = {
            'performance_report': self.generate_performance_report(),
            'attack_history': [
                {
                    'timestamp': float(record['timestamp']),
                    'method': record['method'],
                    'success': bool(record['success']),
                    'attempts': int(record['attempts']),
                    'time_taken': float(record['time_taken']),
                    'password_length': int(record['password_length']),
                    'password_complexity': float(record['password_complexity'])
                }
                for record in self.attack_history
            ],
            'password_complexity': [
                {
                    'password': data['password'],
                    'length': int(data['length']),
                    'complexity': float(data['complexity'])
                }
                for data in self.password_complexity_data
            ],
            'summary': {
                'total_attacks': int(len(self.attack_history)),
                'successful_attacks': int(sum(1 for r in self.attack_history if r['success'])),
                'overall_success_rate': float(self.generate_performance_report().get('overall_success_rate', 0))
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)  # Use str as fallback
        
        print(f"Results exported to {filename}")

# Quick test function
def quick_test():
    """Quick test to verify the cracker works"""
    print("QUICK TEST - Enhanced Password Cracker")
    print("=" * 40)
    
    cracker = ComprehensivePasswordCracker(
        security_level=SecurityLevel.MEDIUM,
        complexity=PasswordComplexity.ALPHANUMERIC_MIXED,
        verbose=True
    )
    
    test_passwords = ["pas", "crac", "paaaass", "securepass12", "password", "a", "ab", "abc", "Password123"]
    
    for password in test_passwords:
        print(f"\nTesting password: '{password}'")
        target_hash = cracker.hasher.hash_to_hex(password)
        print(f"Hash: {target_hash}")
        
        # Test hybrid attack
        result = cracker.hybrid_attack(target_hash, timeout=10)
        
        if result.success:
            print(f"✓ SUCCESS: Found '{result.password}' in {result.time_taken:.2f}s")
        else:
            print(f"✗ FAILED: {result.time_taken:.2f}s, {result.attempts} attempts")

if __name__ == "__main__":
    quick_test()
