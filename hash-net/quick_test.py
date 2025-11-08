# quick_test.py
import torch
from hash_generate import load_model, crack_hash
from simple_hash import SimpleHashFunction

def quick_test():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Quick test of hash cracker...")
    
    # Load model
    model = load_model()
    model.eval()
    
    # Test with a simple password
    hash_function = SimpleHashFunction(device=device)
    test_password = "test123"
    target_hash = hash_function.actual_hash(test_password)
    
    print(f"Testing with password: '{test_password}'")
    cracked = crack_hash(target_hash, temperature=0.8, max_length=10)
    
    print(f"Original: '{test_password}'")
    print(f"Cracked:  '{cracked}'")
    print(f"Match: {test_password == cracked}")

if __name__ == "__main__":
    quick_test()
