# simple_hash_generate.py
import torch
from hash_model import HashCracker
from hash_data_prep import char_to_idx, idx_to_char, vocab_size
from simple_hash import SimpleHashFunction

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_simple_model():
    hash_function = SimpleHashFunction(output_dim=64, device=device)
    model = HashCracker(vocab_size, hash_function, hash_dim=64).to(device)
    
    try:
        model.load_state_dict(torch.load("simple_hash_cracker.pth", map_location=device))
        print("✅ Simple hash cracker loaded!")
    except:
        print("❌ Simple model not found, please train first")
        return None
    
    model.eval()
    return model, hash_function

def crack_simple_hash(target_hash, max_attempts=5):
    """Crack the simple hash with multiple attempts"""
    model, hash_function = load_simple_model()
    if model is None:
        return None, 0
    
    best_result = ""
    best_similarity = 0
    
    start_chars = ['p', 'a', '1', 't', 's', 'h', 'l', 'm']
    
    for start_char in start_chars:
        if start_char not in char_to_idx:
            continue
            
        for temp in [0.5, 0.7, 0.9]:
            result = generate_password(model, target_hash, start_char, temp, max_length=15)
            similarity = 1.0 - torch.mean(torch.abs(target_hash - hash_function.actual_hash(result))).item()
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_result = result
            
            # Early exit for good matches
            if similarity > 0.95:
                return result, similarity
    
    return best_result, best_similarity

def generate_password(model, target_hash, start_char, temperature, max_length=15):
    """Generate a single password attempt"""
    with torch.no_grad():
        input_seq = torch.tensor([[char_to_idx[start_char]]], device=device)
        hidden = None
        result = start_char
        target_hash = target_hash.unsqueeze(0).to(device)
        
        for _ in range(max_length - 1):
            char_logits, hidden = model(input_seq, target_hash, hidden)
            probs = torch.softmax(char_logits[0, -1] / temperature, dim=-1)
            next_idx = torch.multinomial(probs, 1).item()
            next_char = idx_to_char.get(next_idx, '')
            
            if next_char == '':
                break
            result += next_char
            input_seq = torch.tensor([[next_idx]], device=device)
            
            if len(result) >= max_length:
                break
        
        return result

def demo_simple_hash_cracking():
    """Demonstrate the simple hash cracking"""
    model, hash_function = load_simple_model()
    if model is None:
        return
    
    print("Simple Hash Cracking Demonstration")
    print("=" * 40)
    
    test_passwords = [
        "password123", "hello123", "test123", 
        "admin123", "welcome1", "letmein1"
    ]
    
    exact_matches = 0
    high_similarity = 0
    
    for true_password in test_passwords:
        target_hash = hash_function.actual_hash(true_password)
        
        print(f"\nTarget: '{true_password}'")
        
        # Try multiple cracking attempts
        cracked, similarity = crack_simple_hash(target_hash)
        
        print(f"Cracked: '{cracked}'")
        print(f"Similarity: {similarity:.1%}")
        
        if true_password == cracked:
            print("✅ EXACT MATCH!")
            exact_matches += 1
        elif similarity > 0.9:
            print("✅ Very close!")
            high_similarity += 1
        elif similarity > 0.7:
            print("⚠️  Close match")
    
    print(f"\n📊 Results: {exact_matches}/{len(test_passwords)} exact matches")
    print(f"📊 High similarity: {high_similarity}/{len(test_passwords)}")

if __name__ == "__main__":
    demo_simple_hash_cracking()
