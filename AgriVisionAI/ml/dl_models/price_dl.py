import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os
import joblib

class PriceDataset(Dataset):
    def __init__(self, X, y):
        # We add an extra dimension for LSTM: (batch, seq_len, features) where seq_len=1
        self.X = torch.tensor(X, dtype=torch.float32).unsqueeze(1)
        self.y = torch.tensor(y, dtype=torch.float32).unsqueeze(1)
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class PricePredictionLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim=1):
        super(PricePredictionLSTM, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2)
        self.fc1 = nn.Linear(hidden_dim, 64)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(64, output_dim)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        
        out, _ = self.lstm(x, (h0, c0))
        # Take the output of the last time step
        out = out[:, -1, :]
        out = self.fc1(out)
        out = self.relu(out)
        out = self.fc2(out)
        return out

def train_price_model(data_path, save_dir='ml/models', epochs=30, batch_size=64):
    print("Loading price data...")
    df = pd.read_csv(data_path)
    
    # Select features
    features = ['year', 'month', 'state_code', 'district_code', 'market_code', 'commodity_code', 'variety_code', 'grade_code']
    X = df[features].values
    y = df['modal_price'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    feature_scaler = StandardScaler()
    X_train_scaled = feature_scaler.fit_transform(X_train)
    X_test_scaled = feature_scaler.transform(X_test)
    
    # Scale target (important for LSTM regression)
    target_scaler = MinMaxScaler()
    y_train_scaled = target_scaler.fit_transform(y_train.reshape(-1, 1)).flatten()
    y_test_scaled = target_scaler.transform(y_test.reshape(-1, 1)).flatten()
    
    os.makedirs(save_dir, exist_ok=True)
    joblib.dump(feature_scaler, os.path.join(save_dir, 'price_feature_scaler.pkl'))
    joblib.dump(target_scaler, os.path.join(save_dir, 'price_target_scaler.pkl'))
    
    train_dataset = PriceDataset(X_train_scaled, y_train_scaled)
    test_dataset = PriceDataset(X_test_scaled, y_test_scaled)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    input_dim = X.shape[1]
    hidden_dim = 128
    num_layers = 2
    
    model = PricePredictionLSTM(input_dim, hidden_dim, num_layers)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print(f"Training started for {epochs} epochs...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs} - MSE Loss: {running_loss/len(train_loader):.4f}")
            
    # Evaluation
    model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            all_preds.extend(outputs.numpy())
            all_labels.extend(labels.numpy())
            
    all_preds = np.array(all_preds).flatten()
    all_labels = np.array(all_labels).flatten()
    
    # Inverse transform to get actual prices
    preds_actual = target_scaler.inverse_transform(all_preds.reshape(-1, 1)).flatten()
    labels_actual = target_scaler.inverse_transform(all_labels.reshape(-1, 1)).flatten()
    
    mae = mean_absolute_error(labels_actual, preds_actual)
    rmse = np.sqrt(mean_squared_error(labels_actual, preds_actual))
    r2 = r2_score(labels_actual, preds_actual)
    
    print(f"Test MAE: {mae:.2f}")
    print(f"Test RMSE: {rmse:.2f}")
    print(f"Test R2 Score: {r2:.4f}")
    
    # Save the model
    torch.save(model.state_dict(), os.path.join(save_dir, 'price_dl_model.pth'))
    print(f"Model and scalers saved to {save_dir}")

if __name__ == '__main__':
    train_price_model('ml/datasets/price_recommendation_preprocessed.csv')
