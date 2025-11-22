# qaoa_simulator.py
#!/usr/bin/env python3
"""
Enhanced QAOA Simulator for Password Cracking
"""

import numpy as np
from scipy.optimize import minimize
from typing import List, Tuple
import networkx as nx

class QAOASimulator:
    def __init__(self, hasher):
        self.hasher = hasher
    
    def create_cost_hamiltonian(self, target_hash: str, num_qubits: int, bit_length: int = 16):
        """
        Create cost Hamiltonian for the password cracking problem
        """
        def cost_function(bit_string):
            # Convert bit string to password
            charset = "abcdefghijklmnopqrstuvwxyz0123456789!@"
            password = self._bits_to_password(bit_string, charset)
            
            if not password:
                return 1000  # High cost for invalid passwords
            
            # Calculate hash difference
            candidate_hash = self.hasher.hash_password(password)
            target_hash_int = int(target_hash, 16)
            
            # Use lower bits for comparison
            target_bits = target_hash_int & ((1 << bit_length) - 1)
            candidate_bits = candidate_hash & ((1 << bit_length) - 1)
            
            # Hamming distance
            hamming_dist = bin(target_bits ^ candidate_bits).count('1')
            
            return hamming_dist
        
        return cost_function
    
    def _bits_to_password(self, bit_string: List[int], charset: str) -> str:
        """Convert bit string to password"""
        chars_per_char = 6
        password = ""
        
        for i in range(0, len(bit_string) - chars_per_char + 1, chars_per_char):
            char_bits = bit_string[i:i+chars_per_char]
            char_index = sum(bit * (2 ** (chars_per_char - 1 - j)) 
                           for j, bit in enumerate(char_bits))
            
            if char_index < len(charset):
                password += charset[char_index]
            else:
                return ""
        
        return password
    
    def qaoa_circuit(self, params: List[float], cost_hamiltonian, num_qubits: int, 
                    p: int = 1) -> float:
        """
        Simulate QAOA circuit and return expectation value
        """
        gamma, beta = params[:p], params[p:2*p]
        
        # Simple simulation: sample bit strings and compute expectation
        num_samples = 1000
        total_cost = 0
        
        for _ in range(num_samples):
            # Generate random bit string (simplified mixing)
            bit_string = np.random.choice([0, 1], size=num_qubits)
            
            # Apply cost function
            cost_val = cost_hamiltonian(bit_string)
            total_cost += cost_val
        
        return total_cost / num_samples
    
    def optimize_qaoa(self, target_hash: str, num_qubits: int = 24, 
                     p: int = 1, max_iter: int = 50) -> Tuple[str, float]:
        """
        Optimize QAOA parameters to find password
        """
        cost_hamiltonian = self.create_cost_hamiltonian(target_hash, num_qubits)
        
        # Initial parameters
        initial_params = np.random.uniform(0, np.pi, 2 * p)
        
        def objective(params):
            return self.qaoa_circuit(params, cost_hamiltonian, num_qubits, p)
        
        result = minimize(objective, initial_params, method='COBYLA', 
                         options={'maxiter': max_iter})
        
        # Find best candidate from final parameters
        best_bits = self._sample_from_qaoa(result.x, num_qubits, p)
        charset = "abcdefghijklmnopqrstuvwxyz0123456789!@"
        best_password = self._bits_to_password(best_bits, charset)
        
        return best_password, result.fun
    
    def _sample_from_qaoa(self, params: List[float], num_qubits: int, p: int) -> List[int]:
        """Sample bit string from optimized QAOA parameters"""
        # Simplified sampling - in real QAOA this would be quantum measurement
        num_samples = 100
        best_bits = None
        best_cost = float('inf')
        
        cost_hamiltonian = self.create_cost_hamiltonian("0" * 8, num_qubits)  # Dummy
        
        for _ in range(num_samples):
            bits = np.random.choice([0, 1], size=num_qubits)
            cost = cost_hamiltonian(bits)
            
            if cost < best_cost:
                best_cost = cost
                best_bits = bits
        
        return best_bits
