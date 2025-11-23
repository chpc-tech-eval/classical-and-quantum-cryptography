# simple_hash.py
import torch
import torch.nn as nn

class SimpleHashFunction:
    """Extremely simple hash that's trivial to invert"""
    
    def __init__(self, output_dim=16, device='cpu'):
        self.output_dim = output_dim
        self.device = device
        
    def actual_hash(self, password):
        """Super simple hash: just encode character positions"""
        if isinstance(password, str):
            from hash_data_prep import char_to_idx
            indices = [char_to_idx.get(c, 0) for c in password]
        else:
            indices = password
            
        hash_vector = torch.zeros(self.output_dim, device=self.device)
        
        # Trivial encoding: each character affects one position
        for i, char_idx in enumerate(indices):
            if i < self.output_dim:
                hash_vector[i] = (char_idx + 1) / 72.0  # Normalized character
        
        # Add length info
        if len(indices) < self.output_dim:
            hash_vector[len(indices)] = 1.0
            
        return hash_vector
    
    def differentiable_hash(self, password_logits):
        """Even simpler differentiable version"""
        batch_size, seq_len, vocab_size = password_logits.shape
        
        # Just take the most likely character at each position
        _, predicted_chars = torch.max(password_logits, dim=-1)
        
        # Convert to the same simple hash format
        hash_vectors = []
        for i in range(batch_size):
            hash_vec = torch.zeros(self.output_dim, device=self.device)
            for j, char_idx in enumerate(predicted_chars[i]):
                if j < self.output_dim:
                    hash_vec[j] = (char_idx + 1) / 72.0
            hash_vectors.append(hash_vec)
            
        return torch.stack(hash_vectors)

    def __call__(self, password):
        return self.actual_hash(password)
