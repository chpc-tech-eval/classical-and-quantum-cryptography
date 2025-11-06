# data_prep.py
import torch
import numpy as np

# Load data
with open("passwords.txt", "r", encoding="utf-8") as f:
    text = f.read().lower()

# Create character set and mappings
chars = sorted(list(set(text)))
char_to_idx = {ch: i for i, ch in enumerate(chars)}
idx_to_char = {i: ch for ch, i in char_to_idx.items()}

vocab_size = len(chars)
print("Unique chars:", vocab_size)

# Convert to integers
encoded = np.array([char_to_idx[c] for c in text])

# Create sequences
seq_length = 20  # number of chars per training example
sequences = []
targets = []

for i in range(len(encoded) - seq_length):
    seq = encoded[i:i+seq_length]
    target = encoded[i+seq_length]
    sequences.append(seq)
    targets.append(target)

x = torch.tensor(sequences)
y = torch.tensor(targets)
print("Dataset size:", x.shape)
