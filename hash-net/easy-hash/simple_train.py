# simple_train.py
import torch
import torch.nn as nn
import torch.optim as optim
from hash_model import HashCracker
from hash_data_prep import training_pairs, vocab_size, char_to_idx, idx_to_char
from simple_hash import SimpleHashFunction

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def train_simple_cracker(epochs=50, batch_size=32):
    hash_function = SimpleHashFunction(output_dim=16, device=device)
    model = HashCracker(vocab_size, hash_function, hash_dim=16).to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss()
    
    print("Training Simple Cracker...")
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        batches = 0
        
        indices = torch.randperm(len(training_pairs))
        
        for i in range(0, len(indices), batch_size):
            batch_indices = indices[i:i+batch_size]
            if len(batch_indices) < 2:
                continue
                
            batch = [training_pairs[idx] for idx in batch_indices]
            
            input_seqs = torch.tensor([item['input_sequence'] for item in batch], device=device)
            target_chars = torch.tensor([item['target_char'] for item in batch], device=device)
            target_hashes = torch.stack([item['target_hash'] for item in batch]).to(device)
            
            # Forward pass
            char_logits, _ = model(input_seqs, target_hashes)
            
            # Simple cross-entropy loss only
            loss = criterion(char_logits.view(-1, vocab_size), target_chars.repeat(char_logits.size(1)))
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            batches += 1
        
        if batches > 0 and (epoch + 1) % 5 == 0:
            avg_loss = total_loss / batches
            print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
            
            # Quick test
            test_passwords = ["test123", "hello123", "password123"]
            exact_matches = 0
            
            for pwd in test_passwords:
                target_hash = hash_function.actual_hash(pwd)
                result = generate_simple(model, target_hash, max_length=12)
                
                if result == pwd:
                    exact_matches += 1
                    print(f"  ✅ '{pwd}' -> EXACT MATCH!")
                else:
                    print(f"  '{pwd}' -> '{result}'")
            
            if exact_matches == len(test_passwords):
                print("🎉 Perfect training achieved!")
                break
    
    torch.save(model.state_dict(), "simple_cracker.pth")

def generate_simple(model, target_hash, max_length=12):
    """Simple generation without temperature"""
    model.eval()
    with torch.no_grad():
        # Try multiple start characters
        for start_char in ['t', 'h', 'p', 'a']:
            if start_char not in char_to_idx:
                continue
                
            input_seq = torch.tensor([[char_to_idx[start_char]]], device=device)
            hidden = None
            result = start_char
            target_hash = target_hash.unsqueeze(0).to(device)
            
            for _ in range(max_length - 1):
                char_logits, hidden = model(input_seq, target_hash, hidden)
                
                # Greedy decoding - take most likely character
                next_idx = torch.argmax(char_logits[0, -1]).item()
                next_char = idx_to_char.get(next_idx, '')
                
                if next_char == '':
                    break
                    
                result += next_char
                input_seq = torch.tensor([[next_idx]], device=device)
                
                if len(result) >= max_length:
                    break
            
            # Return first reasonable result
            if len(result) >= 3:
                return result
        
        return result

if __name__ == "__main__":
    train_simple_cracker(epochs=50)
