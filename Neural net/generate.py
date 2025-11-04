# generate.py
import torch
import numpy as np
from model import PasswordRNN
from data_prep import char_to_idx, idx_to_char, vocab_size

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = PasswordRNN(vocab_size).to(device)
model.load_state_dict(torch.load("password_rnn.pth"))
model.eval()

def generate_password(seed="p", length=12):
    input_seq = torch.tensor([[char_to_idx.get(c, 0) for c in seed]], device=device)
    hidden = None
    result = seed

    for _ in range(length - len(seed)):
        output, hidden = model(input_seq, hidden)
        probs = torch.softmax(output, dim=-1).cpu().detach().numpy().flatten()

        # Normalize in case of rounding errors
        probs = probs / probs.sum()

        next_idx = np.random.choice(len(probs), p=probs)
        next_char = idx_to_char[next_idx]
        result += next_char
        input_seq = torch.tensor([[next_idx]], device=device)

    return result

# Generate and print 20 passwords
print("Generated Passwords:\n---------------------")
for i in range(20):
    pwd = generate_password(seed="p", length=10)
    print(f"{i+1:2d}. {pwd}")

