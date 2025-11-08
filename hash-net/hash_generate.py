# hash_generate.py
import torch
import numpy as np
from hash_model import HashCracker
from hash_data_prep import char_to_idx, idx_to_char, vocab_size
from simple_hash import SimpleHashFunction

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

def load_model(model_path="hash_cracker_rnn.pth"):
    """Load the trained model"""
    hash_function = SimpleHashFunction(device=device)
    model = HashCracker(vocab_size, hash_function).to(device)
    
    print(f"Loading model from {model_path}...")
    state_dict = torch.load(model_path, map_location=device, weights_only=False)
    print(f"Loaded state dict type: {type(state_dict)}")
    
    # Handle different state dict formats
    if isinstance(state_dict, dict):
        if 'model_state_dict' in state_dict:
            print("Loading from checkpoint dictionary...")
            model.load_state_dict(state_dict['model_state_dict'])
        elif 'rnn.hash_encoder.0.weight' in state_dict:
            print("Loading from model state dict...")
            model.load_state_dict(state_dict)
        else:
            print("Unexpected dictionary format, trying direct load...")
            model.load_state_dict(state_dict)
    else:
        # Assume it's already a state dict
        model.load_state_dict(state_dict)
    
    print("✅ Model loaded successfully!")
    return model

# Load model
model = load_model()
model.eval()
print("Model is ready for hash cracking!")

def crack_hash(target_hash, max_length=20, temperature=0.8):
    """Generate password that likely produces the target hash"""
    # Initialize with a starting character
    start_char = 'p'
    if start_char not in char_to_idx:
        start_char = list(char_to_idx.keys())[10]  # Use a different starting char if 'p' not available
    
    input_seq = torch.tensor([[char_to_idx[start_char]]], device=device)
    hidden = None
    result = start_char
    target_hash = target_hash.unsqueeze(0).to(device)  # Add batch dimension
    
    print(f"Starting hash cracking with temperature {temperature}...")
    
    for step in range(max_length - 1):
        with torch.no_grad():
            char_logits, hidden = model(input_seq, target_hash, hidden)
            
            # Sample next character with temperature
            probs = torch.softmax(char_logits[0, -1] / temperature, dim=-1)
            next_idx = torch.multinomial(probs, 1).item()
            next_char = idx_to_char.get(next_idx, '')
            
            # Stop if we get an unknown character
            if next_char == '':
                print(f"Stopping: unknown character index {next_idx}")
                break
                
            result += next_char
            input_seq = torch.tensor([[next_idx]], device=device)
            
            # Stop conditions
            if next_char in ['\n', ' ']:
                print(f"Stopping: generated stop character '{next_char}'")
                break
            if len(result) >= max_length:
                print(f"Stopping: reached max length {max_length}")
                break
            
            # Print progress for longer generations
            if step % 5 == 0:
                print(f"  Step {step}: current result: '{result}'")
    
    return result

def crack_hashes_from_test_passwords(num_passwords=5):
    """Test the model by cracking hashes of known passwords"""
    hash_function = SimpleHashFunction(device=device)
    
    # Test passwords that should be in the training distribution
    test_passwords = ["password123", "admin2024", "hello123", "welcome1", "testpass"]
    
    print("\nHash Cracking Test Results")
    print("=" * 50)
    
    for i, true_password in enumerate(test_passwords):
        print(f"\nTest {i+1}: Cracking hash for '{true_password}'")
        
        # Create target hash for this password
        target_hash = hash_function.actual_hash(true_password)
        
        # Try to crack it multiple times with different temperatures
        best_match = ""
        best_similarity = 0
        
        for temp in [0.5, 0.8, 1.0]:
            print(f"  Trying temperature {temp}...")
            cracked_password = crack_hash(target_hash, max_length=len(true_password) + 5, temperature=temp)
            cracked_hash = hash_function.actual_hash(cracked_password)
            similarity = torch.sum(target_hash == cracked_hash).item() / len(target_hash)
            
            print(f"  Result: '{cracked_password}' (similarity: {similarity:.2%})")
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = cracked_password
        
        print(f"✓ Best result: '{best_match}'")
        print(f"  Similarity: {best_similarity:.2%}")
        print(f"  Exact match: {true_password == best_match}")

def demonstrate_training_effectiveness():
    """Show that the model has learned from the training data"""
    hash_function = SimpleHashFunction(device=device)
    
    print("\nTraining Effectiveness Demonstration")
    print("=" * 45)
    
    # Test with patterns that should be in the training data
    test_cases = [
        "password123",  # Common pattern
        "admin2024",    # Common pattern with year
        "hello123",     # Simple word with numbers
        "welcome1",     # Another common pattern
    ]
    
    for password in test_cases:
        target_hash = hash_function.actual_hash(password)
        
        print(f"\nTarget: '{password}'")
        for temp in [0.6, 0.8, 1.0]:
            cracked = crack_hash(target_hash, temperature=temp, max_length=15)
            cracked_hash = hash_function.actual_hash(cracked)
            similarity = torch.sum(target_hash == cracked_hash).item() / len(target_hash)
            
            print(f"  temp={temp}: '{cracked}' (similarity: {similarity:.2%})")

if __name__ == "__main__":
    print("Hash Cracker RNN - Generation Test")
    print("=" * 35)
    
    # First, demonstrate basic functionality
    demonstrate_training_effectiveness()
    
    # Then run comprehensive tests
    crack_hashes_from_test_passwords(num_passwords=5)
    
    print("\n" + "=" * 50)
    print("Testing complete!")
    print("=" * 50)
