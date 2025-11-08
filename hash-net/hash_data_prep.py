# hash_data_prep.py
import torch
import numpy as np
import re
from simple_hash import SimpleHashFunction

def clean_text(text):
    """Remove excessive newlines and clean the text"""
    text = re.sub(r'\n+', '\n', text)
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    return '\n'.join(lines)

# Load and clean data
with open("passwords.txt", "r", encoding="utf-8") as f:
    passwords = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(passwords)} passwords")

# Create character set and mappings from ALL passwords
all_text = ''.join(passwords)
chars = sorted(list(set(all_text)))
char_to_idx = {ch: i for i, ch in enumerate(chars)}
idx_to_char = {i: ch for i, ch in enumerate(chars)}
vocab_size = len(chars)

print(f"Vocabulary: {vocab_size} characters")
print(f"Character set: {''.join(chars)}")

def create_hash_password_pairs(passwords, seq_length=20):
    """Create training pairs: (target_hash, password_sequence)"""
    hash_function = SimpleHashFunction()
    pairs = []
    
    for password in passwords:
        if len(password) < 4:  # Skip very short passwords
            continue
            
        # Create target hash
        target_hash = hash_function.actual_hash(password)
        
        # Convert password to character sequences
        encoded = [char_to_idx.get(c, 0) for c in password]
        
        # Only create sequences if password is long enough
        if len(encoded) > seq_length:
            # Create overlapping sequences
            for i in range(len(encoded) - seq_length):
                seq = encoded[i:i+seq_length]
                target_char = encoded[i+seq_length]
                
                pairs.append({
                    'target_hash': target_hash,
                    'input_sequence': seq,
                    'target_char': target_char,
                    'full_password': password
                })
        else:
            # For short passwords, pad and create at least one sequence
            seq = encoded[:seq_length]
            # Pad if necessary
            if len(seq) < seq_length:
                seq = seq + [0] * (seq_length - len(seq))
            target_char = 0  # Use padding index as target
            
            pairs.append({
                'target_hash': target_hash,
                'input_sequence': seq,
                'target_char': target_char,
                'full_password': password
            })
    
    return pairs

# Create training pairs
training_pairs = create_hash_password_pairs(passwords)

print(f"Created {len(training_pairs)} training pairs")

if len(training_pairs) > 0:
    print(f"Sample training pair:")
    sample = training_pairs[0]
    print(f"  Password: {sample['full_password']}")
    print(f"  Input sequence length: {len(sample['input_sequence'])}")
    print(f"  Target char: {idx_to_char[sample['target_char']] if sample['target_char'] in idx_to_char else 'PAD'}")
    print(f"  Target hash shape: {sample['target_hash'].shape}")
else:
    print("WARNING: No training pairs created! Check your passwords.txt file")
