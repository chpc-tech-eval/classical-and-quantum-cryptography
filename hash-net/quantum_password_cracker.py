# quantum_password_cracker.py
#!/usr/bin/env python3
"""
Quantum Password Cracker using QAOA
Compares quantum-inspired approach with classical methods for hash reversal
"""

import numpy as np
import time
import hashlib
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
from generate_training_data_with_hashes import ToyHasher
import itertools

class QuantumPasswordCracker:
    def __init__(self, hasher=None):
        self.hasher = hasher or ToyHasher()
        self.password_cache = {}
        
    def classical_brute_force(self, target_hash: str, charset: str, max_length: int, 
                             timeout: int = 30) -> Tuple[str, int, float]:
        """
        Classical brute force attack
        """
        print(f"Starting classical brute force (max length: {max_length}, charset: {len(charset)} chars)")
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
                    elapsed = time.time() - start_time
                    return password, attempts, elapsed
        
        elapsed = time.time() - start_time
        return None, attempts, elapsed
    
    def classical_dictionary_attack(self, target_hash: str, wordlist: List[str], 
                                  timeout: int = 30) -> Tuple[str, int, float]:
        """
        Classical dictionary attack with common modifications
        """
        print(f"Starting dictionary attack ({len(wordlist)} words)")
        start_time = time.time()
        attempts = 0
        
        # Common modifications
        suffixes = ['', '1', '123', '!', '!!', '1234', '2023', '2024']
        prefixes = ['', '!', '#', '$']
        
        for base_word in wordlist:
            if time.time() - start_time > timeout:
                break
                
            for prefix in prefixes:
                for suffix in suffixes:
                    candidate = prefix + base_word + suffix
                    attempts += 1
                    
                    if self.hasher.hash_to_hex(candidate) == target_hash:
                        elapsed = time.time() - start_time
                        return candidate, attempts, elapsed
        
        elapsed = time.time() - start_time
        return None, attempts, elapsed
    
    def quantum_cost_function(self, password_bits: np.ndarray, target_hash: str, 
                            bit_length: int = 16) -> float:
        """
        Quantum cost function: minimizes difference between candidate hash and target hash
        """
        # Convert bits to password string
        charset = "abcdefghijklmnopqrstuvwxyz0123456789!@"
        password = self.bits_to_password(password_bits, charset)
        
        if not password:
            return float('inf')
        
        # Calculate hash
        candidate_hash = self.hasher.hash_password(password)
        
        # Convert to bit representation for comparison
        target_hash_int = int(target_hash, 16) if isinstance(target_hash, str) else target_hash
        target_bits = target_hash_int & ((1 << bit_length) - 1)
        candidate_bits = candidate_hash & ((1 << bit_length) - 1)
        
        # Hamming distance between hash bits
        hamming_dist = bin(target_bits ^ candidate_bits).count('1')
        
        return hamming_dist
    
    def bits_to_password(self, bits, charset):
	password = ""
	bits_per_char = int(math.log2(len(charset)))

	for i in range(0, len(bits), bits_per_char):
	    chunk = bits[i:i + bits_per_char]
	    if len(chunk) < bits_per_char:
	        break  # ignore incomplete chunk (shouldn't happen)
	        
	    char_index = int("".join(str(b) for b in chunk), 2)
	    char_index = char_index % len(charset)   # prevent crash
	        
	    password += charset[char_index]
	    
	return password
    
    def password_to_bits(self, password: str, charset: str, total_bits: int) -> np.ndarray:
        """
        Convert password to bit representation
        """
        bits = []
        chars_per_char = 6
        
        for char in password:
            if char in charset:
                index = charset.index(char)
                char_bits = [int(b) for b in format(index, f'0{chars_per_char}b')]
                bits.extend(char_bits)
            else:
                # Character not in charset, use zeros
                bits.extend([0] * chars_per_char)
        
        # Pad to total_bits
        while len(bits) < total_bits:
            bits.append(0)
        
        return np.array(bits[:total_bits])
    
    def qaoa_optimize(self, target_hash: str, bit_length: int = 16, num_qubits: int = 24,
                 max_iter: int = 100, num_shots: int = 1000, timeout: int = 30) -> Tuple[str, int, float]:
	    """
	    QAOA-inspired optimization for hash reversal
	    Uses classical optimization to simulate quantum behavior
	    """
	    print(f"Starting QAOA-inspired optimization ({num_qubits} qubits, {bit_length} hash bits)")
	    start_time = time.time()
	    
	    # Simplified QAOA simulation using classical optimization
	    from scipy.optimize import minimize
	    
	    charset = "abcdefghijklmnopqrstuvwxyz0123456789!@"
	    
	    def objective_function(x):
	        return self.quantum_cost_function(x, target_hash, bit_length)
	    
	    # Initial random guess
	    x0 = np.random.choice([0, 1], size=num_qubits)
	    
	    attempts = 0
	    best_password = None
	    best_cost = float('inf')
	    
	    for shot in range(num_shots):
	        if attempts >= max_iter or (time.time() - start_time) > timeout:
	            break
	            
	        # Random restart with local optimization
	        x0 = np.random.choice([0, 1], size=num_qubits)
	        result = minimize(objective_function, x0, method='Powell', 
	                        options={'maxiter': 10})
	        
	        attempts += 1
	        candidate_password = self.bits_to_password(np.round(result.x).astype(int), charset)
	        
	        if candidate_password and self.hasher.hash_to_hex(candidate_password) == target_hash:
	            elapsed = time.time() - start_time
	            return candidate_password, attempts, elapsed
	        
	        # Track best candidate
	        current_cost = result.fun
	        if current_cost < best_cost:
	            best_cost = current_cost
	            best_password = candidate_password
	    
	    elapsed = time.time() - start_time
	    return best_password, attempts, elapsed

    def genetic_algorithm_attack(self, target_hash: str, population_size: int = 100,
                               generations: int = 50, timeout: int = 30) -> Tuple[str, int, float]:
        """
        Genetic algorithm for hash reversal
        """
        print(f"Starting genetic algorithm (pop: {population_size}, gens: {generations})")
        start_time = time.time()
        charset = "abcdefghijklmnopqrstuvwxyz0123456789!@"
        attempts = 0
        
        def fitness(password):
            return -self.quantum_cost_function(
                self.password_to_bits(password, charset, 24), 
                target_hash, 16
            )
        
        # Initialize population
        population = []
        for _ in range(population_size):
            length = np.random.randint(4, 12)
            password = ''.join(np.random.choice(list(charset), length))
            population.append(password)
        
        for generation in range(generations):
            if time.time() - start_time > timeout:
                break
                
            # Evaluate fitness
            fitness_scores = [fitness(pwd) for pwd in population]
            attempts += len(population)
            
            # Check for solution
            for password in population:
                if self.hasher.hash_to_hex(password) == target_hash:
                    elapsed = time.time() - start_time
                    return password, attempts, elapsed
            
            # Selection (tournament)
            new_population = []
            for _ in range(population_size):
                # Tournament selection
                tournament = np.random.choice(len(population), 3, replace=False)
                winner = tournament[np.argmax([fitness_scores[i] for i in tournament])]
                new_population.append(population[winner])
            
            # Crossover and mutation
            population = []
            for i in range(0, len(new_population), 2):
                if i + 1 < len(new_population):
                    p1, p2 = new_population[i], new_population[i+1]
                    
                    # Crossover
                    crossover_point = np.random.randint(1, min(len(p1), len(p2)))
                    child1 = p1[:crossover_point] + p2[crossover_point:]
                    child2 = p2[:crossover_point] + p1[crossover_point:]
                    
                    # Mutation
                    if np.random.random() < 0.1:
                        pos = np.random.randint(len(child1))
                        child1 = child1[:pos] + np.random.choice(list(charset)) + child1[pos+1:]
                    
                    if np.random.random() < 0.1:
                        pos = np.random.randint(len(child2))
                        child2 = child2[:pos] + np.random.choice(list(charset)) + child2[pos+1:]
                    
                    population.extend([child1, child2])
                else:
                    population.append(new_population[i])
        
        elapsed = time.time() - start_time
        return None, attempts, elapsed

