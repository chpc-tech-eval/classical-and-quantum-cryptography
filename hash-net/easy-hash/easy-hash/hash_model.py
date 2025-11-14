# hash_model.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class HashToPasswordRNN(nn.Module):
    def __init__(self, hash_dim=128, vocab_size=100, embed_dim=64, hidden_dim=256, num_layers=2):
        super().__init__()
        self.vocab_size = vocab_size
        self.hash_dim = hash_dim
        
        # Hash processing branch
        self.hash_encoder = nn.Sequential(
            nn.Linear(hash_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
        )
        
        # Character embedding
        self.char_embed = nn.Embedding(vocab_size, embed_dim)
        
        # LSTM that combines hash context and character sequence
        self.lstm = nn.LSTM(
            embed_dim + 128,  # char embedding + hash context
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0,
            bidirectional=False
        )
        
        # Output layer
        self.fc = nn.Linear(hidden_dim, vocab_size)
        
    def forward(self, char_sequence, hash_input, hidden=None):
        batch_size = char_sequence.size(0)
        
        # Encode the target hash
        hash_context = self.hash_encoder(hash_input)  # (batch, 128)
        hash_context_expanded = hash_context.unsqueeze(1)  # (batch, 1, 128)
        
        # Character embeddings
        char_embedded = self.char_embed(char_sequence)  # (batch, seq_len, embed_dim)
        
        # Combine hash context with character embeddings
        hash_context_repeated = hash_context_expanded.repeat(1, char_embedded.size(1), 1)
        lstm_input = torch.cat([char_embedded, hash_context_repeated], dim=-1)
        
        # LSTM processing
        lstm_out, hidden = self.lstm(lstm_input, hidden)
        
        # Output
        output = self.fc(lstm_out)  # (batch, seq_len, vocab_size)
        
        return output, hidden, hash_context

class HashCracker(nn.Module):
    """Wrapper model that handles the hash comparison objective"""
    def __init__(self, vocab_size, hash_function, hash_dim=128):
        super().__init__()
        self.hash_function = hash_function  # The hash function we're trying to "crack"
        self.rnn = HashToPasswordRNN(hash_dim, vocab_size)
        
    def forward(self, char_sequence, target_hash, hidden=None):
        # Generate password probabilities
        logits, hidden, hash_context = self.rnn(char_sequence, target_hash, hidden)
        return logits, hidden
    
    def compute_hash_loss(self, generated_password, target_hash):
        """Compute loss based on hash similarity"""
        # Convert generated password to actual hash
        generated_hash = self.hash_function(generated_password)
        
        # Compute similarity loss (we want these to match)
        hash_loss = F.mse_loss(generated_hash, target_hash)
        return hash_loss
