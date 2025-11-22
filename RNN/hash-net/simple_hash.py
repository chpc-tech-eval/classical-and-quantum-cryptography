# simple_hash.py
import torch
import hashlib
import numpy as np
import torch.nn as nn

class SimpleHashFunction:
    """A simple deterministic hash function for educational purposes"""
    
    def __init__(self, output_dim=128, device='cpu'):
        self.output_dim = output_dim
        self.device = device
        self.hash_proj = None  # Initialize later when we know vocab_size
        
    def init_projection(self, vocab_size):
        """Initialize the projection layer when we know the vocabulary size"""
        self.hash_proj = nn.Linear(vocab_size, self.output_dim).to(self.device)
        
    def __call__(self, password):
        """Convert password to fixed-length hash vector"""
        if isinstance(password, torch.Tensor):
            # During training - we need differentiable approximation
            return self.differentiable_hash(password)
        else:
            # For evaluation - actual hash
            return self.actual_hash(password)
    
    def actual_hash(self, password):
        """Actual non-differentiable hash (for validation)"""
        if isinstance(password, str):
            # String input
            hash_obj = hashlib.sha256(password.encode())
            hash_hex = hash_obj.hexdigest()
        else:
            # Assume it's a list of character indices or similar
            try:
                if isinstance(password, list):
                    # Convert list of indices back to string
                    from hash_data_prep import idx_to_char
                    password_str = ''.join([idx_to_char.get(i, '') for i in password])
                else:
                    password_str = str(password)
                hash_obj = hashlib.sha256(password_str.encode())
                hash_hex = hash_obj.hexdigest()
            except:
                # Fallback
                hash_hex = hashlib.sha256(str(password).encode()).hexdigest()
        
        # Convert to fixed-length vector
        hash_int = int(hash_hex[:32], 16)  # Use first 32 hex chars
        hash_vector = torch.tensor([(hash_int >> i) & 1 for i in range(self.output_dim)], 
                                  dtype=torch.float32).to(self.device)
        return hash_vector
    
    def differentiable_hash(self, password_logits):
        """Differentiable approximation of hash for training"""
        if self.hash_proj is None:
            vocab_size = password_logits.size(-1)
            self.init_projection(vocab_size)
            
        # This is a learned approximation - the model learns to mimic hash patterns
        batch_size, seq_len, vocab_size = password_logits.shape
        
        # Take the most likely character at each position
        password_probs = torch.softmax(password_logits, dim=-1)
        
        # Create a simple transformation that the model can learn to invert
        # This is essentially learning the "hash pattern"
        hash_approx = torch.mean(password_probs, dim=1)  # (batch, vocab_size)
        
        # Project to output dimension
        hash_approx = self.hash_proj(hash_approx)
        
        return torch.sigmoid(hash_approx)  # Normalize to [0,1]
