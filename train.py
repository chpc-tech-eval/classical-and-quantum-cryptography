# train.py
import torch
import torch.nn as nn
import torch.optim as optim
from model import PasswordRNN
from data_prep import x, y, vocab_size

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = PasswordRNN(vocab_size).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.003)

num_epochs = 20
batch_size = 128

for epoch in range(num_epochs):
    for i in range(0, len(x), batch_size):
        inputs = x[i:i+batch_size].to(device)
        targets = y[i:i+batch_size].to(device)

        outputs, _ = model(inputs)
        loss = criterion(outputs, targets)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    print(f"Epoch {epoch+1}/{num_epochs}, Loss: {loss.item():.4f}")
#save the model after training is done
torch.save(model.state_dict(), "password_rnn.pth")
