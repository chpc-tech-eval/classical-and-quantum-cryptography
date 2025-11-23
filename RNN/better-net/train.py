# train.py
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from model import PasswordRNN
from data_prep import x_train, y_train, x_val, y_val, vocab_size
import time
import os

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# More conservative model to prevent overfitting
model = PasswordRNN(
    vocab_size=vocab_size,
    embed_dim=256,  # Reduced from 256
    hidden_dim=512,  # Reduced from 512
    num_layers=4,   # Reduced from 3
    dropout=0.5      # Increased dropout
).to(device)

criterion = nn.CrossEntropyLoss()
# Lower learning rate with more weight decay
optimizer = optim.AdamW(model.parameters(), lr=0.0005, weight_decay=0.02)

# More gradual learning rate scheduler
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50, eta_min=0.0001)

num_epochs = 100
batch_size = 64  # Smaller batch size
best_val_loss = float('inf')
patience = 15    # More patience
patience_counter = 0

# For tracking metrics
train_losses = []
val_losses = []
train_accuracies = []
val_accuracies = []

def calculate_accuracy(outputs, targets):
    """Calculate prediction accuracy"""
    _, predicted = torch.max(outputs, 1)
    correct = (predicted == targets).float()
    return correct.mean().item()

def add_label_smoothing(targets, num_classes, smoothing=0.1):
    """Add label smoothing to prevent overconfidence"""
    confidence = 1.0 - smoothing
    smoothing_value = smoothing / (num_classes - 1)
    one_hot = torch.full((targets.size(0), num_classes), smoothing_value).to(device)
    one_hot.scatter_(1, targets.unsqueeze(1), confidence)
    return one_hot

print("Starting improved training with overfitting prevention...")
print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

for epoch in range(num_epochs):
    start_time = time.time()
    
    # Training phase
    model.train()
    train_loss = 0
    train_acc = 0
    num_batches = 0
    
    # Shuffle training data each epoch
    indices = torch.randperm(len(x_train))
    x_train_shuffled = x_train[indices]
    y_train_shuffled = y_train[indices]
    
    for i in range(0, len(x_train_shuffled), batch_size):
        inputs = x_train_shuffled[i:i+batch_size].to(device)
        targets = y_train_shuffled[i:i+batch_size].to(device)
        
        outputs, _ = model(inputs)
        
        # Use label smoothing
        smoothed_targets = add_label_smoothing(targets, vocab_size, smoothing=0.1)
        loss = criterion(outputs, smoothed_targets)
        
        optimizer.zero_grad()
        loss.backward()
        
        # Gentle gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
        optimizer.step()
        
        # Calculate accuracy with original targets (no smoothing)
        with torch.no_grad():
            acc = calculate_accuracy(outputs, targets)
        
        train_loss += loss.item()
        train_acc += acc
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
            loss = criterion(outputs, targets)  # No smoothing for validation
            
            val_loss += loss.item()
            val_acc += calculate_accuracy(outputs, targets)
            num_val_batches += 1
    
    avg_val_loss = val_loss / num_val_batches
    avg_val_acc = val_acc / num_val_batches
    
    # Update learning rate
    scheduler.step()
    
    # Track metrics
    train_losses.append(avg_train_loss)
    val_losses.append(avg_val_loss)
    train_accuracies.append(avg_train_acc)
    val_accuracies.append(avg_val_acc)
    
    epoch_time = time.time() - start_time
    
    print(f"Epoch {epoch+1}/{num_epochs} ({epoch_time:.2f}s)")
    print(f"  Train Loss: {avg_train_loss:.4f}, Train Acc: {avg_train_acc:.4f}")
    print(f"  Val Loss: {avg_val_loss:.4f}, Val Acc: {avg_val_acc:.4f}")
    print(f"  LR: {optimizer.param_groups[0]['lr']:.6f}")
    
    # Early stopping with improvement threshold
    if avg_val_loss < best_val_loss - 0.0005:  # Smaller improvement threshold
        best_val_loss = avg_val_loss
        patience_counter = 0
        torch.save(model.state_dict(), "password_rnn.pth")
        print("  ↳ Model saved! (improvement)")
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"Early stopping triggered after {epoch+1} epochs!")
            print(f"Best validation loss: {best_val_loss:.4f}")
            break
    
    # Print progress every 5 epochs
    if (epoch + 1) % 5 == 0:
        print(f"--- Progress: {epoch+1}/{num_epochs} epochs completed ---")

print("Training completed!")
print(f"Final best validation loss: {best_val_loss:.4f}")

# Plotting function
try:
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Val Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Training and Validation Loss')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    plt.plot(train_accuracies, label='Train Accuracy')
    plt.plot(val_accuracies, label='Val Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.title('Training and Validation Accuracy')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('training_metrics.png', dpi=150, bbox_inches='tight')
    print("Training metrics plot saved as 'training_metrics.png'")
    
except ImportError:
    print("Matplotlib not available, skipping plots")
