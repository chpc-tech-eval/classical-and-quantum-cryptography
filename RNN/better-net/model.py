# model.py
import torch
import torch.nn as nn

class PasswordRNN(nn.Module):
    def __init__(self, vocab_size, embed_dim=256, hidden_dim=512, num_layers=3, dropout=0.3):
        super().__init__()
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # Embedding layer with larger dimension
        self.embed = nn.Embedding(vocab_size, embed_dim)
        
        # Multi-layer LSTM with dropout and batch normalization
        self.lstm = nn.LSTM(
            embed_dim, 
            hidden_dim, 
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=False
        )
        
        # Layer normalization for better training stability
        self.layer_norm = nn.LayerNorm(hidden_dim)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(dropout)
        
        # Additional fully connected layer for more capacity
        self.fc1 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc2 = nn.Linear(hidden_dim // 2, vocab_size)
        
        # Activation
        self.relu = nn.ReLU()
        
    def forward(self, x, hidden=None):
        batch_size = x.size(0)
        
        # Embedding
        x = self.embed(x)
        
        # LSTM
        lstm_out, hidden = self.lstm(x, hidden)
        
        # Use the last output only
        lstm_out = lstm_out[:, -1, :]
        
        # Layer normalization and dropout
        lstm_out = self.layer_norm(lstm_out)
        lstm_out = self.dropout(lstm_out)
        
        # Additional fully connected layers
        fc_out = self.relu(self.fc1(lstm_out))
        fc_out = self.dropout(fc_out)
        
        # Final output
        out = self.fc2(fc_out)
        
        return out, hidden
    
    def init_hidden(self, batch_size, device):
        """Initialize hidden state"""
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_dim).to(device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_dim).to(device)
        return (h0, c0)
