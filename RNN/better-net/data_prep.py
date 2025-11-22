# data_prep.py
import torch
import numpy as np
import re

def clean_text(text):
    """Remove excessive newlines and clean the text"""
    # Replace multiple newlines with single newlines
    text = re.sub(r'\n+', '\n', text)
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    # Filter out empty lines
    lines = [line for line in lines if line]
    return '\n'.join(lines)

# Load and clean data
with open("passwords.txt", "r", encoding="utf-8") as f:
    text = f.read().lower()
    text = clean_text(text)

print(f"Total characters: {len(text)}")
print(f"First 100 chars: {repr(text[:100])}")

# Create character set and mappings
chars = sorted(list(set(text)))
char_to_idx = {ch: i for i, ch in enumerate(chars)}
idx_to_char = {i: ch for i, ch in enumerate(chars)}

vocab_size = len(chars)
print(f"Unique characters: {vocab_size}")
print(f"Character set: {''.join(chars)}")

# Convert to integers
encoded = np.array([char_to_idx[c] for c in text])

# Create sequences with improved batching
seq_length = 30  # Increased sequence length for better context
sequences = []
targets = []

for i in range(len(encoded) - seq_length):
    seq = encoded[i:i+seq_length]
    target = encoded[i+seq_length]
    sequences.append(seq)
    targets.append(target)

# Convert to tensors and create train/validation split
x = torch.tensor(sequences, dtype=torch.long)
y = torch.tensor(targets, dtype=torch.long)

# Shuffle and split
indices = torch.randperm(len(x))
split_idx = int(0.8 * len(x))  # 80% train, 20% validation

x_train, x_val = x[indices[:split_idx]], x[indices[split_idx:]]
y_train, y_val = y[indices[:split_idx]], y[indices[split_idx:]]

print(f"Training set: {x_train.shape}")
print(f"Validation set: {x_val.shape}")
