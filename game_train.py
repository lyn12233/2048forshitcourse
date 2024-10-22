import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os

from game_nn import ConvAttentionNN

# Load the data
data = np.load('label.npz')['dat']  # Assuming 'data' is the key for input data
labels = np.load('label.npz')['label']  # Assuming 'label' is the key for labels

# Convert data to PyTorch tensors
data = torch.tensor(data, dtype=torch.float32)  # Shape (n_samples, 4,4)
data=data.view(data.shape[0],-1) # Shape (n_samples, 16)
labels = torch.tensor(labels, dtype=torch.float32).view(-1, 1)  # Shape (n_samples, 1)

# Define the neural network
class SimpleNN(nn.Module):
    def __init__(self):
        super(SimpleNN, self).__init__()
        # Define layers
        self.fc1 = nn.Linear(16, 128)  # Input: 16 features -> 32 hidden neurons
        self.fc2 = nn.Linear(128,128)  # 
        self.fc3 = nn.Linear(128,128)  
        self.fc4 = nn.Linear(128, 1)  # Output: 1 neuron for regression output

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        x = self.fc3(x)
        x = self.fc4(x)
        return x

# Initialize the model
model = ConvAttentionNN()

# Check if pretrained parameters exist
if os.path.exists('parm.npz'):
    # Load pre-trained parameters
    params = np.load('parm.npz')
    print("Loading pretrained parameters from parm.npz...")
    with torch.no_grad():
        model.fc1.weight.copy_(torch.tensor(params['w1'], dtype=torch.float32))
        model.fc1.bias.copy_(torch.tensor(params['b1'], dtype=torch.float32))
        model.fc2.weight.copy_(torch.tensor(params['w2'], dtype=torch.float32))
        model.fc2.bias.copy_(torch.tensor(params['b2'], dtype=torch.float32))
else:
    # If parm.npz doesn't exist, weights will be randomly initialized
    print("parm.npz not found. Initializing weights randomly.")

# Define loss function and optimizer
criterion = nn.MSELoss()  # Mean squared error for regression
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
epochs = 100
for epoch in range(epochs):
    # Forward pass
    outputs = model(data)
    loss = criterion(outputs, labels)
    
    # Backward pass and optimization
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 10 == 0:
        print(f'Epoch [{epoch + 1}/{epochs}], Loss: {loss.item():.4f}')

# Save the updated parameters back into parm.npz
updated_params = {
    'w1': model.fc1.weight.detach().numpy(),
    'b1': model.fc1.bias.detach().numpy(),
    'w2': model.fc2.weight.detach().numpy(),
    'b2': model.fc2.bias.detach().numpy(),
}
np.savez('parm.npz', **updated_params)
print("Updated parameters saved to parm.npz.")
