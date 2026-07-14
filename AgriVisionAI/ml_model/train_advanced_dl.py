"""
Advanced Deep Learning Architectures for Crop Recommendation
Implements: Attention-Enhanced MLP (SE-Net), LSTM, GRU
As requested by Dr. Abir Sen's revision requirements.
"""
import os
import time
import pandas as pd
import numpy as np
import joblib
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# ============================================================
# MODEL DEFINITIONS
# ============================================================

class SEBlock(nn.Module):
    """Squeeze-and-Excitation (SE) Attention Block for feature recalibration."""
    def __init__(self, channels, reduction=2):
        super().__init__()
        self.fc1 = nn.Linear(channels, channels // reduction)
        self.fc2 = nn.Linear(channels // reduction, channels)
    
    def forward(self, x):
        # Squeeze: x is already a 1D feature vector, so we skip global pooling
        s = torch.relu(self.fc1(x))
        s = torch.sigmoid(self.fc2(s))  # Excitation
        return x * s  # Scale


class AttentionMLP(nn.Module):
    """MLP with SE-Net style channel attention on input features."""
    def __init__(self, n_features, n_classes):
        super().__init__()
        self.se = SEBlock(n_features, reduction=2)
        self.net = nn.Sequential(
            nn.Linear(n_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Linear(64, n_classes)
        )
    
    def forward(self, x):
        x = self.se(x)  # Attention-weighted features
        return self.net(x)


class LSTMClassifier(nn.Module):
    """LSTM treating each feature as a time-step in a sequence."""
    def __init__(self, n_features, n_classes, hidden_size=64, num_layers=2):
        super().__init__()
        # Each feature is treated as a 1-dimensional time step
        self.lstm = nn.LSTM(input_size=1, hidden_size=hidden_size,
                           num_layers=num_layers, batch_first=True,
                           dropout=0.2)
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Linear(64, n_classes)
        )
    
    def forward(self, x):
        # x: (batch, n_features) -> (batch, n_features, 1) for LSTM
        x = x.unsqueeze(-1)
        lstm_out, (h_n, _) = self.lstm(x)
        # Use the last hidden state
        out = h_n[-1]
        return self.fc(out)


class GRUClassifier(nn.Module):
    """GRU treating each feature as a time-step in a sequence."""
    def __init__(self, n_features, n_classes, hidden_size=64, num_layers=2):
        super().__init__()
        self.gru = nn.GRU(input_size=1, hidden_size=hidden_size,
                          num_layers=num_layers, batch_first=True,
                          dropout=0.2)
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Linear(64, n_classes)
        )
    
    def forward(self, x):
        x = x.unsqueeze(-1)
        gru_out, h_n = self.gru(x)
        out = h_n[-1]
        return self.fc(out)


# ============================================================
# TRAINING UTILITIES
# ============================================================

def train_pytorch_model(model, X_train, y_train, X_test, y_test,
                        model_name, epochs=100, lr=1e-3, batch_size=128):
    """Generic PyTorch training loop with metrics collection."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    X_tr_t = torch.tensor(X_train, dtype=torch.float32)
    y_tr_t = torch.tensor(y_train, dtype=torch.long)
    X_te_t = torch.tensor(X_test, dtype=torch.float32).to(device)
    
    dataset = TensorDataset(X_tr_t, y_tr_t)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    
    # Training
    print(f"  Training {model_name}...")
    start_time = time.time()
    model.train()
    for epoch in range(epochs):
        for bx, by in loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad()
            pred = model(bx)
            loss = criterion(pred, by)
            loss.backward()
            optimizer.step()
    train_time = time.time() - start_time
    
    # Inference with FPS measurement
    model.eval()
    n_samples = len(X_te_t)
    
    start_time = time.time()
    with torch.no_grad():
        preds = model(X_te_t).argmax(dim=1).cpu().numpy()
    inference_time = time.time() - start_time
    
    fps = n_samples / inference_time if inference_time > 0 else float('inf')
    
    acc = accuracy_score(y_test, preds)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, preds, average='weighted')
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    
    return {
        'Model': model_name,
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1-score': f1,
        'Training Time (s)': round(train_time, 2),
        'Inference Time (s)': round(inference_time, 6),
        'FPS': round(fps, 1),
        'Parameters': total_params
    }


# ============================================================
# MAIN
# ============================================================

def main():
    os.makedirs('models/deep_learning', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # Load data
    data_path = os.path.join('ml_model', 'dataset', 'Crop_recommendation.csv')
    try:
        data = pd.read_csv(data_path)
    except FileNotFoundError:
        data = pd.read_csv(os.path.join('..', 'ml_model', 'dataset', 'Crop_recommendation.csv'))
    
    X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].values
    y = data['label'].values
    
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    n_features = X.shape[1]
    n_classes = len(le.classes_)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    results = []
    
    # 1. Attention-Enhanced MLP (SE-Net)
    model_attn = AttentionMLP(n_features, n_classes)
    res = train_pytorch_model(model_attn, X_train_scaled, y_train, X_test_scaled, y_test,
                              'Attention-MLP (SE-Net)', epochs=150, lr=1e-3)
    results.append(res)
    torch.save(model_attn.state_dict(), os.path.join('models', 'deep_learning', 'attention_mlp.pt'))
    
    # 2. LSTM Classifier
    model_lstm = LSTMClassifier(n_features, n_classes)
    res = train_pytorch_model(model_lstm, X_train_scaled, y_train, X_test_scaled, y_test,
                              'LSTM', epochs=100, lr=1e-3)
    results.append(res)
    torch.save(model_lstm.state_dict(), os.path.join('models', 'deep_learning', 'lstm_model.pt'))
    
    # 3. GRU Classifier
    model_gru = GRUClassifier(n_features, n_classes)
    res = train_pytorch_model(model_gru, X_train_scaled, y_train, X_test_scaled, y_test,
                              'GRU', epochs=100, lr=1e-3)
    results.append(res)
    torch.save(model_gru.state_dict(), os.path.join('models', 'deep_learning', 'gru_model.pt'))
    
    # Print results
    print("\n" + "="*80)
    print("ADVANCED DL ARCHITECTURE RESULTS")
    print("="*80)
    for r in results:
        print(f"{r['Model']:25s}  Acc: {r['Accuracy']:.4f}  F1: {r['F1-score']:.4f}  "
              f"FPS: {r['FPS']:.1f}  Params: {r['Parameters']}")
    
    # Save results
    df = pd.DataFrame(results)
    df.to_csv(os.path.join('reports', 'advanced_dl_results.csv'), index=False)
    print("\nResults saved to reports/advanced_dl_results.csv")


if __name__ == '__main__':
    main()
