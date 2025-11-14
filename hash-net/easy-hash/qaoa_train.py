# qaoa_train.py
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from hash_model import HashCracker
from hash_data_prep import training_pairs, vocab_size, char_to_idx, idx_to_char
from simple_hash import SimpleHashFunction

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class ExplorationLoss(nn.Module):
    def __init__(self, diversity_weight=0.1):
        super().__init__()
        self.ce_loss = nn.CrossEntropyLoss()
        self.diversity_weight = diversity_weight
        
    def forward(self, char_logits, target_chars, generated_hash, target_hash, generated_texts=None):
        # Main character prediction loss
        batch_size, seq_len, vocab_size = char_logits.shape
        char_logits_flat = char_logits.reshape(-1, vocab_size)
        target_chars_flat = target_chars.unsqueeze(1).repeat(1, seq_len).reshape(-1)
        char_loss = self.ce_loss(char_logits_flat, target_chars_flat)
        
        # Hash matching loss
        hash_loss = nn.MSELoss()(generated_hash, target_hash)
        
        # Diversity encouragement
        diversity_loss = 0
        if generated_texts:
            for text in generated_texts:
                # Penalize repetitive patterns
                unique_chars = len(set(text))
                diversity_loss += (1.0 - unique_chars / len(text)) if len(text) > 0 else 0
            diversity_loss /= len(generated_texts)
        
        total_loss = char_loss + hash_loss - (self.diversity_weight * diversity_loss)
        return total_loss, char_loss, hash_loss, diversity_loss

def train_with_exploration(epochs=150, batch_size=32):
    hash_function = SimpleHashFunction(output_dim=32, device=device)
    model = HashCracker(vocab_size, hash_function, hash_dim=32).to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=0.005)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    loss_fn = ExplorationLoss(diversity_weight=0.2)
    
    print("Training with exploration strategies...")
    
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
            char_logits, hidden = model(input_seqs, target_hashes)
            generated_hash = hash_function.differentiable_hash(char_logits)
            
            # Generate diverse samples for diversity loss
            with torch.no_grad():
                sample_texts = []
                for j in range(min(4, len(batch))):
                    text = generate_with_exploration(model, target_hashes[j:j+1], 
                                                   temperature=1.5,  # High temp for exploration
                                                   max_length=15)
                    sample_texts.append(text)
            
            # Apply exploration loss
            loss, char_loss, hash_loss, div_loss = loss_fn(
                char_logits, target_chars, generated_hash, target_hashes, sample_texts
            )
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            
            # Add noise to gradients to escape local minima
            for param in model.parameters():
                if param.grad is not None:
                    noise = torch.randn_like(param.grad) * 0.01
                    param.grad += noise
            
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
            total_loss += loss.item()
            batches += 1
        
        scheduler.step()
        
        if batches > 0 and (epoch + 1) % 10 == 0:
            avg_loss = total_loss / batches
            print(f"\nEpoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
            
            # Test with multiple exploration strategies
            test_exploration_generation(model, hash_function, epoch)
    
    torch.save(model.state_dict(), "exploration_cracker.pth")

def generate_with_exploration(model, target_hash, temperature=1.5, max_length=15):
    """Generate with exploration strategies"""
    model.eval()
    with torch.no_grad():
        # Try different start characters randomly
        start_chars = list('abcdefghijklmnopqrstuvwxyz1234567890')
        start_char = np.random.choice(start_chars)
        
        if start_char not in char_to_idx:
            start_char = 'a'
            
        input_seq = torch.tensor([[char_to_idx[start_char]]], device=device)
        hidden = None
        result = start_char
        target_hash = target_hash.unsqueeze(0).to(device)
        
        for step in range(max_length - 1):
            char_logits, hidden = model(input_seq, target_hash, hidden)
            
            # High temperature for exploration
            probs = torch.softmax(char_logits[0, -1] / temperature, dim=-1)
            
            # Sometimes use top-k sampling instead of multinomial
            if step % 3 == 0:  # Every 3rd step, be more exploratory
                top_k = 10
                top_probs, top_indices = torch.topk(probs, top_k)
                top_probs = top_probs / top_probs.sum()
                next_idx = top_indices[torch.multinomial(top_probs, 1)].item()
            else:
                next_idx = torch.multinomial(probs, 1).item()
            
            next_char = idx_to_char.get(next_idx, '')
            
            if next_char == '':
                break
                
            result += next_char
            input_seq = torch.tensor([[next_idx]], device=device)
            
            # Dynamic stopping
            if len(result) >= 8 and has_repeating_pattern(result):
                break
            if len(result) >= max_length:
                break
        
        return result

def test_exploration_generation(model, hash_function, epoch):
    """Test generation with multiple exploration strategies"""
    model.eval()
    
    test_passwords = ["test123", "hello123", "password123", "admin123"]
    print(f"  Exploration Test (Epoch {epoch+1}):")
    
    for pwd in test_passwords:
        target_hash = hash_function.actual_hash(pwd)
        
        # Try multiple strategies
        strategies = [
            {'temp': 0.8, 'name': 'low_temp'},
            {'temp': 1.2, 'name': 'med_temp'}, 
            {'temp': 2.0, 'name': 'high_temp'},
            {'temp': 1.5, 'name': 'top_k'}
        ]
        
        best_result = ""
        best_similarity = 0
        
        for strategy in strategies:
            result = generate_with_exploration(model, target_hash, 
                                             temperature=strategy['temp'],
                                             max_length=len(pwd) + 3)
            
            similarity = calculate_similarity(hash_function, pwd, result)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_result = result
            
            if result == pwd:
                print(f"    ✅ '{pwd}' -> EXACT MATCH! ({strategy['name']})")
                break
        else:
            # No break = no exact match
            if best_similarity > 0.7:
                print(f"    ⚠️  '{pwd}' -> '{best_result}' ({best_similarity:.1%})")
            else:
                print(f"    ❌ '{pwd}' -> '{best_result}' ({best_similarity:.1%})")
    
    model.train()

def has_repeating_pattern(text, min_repeat=4):
    """Check for problematic repeating patterns"""
    if len(text) < min_repeat * 2:
        return False
    for i in range(len(text) - min_repeat):
        if text[i] * min_repeat in text:
            return True
    return False

def calculate_similarity(hash_function, true_pwd, generated_pwd):
    true_hash = hash_function.actual_hash(true_pwd)
    gen_hash = hash_function.actual_hash(generated_pwd)
    return 1.0 - torch.mean(torch.abs(true_hash - gen_hash)).item()

if __name__ == "__main__":
    train_with_exploration(epochs=150)
