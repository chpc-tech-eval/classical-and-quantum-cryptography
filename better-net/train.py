# train.py
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from model import PasswordRNN
from data_prep import x_train, y_train, x_val, y_val, vocab_size
import time

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Enhanced model with more capacity
model = PasswordRNN(
    vocab_size=vocab_size,
    embed_dim=256,
    hidden_dim=512,
    num_layers=3,
    dropout=0.3
).to(device)

criterion = nn.CrossEntropyLoss()
# Use AdamW with weight decay for better regularization
optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)

# More sophisticated scheduler
scheduler = optim.lr_scheduler.OneCycleLR(
    optimizer, 
    max_lr=0.01,
    epochs=100,
    steps_per_epoch=len(x_train) // 128 + 1
)

num_epochs = 100
batch_size = 128
best_val_loss = float('inf')
patience = 8
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

print("Starting enhanced training...")
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
        loss = criterion(outputs, targets)
        
        optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping to prevent explosion
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()
        
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
    if avg_val_loss < best_val_loss - 0.001:  # Require meaningful improvement
        best_val_loss = avg_val_loss
        patience_counter = 0
        torch.save(model.state_dict(), "password_rnn.pth")
        print("  ↳ Model saved! (improvement)")
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"Early stopping triggered after {epoch+1} epochs!")
            break
    
    # Print progress every 10 epochs
    if (epoch + 1) % 10 == 0:
        print(f"--- Progress: {epoch+1}/{num_epochs} epochs completed ---")

print("Training completed!")
print(f"Best validation loss: {best_val_loss:.4f}")

# Plotting function (optional)
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
    
    plt.subplot(1, 2, 2)
    plt.plot(train_accuracies, label='Train Accuracy')
    plt.plot(val_accuracies, label='Val Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.title('Training and Validation Accuracy')
    
    plt.tight_layout()
    plt.savefig('training_metrics.png', dpi=150, bbox_inches='tight')
    print("Training metrics plot saved as 'training_metrics.png'")
    
except ImportError:
    print("Matplotlib not available, skipping plots")
