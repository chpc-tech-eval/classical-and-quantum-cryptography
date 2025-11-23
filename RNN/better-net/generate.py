# generate.py
import torch
import numpy as np
from model import PasswordRNN
from data_prep import char_to_idx, idx_to_char, vocab_size

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load enhanced model
model = PasswordRNN(vocab_size).to(device)
model.load_state_dict(torch.load("password_rnn.pth", map_location=device))
model.eval()

def generate_password(seed="pass", length=12, temperature=0.8, max_attempts=5, top_k=20):
    """
    Generate password with temperature sampling and top-k filtering
    
    Args:
        seed: Starting characters
        length: Total password length
        temperature: Controls randomness (0.1 = deterministic, 1.0 = random)
        max_attempts: Maximum attempts to generate without newlines
        top_k: Only sample from top k most likely characters
    """
    
    for attempt in range(max_attempts):
        try:
            input_seq = torch.tensor([[char_to_idx.get(c, 0) for c in seed]], device=device)
            hidden = None
            result = seed

            for _ in range(length - len(seed)):
                output, hidden = model(input_seq, hidden)
                
                # Apply temperature
                output = output / temperature
                probs = torch.softmax(output, dim=-1).cpu().detach().numpy().flatten()

                # Top-k filtering
                if top_k is not None and top_k < len(probs):
                    top_k_indices = np.argpartition(probs, -top_k)[-top_k:]
                    top_k_probs = probs[top_k_indices]
                    # Renormalize
                    top_k_probs = top_k_probs / top_k_probs.sum()
                    
                    # Create new probability distribution with only top-k
                    new_probs = np.zeros_like(probs)
                    new_probs[top_k_indices] = top_k_probs
                    probs = new_probs

                # Ensure valid probability distribution
                probs = np.clip(probs, 1e-8, 1.0)  # Avoid zeros
                probs = probs / probs.sum()

                next_idx = np.random.choice(len(probs), p=probs)
                next_char = idx_to_char[next_idx]
                result += next_char
                input_seq = torch.tensor([[next_idx]], device=device)

            # Check if result contains unwanted newlines and meets basic criteria
            if '\n' not in result and len(result) >= 4:
                return result
        except Exception as e:
            print(f"Generation attempt {attempt + 1} failed: {e}")
            continue
    
    # If all attempts contain newlines or are too short, return a cleaned version
    clean_result = result.replace('\n', '').replace('\r', '')
    return clean_result if len(clean_result) >= 4 else clean_result + "123"

def generate_multiple_passwords(num_passwords=25, min_length=8, max_length=16):
    """Generate multiple passwords with varied lengths and seeds"""
    seeds = ["pass", "qwer", "abc", "123", "let", "admin", "test", "user", 
             "my", "secure", "key", "code", "access", "hello", "world"]
    
    print("Generated Passwords:\n" + "="*40)
    passwords = []
    
    for i in range(num_passwords):
        seed = np.random.choice(seeds)
        length = np.random.randint(min_length, max_length + 1)
        temp = np.random.uniform(0.5, 1.2)  # Vary temperature
        top_k = np.random.choice([10, 15, 20, 25, 30])  # Vary top-k
        
        pwd = generate_password(
            seed=seed, 
            length=length, 
            temperature=temp,
            top_k=top_k
        )
        
        passwords.append(pwd)
        print(f"{i+1:2d}. {pwd} (seed: '{seed}', temp: {temp:.2f}, top_k: {top_k})")
    
    return passwords

def analyze_passwords(passwords):
    """Analyze generated passwords for quality"""
    print("\nPassword Analysis:")
    print("=" * 40)
    
    if not passwords:
        return
    
    avg_length = sum(len(pwd) for pwd in passwords) / len(passwords)
    has_digit = sum(any(c.isdigit() for c in pwd) for pwd in passwords)
    has_upper = sum(any(c.isupper() for c in pwd) for pwd in passwords)
    has_special = sum(any(not c.isalnum() for c in pwd) for pwd in passwords)
    
    print(f"Total passwords: {len(passwords)}")
    print(f"Average length: {avg_length:.1f}")
    print(f"With digits: {has_digit}/{len(passwords)} ({has_digit/len(passwords)*100:.1f}%)")
    print(f"With uppercase: {has_upper}/{len(passwords)} ({has_upper/len(passwords)*100:.1f}%)")
    print(f"With special chars: {has_special}/{len(passwords)} ({has_special/len(passwords)*100:.1f}%)")

if __name__ == "__main__":
    passwords = generate_multiple_passwords()
    analyze_passwords(passwords)
