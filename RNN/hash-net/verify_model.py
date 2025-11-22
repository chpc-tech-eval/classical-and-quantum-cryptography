# verify_model.py
import torch
from hash_model import HashCracker
from hash_data_prep import vocab_size, char_to_idx
from simple_hash import SimpleHashFunction

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def verify_model(model_path="hash_cracker_rnn_fixed.pth"):
    print("Verifying model structure and loading...")
    
    # Create a fresh model
    hash_function = SimpleHashFunction(device=device)
    model = HashCracker(vocab_size, hash_function).to(device)
    
    print("Model structure:")
    for name, param in model.named_parameters():
        print(f"  {name}: {param.shape}")
    
    # Try to load the saved model
    print(f"\nLoading model from {model_path}...")
    try:
        state_dict = torch.load(model_path, map_location=device, weights_only=False)
        
        # Handle different save formats
        if isinstance(state_dict, dict):
            if 'model_state_dict' in state_dict:
                print("Found checkpoint dictionary format")
                state_dict = state_dict['model_state_dict']
            else:
                print("Unexpected dictionary format, trying direct load...")
                # Try to load it as a state dict anyway
                model.load_state_dict(state_dict)
                print("✅ Loaded successfully as state dict!")
                state_dict = None  # Already loaded
        
        if state_dict is not None:
            model.load_state_dict(state_dict)
        
        print("✅ Model loaded successfully!")
        
        # Test forward pass
        print("\nTesting forward pass...")
        test_input = torch.tensor([[char_to_idx.get('p', 0)]], device=device)
        test_hash = torch.randn(1, 128).to(device)  # Random hash
        
        with torch.no_grad():
            output, hidden = model(test_input, test_hash)
            print(f"✅ Forward pass successful!")
            print(f"   Input shape: {test_input.shape}")
            print(f"   Output shape: {output.shape}")
            print(f"   Output sample: {output[0, -1, :5]}")  # First 5 logits
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Try fixed model first, then original
    if not verify_model("hash_cracker_rnn_fixed.pth"):
        print("\nTrying original model file...")
        verify_model("hash_cracker_rnn.pth")
