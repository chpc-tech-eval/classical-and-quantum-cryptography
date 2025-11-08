# fix_model_save.py
import torch
from hash_model import HashCracker
from hash_data_prep import vocab_size
from simple_hash import SimpleHashFunction

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def fix_model_save():
    print("Checking model save format...")
    
    # Load the current checkpoint
    checkpoint = torch.load("hash_cracker_rnn.pth", map_location=device, weights_only=False)
    print(f"Checkpoint type: {type(checkpoint)}")
    
    if isinstance(checkpoint, dict):
        if 'model_state_dict' in checkpoint:
            print("Found model_state_dict in checkpoint")
            model_state_dict = checkpoint['model_state_dict']
            
            # Save just the model state dict
            torch.save(model_state_dict, "hash_cracker_rnn_fixed.pth")
            print("✅ Fixed model saved as 'hash_cracker_rnn_fixed.pth'")
            
        elif 'rnn.hash_encoder.0.weight' in checkpoint:
            print("✅ Checkpoint is already a valid model state dict!")
            print(f"Number of parameter groups: {len(checkpoint)}")
            
            # Verify the model loads correctly
            hash_function = SimpleHashFunction(device=device)
            model = HashCracker(vocab_size, hash_function).to(device)
            model.load_state_dict(checkpoint)
            print("✅ Model loads successfully from current checkpoint!")
            
            # Save it with a clear name to avoid confusion
            torch.save(checkpoint, "hash_cracker_rnn_working.pth")
            print("✅ Model saved as 'hash_cracker_rnn_working.pth'")
            
        else:
            print("Unexpected dictionary format. Keys:", list(checkpoint.keys())[:5])
    else:
        print(f"Checkpoint is {type(checkpoint)} - likely already a state dict")
        torch.save(checkpoint, "hash_cracker_rnn_working.pth")
        print("✅ Model saved as 'hash_cracker_rnn_working.pth'")

if __name__ == "__main__":
    fix_model_save()
