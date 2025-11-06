# train.py
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from model import PasswordRNN
from data_prep import x_train, y_train, x_val, y_val, vocab_size

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Model with multiple LSTM layers
model = PasswordRNN(
    vocab_size=vocab_size,
    embed_dim=128,
    hidden_dim=256,
    num_layers=2,
    dropout=0.2
).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=2, factor=0.5)

num_epochs = 50
batch_size = 64
best_val_loss = float('inf')
patience = 5
patience_counter = 0

def calculate_accuracy(outputs, targets):
    """Calculate prediction accuracy"""
    _, predicted = torch.max(outputs, 1)
    correct = (predicted == targets).float()
    return correct.mean().item()

print("Starting training...")
for epoch in range(num_epochs):
    # Training phase
    model.train()
    train_loss = 0
    train_acc = 0
    num_batches = 0
    
    for i in range(0, len(x_train), batch_size):
        inputs = x_train[i:i+batch_size].to(device)
        targets = y_train[i:i+batch_size].to(device)
        
        outputs, _ = model(inputs)
        loss = criterion(outputs, targets)
        
        optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping to prevent explosion
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        
        train_loss += loss.item()
        train_acc += calculate_accuracy(outputs, targets)
        num_batches += 1
    
    avg_train_loss = train_loss / num_batches
    avg_train_acc = train_acc / num_batches
    
    # Validation phase
    model.eval()
    val_loss = 0
    val_acc = 0
    num_val_batches = 0
    
    with torch.no_grad():
        for i in range(0, len(x_val), batch_size):
            inputs = x_val[i:i+batch_size].to(device)
            targets = y_val[i:i+batch_size].to(device)
            
            outputs, _ = model(inputs)
            loss = criterion(outputs, targets)
            
            val_loss += loss.item()
            val_acc += calculate_accuracy(outputs, targets)
            num_val_batches += 1
    
    avg_val_loss = val_loss / num_val_batches
    avg_val_acc = val_acc / num_val_batches
    
    scheduler.step(avg_val_loss)
    
    print(f"Epoch {epoch+1}/{num_epochs}")
    print(f"  Train Loss: {avg_train_loss:.4f}, Train Acc: {avg_train_acc:.4f}")
    print(f"  Val Loss: {avg_val_loss:.4f}, Val Acc: {avg_val_acc:.4f}")
    print(f"  LR: {optimizer.param_groups[0]['lr']:.6f}")
    
    # Early stopping
    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        patience_counter = 0
        torch.save(model.state_dict(), "password_rnn.pth")
        print("  ↳ Model saved!")
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print("Early stopping triggered!")
            break

print("Training completed!")
