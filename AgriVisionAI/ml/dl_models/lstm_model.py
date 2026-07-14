import torch
import torch.nn as nn

class LSTMModel(nn.Module):
    def __init__(self, num_features, num_classes, hidden_size=64, num_layers=2):
        super(LSTMModel, self).__init__()
        # Treating each feature as a timestep, or we can treat the whole vector as 1 timestep.
        # Given tabular nature, we'll treat it as a sequence of length 1 with `num_features` dimensions,
        # or sequence of `num_features` with 1 dimension.
        # Let's treat it as sequence of `num_features` with 1 dimension to leverage LSTM dynamics.
        
        self.lstm = nn.LSTM(input_size=1, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)
        self.fc1 = nn.Linear(hidden_size, 64)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(64, num_classes)

    def forward(self, x):
        # x is (Batch, num_features)
        # Reshape to (Batch, num_features, 1)
        x = x.unsqueeze(2)
        
        # LSTM output: out is (batch, seq_len, hidden_size)
        out, (hn, cn) = self.lstm(x)
        
        # Take the output of the last timestep
        out = out[:, -1, :] 
        
        out = self.relu(self.fc1(out))
        out = self.fc2(out)
        return out
