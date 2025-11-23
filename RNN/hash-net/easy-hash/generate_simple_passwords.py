# generate_simple_passwords.py
import random
import string
import torch
from simple_hash import SimpleHashFunction

def generate_simple_passwords_with_hashes(count=5000):
    """Generate simple passwords and immediately create training data with hashes"""
    hash_function = SimpleHashFunction()
    passwords = []
    
    # Simple patterns that the trivial hash can easily encode
    base_words = ['test', 'pass', 'hello', 'admin', 'user', 'login', 'secret', 'welcome']
    numbers = ['123', '111', '000', '456', '789', '321', '555', '999']
    
    for i in range(count):
        # Simple pattern: word + numbers
        if random.random() < 0.7:
            word = random.choice(base_words)
            num = random.choice(numbers)
            password = word + num
        # Simple pattern: numbers + word  
        elif random.random() < 0.5:
            word = random.choice(base_words)
            num = random.choice(numbers)
            password = num + word
        # Very simple pattern
        else:
            length = random.randint(6, 10)
            chars = string.ascii_lowercase + string.digits
            password = ''.join(random.choice(chars) for _ in range(length))
        
        passwords.append(password)
    
    # Create character mappings from the generated passwords
    all_text = ''.join(passwords)
    chars = sorted(list(set(all_text)))
    char_to_idx = {ch: i for i, ch in enumerate(chars)}
    idx_to_char = {i: ch for i, ch in enumerate(chars)}
    vocab_size = len(chars)
    
    print(f"Generated {len(passwords)} passwords")
    print(f"Vocabulary: {vocab_size} characters")
    print(f"Character set: {''.join(chars)}")
    
    # Create training pairs directly
    training_pairs = create_training_pairs(passwords, char_to_idx, idx_to_char, hash_function)
    
    return passwords, training_pairs, char_to_idx, idx_to_char, vocab_size

def create_training_pairs(passwords, char_to_idx, idx_to_char, hash_function, seq_length=10):
    """Create training pairs: (target_hash, password_sequence)"""
    pairs = []
    
    for password in passwords:
        if len(password) < 6:  # Skip very short passwords
            continue
            
        # Create target hash
        target_hash = hash_function.actual_hash(password)
        
        # Convert password to character sequences
        encoded = [char_to_idx.get(c, 0) for c in password]
        
        # Create overlapping sequences
        if len(encoded) > seq_length:
            for i in range(len(encoded) - seq_length):
                seq = encoded[i:i+seq_length]
                target_char = encoded[i+seq_length]
                
                pairs.append({
                    'target_hash': target_hash,
                    'input_sequence': seq,
                    'target_char': target_char,
                    'full_password': password
                })
    
    print(f"Created {len(pairs)} training pairs")
    
    # Show some samples
    if pairs:
        print("Sample training pairs:")
        for i in range(min(3, len(pairs))):
            pair = pairs[i]
            target_char = idx_to_char.get(pair['target_char'], '?')
            print(f"  '{pair['full_password']}' -> target: '{target_char}'")
    
    return pairs

# Make the data globally available
passwords, training_pairs, char_to_idx, idx_to_char, vocab_size = generate_simple_passwords_with_hashes(5000)

if __name__ == "__main__":
    print(f"\n✅ Data generation complete!")
    print(f"   Passwords: {len(passwords)}")
    print(f"   Training pairs: {len(training_pairs)}")
    print(f"   Vocabulary size: {vocab_size}")
    print(f"   Sample passwords: {passwords[:5]}")
