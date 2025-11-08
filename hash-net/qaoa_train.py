# qaoa_train.py
import torch
import torch.nn as nn
import torch.optim as optim
from hash_model import HashCracker
from hash_data_prep import training_pairs, vocab_size, char_to_idx, idx_to_char
from simple_hash import SimpleHashFunction

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

class QAOALoss(nn.Module):
    """Loss function inspired by QAOA objective: minimize hash difference"""
    
    def __init__(self, alpha=1.0, beta=0.1):
        super().__init__()
        self.alpha = alpha  # Hash matching weight
        self.beta = beta    # Password likelihood weight
        self.ce_loss = nn.CrossEntropyLoss()
        
    def forward(self, char_logits, target_chars, generated_hash, target_hash):
        # Character prediction loss (standard language modeling)
        # char_logits shape: (batch_size, seq_len, vocab_size)
        # target_chars shape: (batch_size,)
        
        # Reshape for cross entropy: (batch_size * seq_len, vocab_size) and (batch_size * seq_len)
        batch_size, seq_len, vocab_size = char_logits.shape
        char_logits_flat = char_logits.reshape(-1, vocab_size)
        
        # Repeat target_chars for each position in the sequence
        target_chars_flat = target_chars.unsqueeze(1).repeat(1, seq_len).reshape(-1)
        
        char_loss = self.ce_loss(char_logits_flat, target_chars_flat)
        
        # Hash matching loss (QAOA-style objective)
        hash_loss = nn.MSELoss()(generated_hash, target_hash)
        
        # Combined loss - we want to minimize both
        total_loss = self.alpha * hash_loss + self.beta * char_loss
        return total_loss, hash_loss, char_loss

# Initialize model and hash function
hash_function = SimpleHashFunction(device=device)
model = HashCracker(vocab_size, hash_function).to(device)

# Initialize hash function projection layer
hash_function.init_projection(vocab_size)

# QAOA-inspired optimizer with different parameter groups
hash_params = []
char_params = []

for name, param in model.named_parameters():
    if 'hash' in name:
        hash_params.append(param)
    else:
        char_params.append(param)

optimizer = optim.Adam([
    {'params': hash_params, 'lr': 0.001},
    {'params': char_params, 'lr': 0.003}
])

qaoa_loss = QAOALoss(alpha=1.0, beta=0.1)

def train_hash_cracker(epochs=100, batch_size=32):
    # Safety check
    if len(training_pairs) == 0:
        print("ERROR: No training pairs available!")
        return
    
    if len(training_pairs) < batch_size:
        batch_size = len(training_pairs)
        print(f"Warning: Reduced batch_size to {batch_size} to match available data")
    
    model.train()
    
    for epoch in range(epochs):
        total_loss = 0
        total_hash_loss = 0
        total_char_loss = 0
        batches_processed = 0
        
        # Shuffle and batch
        indices = torch.randperm(len(training_pairs))
        
        for i in range(0, len(indices), batch_size):
            batch_indices = indices[i:i+batch_size]
            if len(batch_indices) == 0:
                continue
                
            batch = [training_pairs[idx] for idx in batch_indices]
            current_batch_size = len(batch)
            
            # Prepare batch data - ensure everything is on the same device
            input_seqs = torch.tensor([item['input_sequence'] for item in batch], device=device)
            target_chars = torch.tensor([item['target_char'] for item in batch], device=device)
            target_hashes = torch.stack([item['target_hash'] for item in batch]).to(device)
            
            # Forward pass
            char_logits, hidden = model(input_seqs, target_hashes)
            
            # Debug: print shapes
            if epoch == 0 and batches_processed == 0:
                print(f"Debug shapes:")
                print(f"  input_seqs: {input_seqs.shape}")  # Should be (batch_size, seq_len)
                print(f"  target_chars: {target_chars.shape}")  # Should be (batch_size,)
                print(f"  char_logits: {char_logits.shape}")  # Should be (batch_size, seq_len, vocab_size)
                print(f"  target_hashes: {target_hashes.shape}")  # Should be (batch_size, hash_dim)
            
            # Compute hash of generated sequence (differentiable approximation)
            generated_hash = hash_function.differentiable_hash(char_logits)
            
            # QAOA-inspired loss
            loss, hash_loss, char_loss = qaoa_loss(
                char_logits, target_chars, generated_hash, target_hashes
            )
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
            total_loss += loss.item()
            total_hash_loss += hash_loss.item()
            total_char_loss += char_loss.item()
            batches_processed += 1
        
        # Print progress
        if batches_processed > 0 and (epoch + 1) % 5 == 0:  # Print more frequently
            avg_loss = total_loss / batches_processed
            avg_hash_loss = total_hash_loss / batches_processed
            avg_char_loss = total_char_loss / batches_processed
            
            print(f"Epoch {epoch+1}/{epochs}")
            print(f"  Total Loss: {avg_loss:.4f}")
            print(f"  Hash Loss: {avg_hash_loss:.4f}")
            print(f"  Char Loss: {avg_char_loss:.4f}")
            
            # Generate sample to show progress
            if (epoch + 1) % 20 == 0 and len(training_pairs) > 0:
                generate_from_hash_sample(target_hashes[0], f"Epoch {epoch+1}")
    
    # Save model
    torch.save(model.state_dict(), "hash_cracker_rnn.pth")
    print("model saved successfully!")

def generate_from_hash_sample(target_hash, description=""):
    """Generate password from target hash"""
    model.eval()
    
    with torch.no_grad():
        seed = torch.tensor([[char_to_idx.get('p', 0)]], device=device)
        hidden = None
        result = "p"
        target_hash = target_hash.unsqueeze(0)  # Add batch dimension
        
        for _ in range(19):  # Generate up to 20 chars
            char_logits, hidden = model(seed, target_hash, hidden)
            
            # Sample next character
            probs = torch.softmax(char_logits[0, -1], dim=-1)
            next_idx = torch.multinomial(probs, 1).item()
            next_char = idx_to_char.get(next_idx, '')
            
            result += next_char
            seed = torch.tensor([[next_idx]], device=device)
            
            if next_char == '' or len(result) >= 20:  # Stop conditions
                break
        
        print(f"{description}: '{result}'")
    
    model.train()

if __name__ == "__main__":
    print(f"Starting training with {len(training_pairs)} pairs...")
    train_hash_cracker(epochs=100)
