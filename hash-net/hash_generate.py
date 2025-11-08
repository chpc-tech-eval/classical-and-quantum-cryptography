# hash_generate.py
import torch
import numpy as np
from hash_model import HashCracker
from hash_data_prep import char_to_idx, idx_to_char, vocab_size
from simple_hash import SimpleHashFunction

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load trained model
hash_function = SimpleHashFunction()
model = HashCracker(vocab_size, hash_function).to(device)
model.load_state_dict(torch.load("hash_cracker_rnn.pth", map_location=device))
model.eval()

def crack_hash(target_hash, max_length=20, temperature=0.8):
    """Generate password that likely produces the target hash"""
    input_seq = torch.tensor([[char_to_idx['p']]], device=device)  # Start with 'p'
    hidden = None
    result = "p"
    target_hash = target_hash.unsqueeze(0).to(device)
    
    for _ in range(max_length - 1):
        with torch.no_grad():
            char_logits, hidden = model(input_seq, target_hash, hidden)
            
            # Sample next character with temperature
            probs = torch.softmax(char_logits[0, -1] / temperature, dim=-1)
            next_idx = torch.multinomial(probs, 1).item()
            next_char = idx_to_char[next_idx]
            
            result += next_char
            input_seq = torch.tensor([[next_idx]], device=device)
            
            # Stop conditions
            if next_char in ['\n', ' '] or len(result) >= max_length:
                break
    
    return result

def crack_hashes_from_file(hash_file, num_passwords=10):
    """Attempt to crack multiple hashes from file"""
    # This would read actual hashes from your hash files
    # For demonstration, we'll generate some test hashes
    
    test_passwords = ["password123", "admin2024", "secret!!", "letmein", "hello123"]
    hash_function = SimpleHashFunction()
    
    print("Hash Cracking Results:\n" + "="*40)
    
    for i, pwd in enumerate(test_passwords[:num_passwords]):
        target_hash = hash_function.actual_hash(pwd)
        cracked = crack_hash(target_hash)
        
        # Verify
        cracked_hash = hash_function.actual_hash(cracked)
        match = torch.allclose(target_hash, cracked_hash, atol=0.1)
        
        print(f"{i+1:2d}. Target: '{pwd}'")
        print(f"     Cracked: '{cracked}'")
        print(f"     Match: {match}")
        print()

if __name__ == "__main__":
    crack_hashes_from_file("custom_password_hashes.txt")

