# hash_model.py
import torch
import torch.nn as nn

class HashToPasswordRNN(nn.Module):
    def __init__(self, hash_dim=16, vocab_size=100, embed_dim=16, hidden_dim=32):
        super().__init__()
        self.vocab_size = vocab_size
        
        # Minimal architecture
        self.hash_encoder = nn.Linear(hash_dim, 16)
        self.char_embed = nn.Embedding(vocab_size, embed_dim)
        
        self.lstm = nn.LSTM(
            embed_dim + 16,
            hidden_dim,
            batch_first=True,
        )
        
        self.fc = nn.Linear(hidden_dim, vocab_size)
        
    def forward(self, char_sequence, hash_input, hidden=None):
        # Encode hash
        hash_context = self.hash_encoder(hash_input).unsqueeze(1)
        
        # Character embeddings
        char_embedded = self.char_embed(char_sequence)
        
        # Combine
        hash_context_repeated = hash_context.repeat(1, char_embedded.size(1), 1)
        lstm_input = torch.cat([char_embedded, hash_context_repeated], dim=-1)
        
        # LSTM
        lstm_out, hidden = self.lstm(lstm_input, hidden)
        
        # Output
        out = self.fc(lstm_out)
        
        return out, hidden

class HashCracker(nn.Module):
    def __init__(self, vocab_size, hash_function, hash_dim=16):
        super().__init__()
        self.hash_function = hash_function
        self.rnn = HashToPasswordRNN(hash_dim, vocab_size)
        
    def forward(self, char_sequence, target_hash, hidden=None):
        logits, hidden = self.rnn(char_sequence, target_hash, hidden)
        return logits, hidden
