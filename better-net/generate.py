# generate.py
import torch
import numpy as np
from model import PasswordRNN
from data_prep import char_to_idx, idx_to_char, vocab_size

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
model = PasswordRNN(vocab_size).to(device)
model.load_state_dict(torch.load("password_rnn.pth"))
model.eval()

def generate_password(seed="pass", length=12, temperature=0.8, max_attempts=3):
    """
    Generate password with temperature sampling
    
    Args:
        seed: Starting characters
        length: Total password length
        temperature: Controls randomness (0.1 = deterministic, 1.0 = random)
        max_attempts: Maximum attempts to generate without newlines
    """
    
    for attempt in range(max_attempts):
        input_seq = torch.tensor([[char_to_idx.get(c, 0) for c in seed]], device=device)
        hidden = None
        result = seed

        for _ in range(length - len(seed)):
            output, hidden = model(input_seq, hidden)
            probs = torch.softmax(output / temperature, dim=-1).cpu().detach().numpy().flatten()

            # Ensure valid probability distribution
            probs = np.clip(probs, 1e-8, 1.0)  # Avoid zeros
            probs = probs / probs.sum()

            next_idx = np.random.choice(len(probs), p=probs)
            next_char = idx_to_char[next_idx]
            result += next_char
            input_seq = torch.tensor([[next_idx]], device=device)

        # Check if result contains unwanted newlines
        if '\n' not in result:
            return result
    
    # If all attempts contain newlines, return the last one and remove newlines
    return result.replace('\n', '')

def generate_multiple_passwords(num_passwords=20, min_length=8, max_length=15):
    """Generate multiple passwords with varied lengths and seeds"""
    seeds = ["pass", "qwer", "abc", "123", "let", "admin", "test", "user"]
    
    print("Generated Passwords:\n" + "="*30)
    for i in range(num_passwords):
        seed = np.random.choice(seeds)
        length = np.random.randint(min_length, max_length + 1)
        temp = np.random.uniform(0.5, 1.2)  # Vary temperature
        
        pwd = generate_password(
            seed=seed, 
            length=length, 
            temperature=temp
        )
        print(f"{i+1:2d}. {pwd} (seed: '{seed}', temp: {temp:.2f})")

if __name__ == "__main__":
    generate_multiple_passwords()
