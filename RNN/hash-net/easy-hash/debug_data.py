# debug_data.py
from hash_data_prep import training_pairs, char_to_idx, idx_to_char, vocab_size

print(f"Total training pairs: {len(training_pairs)}")
print(f"Vocabulary size: {vocab_size}")
print(f"Character mappings: {char_to_idx}")

if len(training_pairs) > 0:
    for i in range(min(3, len(training_pairs))):
        pair = training_pairs[i]
        print(f"\nSample {i+1}:")
        print(f"  Full password: {pair['full_password']}")
        print(f"  Input sequence: {pair['input_sequence']}")
        print(f"  Target char index: {pair['target_char']}")
        if pair['target_char'] in idx_to_char:
            print(f"  Target char: '{idx_to_char[pair['target_char']]}'")
        print(f"  Target hash shape: {pair['target_hash'].shape}")
else:
    print("No training pairs found!")
    
    # Check passwords file
    with open("passwords.txt", "r") as f:
        lines = f.readlines()
        print(f"Lines in passwords.txt: {len(lines)}")
        print("First 5 lines:")
        for i, line in enumerate(lines[:5]):
            print(f"  {i+1}: '{line.strip()}'")