class ComparativeAnalyzer:
    def __init__(self, cracker):
        self.cracker = cracker
        self.results = {}
    
    def benchmark_attack(self, target_hash: str, original_password: str, 
                        methods: List[str], bit_sizes: List[int] = [16, 32, 64],
                        timeout: int = 60) -> Dict:
        """
        Benchmark different attack methods
        """
        print(f"\n Benchmarking attacks for hash: {target_hash}")
        print(f"   Original password: {original_password}")
        
        results = {}
        charset = "abcdefghijklmnopqrstuvwxyz0123456789!@"
        wordlist = ["password", "admin", "test", "user", "login", "secret", "hello", "welcome"]
        
        for method in methods:
            print(f"\n Method: {method}")
            method_results = {}
            
            for bit_size in bit_sizes:
                print(f"   Bit size: {bit_size}")
                
                if method == "brute_force":
                    result = self.cracker.classical_brute_force(
                        target_hash, charset, max_length=8, timeout=timeout
                    )
                elif method == "dictionary":
                    result = self.cracker.classical_dictionary_attack(
                        target_hash, wordlist, timeout=timeout
                    )
                elif method == "qaoa":
                    result = self.cracker.qaoa_optimize(
                        target_hash, bit_length=bit_size, timeout=timeout
                    )
                elif method == "genetic":
                    result = self.cracker.genetic_algorithm_attack(
                        target_hash, timeout=timeout
                    )
                else:
                    continue
                
                password, attempts, time_taken = result
                success = password == original_password
                
                method_results[bit_size] = {
                    'success': success,
                    'password_found': password,
                    'attempts': attempts,
                    'time_seconds': time_taken,
                    'attempts_per_second': attempts / time_taken if time_taken > 0 else 0
                }
                
                status = " SUCCESS" if success else " FAILED"
                print(f"     {status} | Time: {time_taken:.2f}s | Attempts: {attempts}")
            
            results[method] = method_results
        
        return results
    
    def plot_comparison(self, results: Dict, title: str = "Password Cracking Methods Comparison"):
        """
        Plot comparative results
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(title, fontsize=16)
        
        methods = list(results.keys())
        bit_sizes = list(next(iter(results.values())).keys())
        
        # Plot 1: Success Rate
        success_rates = []
        for method in methods:
            rates = []
            for bit_size in bit_sizes:
                success = results[method][bit_size]['success']
                rates.append(1 if success else 0)
            success_rates.append(rates)
        
        for i, method in enumerate(methods):
            axes[0, 0].plot(bit_sizes, success_rates[i], marker='o', label=method)
        axes[0, 0].set_title('Success Rate')
        axes[0, 0].set_xlabel('Hash Bit Size')
        axes[0, 0].set_ylabel('Success (1=Yes, 0=No)')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Plot 2: Time Taken
        for method in methods:
            times = [results[method][bit_size]['time_seconds'] for bit_size in bit_sizes]
            axes[0, 1].plot(bit_sizes, times, marker='o', label=method)
        axes[0, 1].set_title('Time Taken (seconds)')
        axes[0, 1].set_xlabel('Hash Bit Size')
        axes[0, 1].set_ylabel('Seconds')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Plot 3: Attempts Made
        for method in methods:
            attempts = [results[method][bit_size]['attempts'] for bit_size in bit_sizes]
            axes[1, 0].plot(bit_sizes, attempts, marker='o', label=method)
        axes[1, 0].set_title('Attempts Made')
        axes[1, 0].set_xlabel('Hash Bit Size')
        axes[1, 0].set_ylabel('Number of Attempts')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Plot 4: Attempts per Second
        for method in methods:
            aps = [results[method][bit_size]['attempts_per_second'] for bit_size in bit_sizes]
            axes[1, 1].plot(bit_sizes, aps, marker='o', label=method)
        axes[1, 1].set_title('Attempts per Second')
        axes[1, 1].set_xlabel('Hash Bit Size')
        axes[1, 1].set_ylabel('Attempts/Second')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig('cracking_comparison.png', dpi=150, bbox_inches='tight')
        plt.show()
    
    def generate_report(self, results: Dict, filename: str = "cracking_analysis_report.txt"):
        """
        Generate detailed analysis report
        """
        with open(filename, 'w') as f:
            f.write("Password Cracking Methods Comparative Analysis\n")
            f.write("=" * 50 + "\n\n")
            
            for method, method_results in results.items():
                f.write(f"Method: {method.upper()}\n")
                f.write("-" * 30 + "\n")
                
                for bit_size, result in method_results.items():
                    f.write(f"  Bit Size: {bit_size}\n")
                    f.write(f"    Success: {result['success']}\n")
                    f.write(f"    Password Found: {result['password_found']}\n")
                    f.write(f"    Time: {result['time_seconds']:.2f} seconds\n")
                    f.write(f"    Attempts: {result['attempts']}\n")
                    f.write(f"    Attempts/Second: {result['attempts_per_second']:.2f}\n\n")

def main():
    """
    Main demonstration and benchmarking function
    """
    print(" Quantum Password Cracker - Analysis")
    print("=" * 50)
    
    # Initialize
    cracker = QuantumPasswordCracker()
    analyzer = ComparativeAnalyzer(cracker)
    
    # Test passwords with their hashes
    test_cases = [
        ("password123", cracker.hasher.hash_to_hex("password123")),
        ("admin", cracker.hasher.hash_to_hex("admin")),
        ("hello123", cracker.hasher.hash_to_hex("hello123")),
        ("test2024", cracker.hasher.hash_to_hex("test2024")),
    ]
    
    all_results = {}
    
    for password, target_hash in test_cases[:2]:  # Test with first 2 for speed
        print(f"\n Target: {password} -> {target_hash}")
        
        results = analyzer.benchmark_attack(
            target_hash=target_hash,
            original_password=password,
            methods=["brute_force", "dictionary", "qaoa", "genetic"],
            bit_sizes=[16, 32],
            timeout=30
        )
        
        all_results[password] = results
    
    # Generate plots and reports
    for password, results in all_results.items():
        analyzer.plot_comparison(results, f"Password: {password}")
        analyzer.generate_report(results, f"report_{password}.txt")
    
    print("\n Analysis complete!")
    print(" Charts saved as 'cracking_comparison.png'")
    print(" Reports saved as 'report_*.txt'")

if __name__ == "__main__":
    main()
