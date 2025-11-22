import torch
import numpy as np
import string
from model import PasswordRNN
from data_prep import char_to_idx, idx_to_char, vocab_size

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
model = PasswordRNN(vocab_size).to(device)
model.load_state_dict(torch.load("password_rnn.pth", map_location=device))
model.eval()

def generate_password(seed="p", length=12, idx=0):
    input_seq = torch.tensor([[char_to_idx.get(c, 0) for c in seed]], device=device)
    hidden = None
    result = seed

    for _ in range(length - len(seed)):
        output, hidden = model(input_seq, hidden)

        # Handle both 2D (batch, vocab_size) and 3D (batch, seq_len, vocab_size)
        if output.dim() == 3:
            output = output[:, -1, :]  # usual RNN output
        else:
            output = output  # already 2D

        probs = torch.softmax(output, dim=-1).cpu().detach().numpy().flatten()
        probs = probs / probs.sum()  # normalize (safe guard)

        next_idx = np.random.choice(len(probs), p=probs)
        next_char = idx_to_char[next_idx]
        result += next_char
        input_seq = torch.tensor([[next_idx]], device=device)

    return result


# Generate and print 20 passwords per letter
print("Generated Passwords:\n---------------------")
letters = string.ascii_lowercase  # 'a'..'z'
per_letter = 20
pw_length = 10

for letter in letters:
    print(f"Letter '{letter}':")
    for i in range(per_letter):
        pwd = generate_password(seed=letter, length=pw_length, idx=i)
        print(f"  {i+1:2d}. {pwd}")
    print()  # blank line between letters
