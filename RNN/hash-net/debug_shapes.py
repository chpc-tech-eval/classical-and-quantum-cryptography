# debug_shapes.py
from hash_data_prep import training_pairs
import torch

print(f"Total training pairs: {len(training_pairs)}")

if len(training_pairs) > 0:
    # Check first few samples
    for i in range(min(3, len(training_pairs))):
        pair = training_pairs[i]
        print(f"\nSample {i+1}:")
        print(f"  Password: '{pair['full_password']}'")
        print(f"  Password length: {len(pair['full_password'])}")
        print(f"  Input sequence: {pair['input_sequence']}")
        print(f"  Sequence length: {len(pair['input_sequence'])}")
        print(f"  Target char index: {pair['target_char']}")
        
        # Check if sequence contains padding
        num_zeros = pair['input_sequence'].count(0)
        print(f"  Zero padding in sequence: {num_zeros}")
        
    # Check batch formation
    batch_size = 2
    batch = training_pairs[:batch_size]
    
    input_seqs = torch.tensor([item['input_sequence'] for item in batch])
    target_chars = torch.tensor([item['target_char'] for item in batch])
    
    print(f"\nBatch shapes:")
    print(f"  input_seqs: {input_seqs.shape}")  # Should be (batch_size, sequence_length)
    print(f"  target_chars: {target_chars.shape}")  # Should be (batch_size,)
