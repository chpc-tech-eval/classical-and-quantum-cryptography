# model.py
import torch
import torch.nn as nn

class PasswordRNN(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=256, num_layers=2, dropout=0.2):
        super().__init__()
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # Embedding layer
        self.embed = nn.Embedding(vocab_size, embed_dim)
        
        # Multi-layer LSTM with dropout
        self.lstm = nn.LSTM(
            embed_dim, 
            hidden_dim, 
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=False
        )
        
        # Dropout for regularization
        self.dropout = nn.Dropout(dropout)
        
        # Output layer
        self.fc = nn.Linear(hidden_dim, vocab_size)
        
    def forward(self, x, hidden=None):
        # Embedding
        x = self.embed(x)
        
        # LSTM
        lstm_out, hidden = self.lstm(x, hidden)
        
        # Apply dropout to last output
        lstm_out = self.dropout(lstm_out[:, -1, :])
        
        # Final output
        out = self.fc(lstm_out)
        
        return out, hidden
    
    def init_hidden(self, batch_size, device):
        """Initialize hidden state"""
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_dim).to(device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_dim).to(device)
        return (h0, c0)
