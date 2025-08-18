import torch
from torch.utils.data import Dataset
import random

class CustomDataset(Dataset):
    def __init__(self, max_size=None):
        self.data = []
        self.labels = []
        self.max_size = max_size

    def add_sample(self, input_data, label):
        self.data.append(input_data)
        self.labels.append(label)

        # Check if the buffer exceeds the maximum size
        if self.max_size is not None and len(self.data) > self.max_size:
            # Remove a random sample to maintain the buffer size
            idx_to_remove = random.randint(0, len(self.data) - 1)
            del self.data[idx_to_remove]
            del self.labels[idx_to_remove]

        """# Check if the buffer exceeds the maximum size
        if self.max_size is not None and len(self.data) > self.max_size:
            # Remove a random sample to maintain the buffer size
            idx_to_remove = torch.randint(0, len(self.data), (1,), device=self.device).item()
            del self.data[idx_to_remove]
            del self.labels[idx_to_remove]"""

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

class SimpleNN(torch.nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.fc1 = torch.nn.Linear(in_features, 128)
        self.fc2 = torch.nn.Linear(128, 64)
        self.fc3 = torch.nn.Linear(64, out_features)

        self.dataset = CustomDataset(max_size=100000)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x
    
    def train_network(self, batch_size=512, epochs=1000, learning_rate=1e-3, device='cpu'):
        with torch.inference_mode(False):
            with torch.enable_grad():
                # Define optimizer and loss function
                optimizer = torch.optim.Adam(self.parameters(), lr=learning_rate)
                loss_fn = torch.nn.MSELoss()
    
                # Create a DataLoader for batching
                dataloader = torch.utils.data.DataLoader(
                    self.dataset,
                    batch_size=batch_size,
                    shuffle=True
                )
    
                # Training loop
                self.train()
                for epoch in range(epochs):
                    for inputs, targets in dataloader:
                    
                        # Forward pass
                        inputs = inputs.view(-1, inputs.size(-1))
                        targets = targets.view(-1, targets.size(-1))
                        predictions = self(inputs)
    
                        loss = loss_fn(predictions, targets)
    
                        # Backward pass and optimization
                        optimizer.zero_grad()
                        loss.backward()
                        optimizer.step()
    
                    print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss.item()}")
    
    

model = SimpleNN(10, 2)
x = torch.randn(4, 10)
y = torch.randn(4, 2)
out = model(x)
print("out.requires_grad:", out.requires_grad)
loss = torch.nn.MSELoss()(out, y)
print("loss.requires_grad:", loss.requires_grad)