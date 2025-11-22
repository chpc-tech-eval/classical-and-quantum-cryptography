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

# Filter passwords by length - only use longer passwords
min_password_length = 8
filtered_passwords = [pwd for pwd in passwords if len(pwd) >= min_password_length]
print(f"Using {len(filtered_passwords)} passwords with length >= {min_password_length}")

# Create character set and mappings from ALL passwords
all_text = ''.join(filtered_passwords)
chars = sorted(list(set(all_text)))
char_to_idx = {ch: i for i, ch in enumerate(chars)}
idx_to_char = {i: ch for i, ch in enumerate(chars)}
vocab_size = len(chars)

print(f"Vocabulary: {vocab_size} characters")
print(f"Character set: {''.join(chars)}")

def create_hash_password_pairs(passwords, seq_length=10):
    """Create training pairs: (target_hash, password_sequence)"""
    hash_function = SimpleHashFunction()
    pairs = []
    
    for password in passwords:
        # Create target hash
        target_hash = hash_function.actual_hash(password)
        
        # Convert password to character sequences
        encoded = [char_to_idx.get(c, 0) for c in password]
        
        # Create multiple training examples from each password
        # Use sliding window approach
        for i in range(len(encoded) - seq_length):
            seq = encoded[i:i+seq_length]
            target_char = encoded[i+seq_length]
            
            pairs.append({
                'target_hash': target_hash,
                'input_sequence': seq,
                'target_char': target_char,
                'full_password': password
            })
    
    return pairs

# Create training pairs
training_pairs = create_hash_password_pairs(filtered_passwords, seq_length=8)

print(f"Created {len(training_pairs)} training pairs")

if len(training_pairs) > 0:
    # Show samples with diverse target characters
    print(f"\nSample training pairs (showing target character diversity):")
    seen_chars = set()
    samples_shown = 0
    
    for pair in training_pairs:
        if pair['target_char'] not in seen_chars and pair['target_char'] in idx_to_char:
            seen_chars.add(pair['target_char'])
            print(f"  Password: {pair['full_password']}")
            print(f"  Target char: '{idx_to_char[pair['target_char']]}' (index: {pair['target_char']})")
            samples_shown += 1
            if samples_shown >= 5:
                break
