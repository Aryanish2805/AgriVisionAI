import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import os
import joblib

class FertilizerDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class FertilizerRecommendationModel(nn.Module):
    def __init__(self, input_dim, num_classes):
        super(FertilizerRecommendationModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.4),
            
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            
            nn.Linear(64, num_classes)
        )
        
    def forward(self, x):
        return self.network(x)

def train_fertilizer_model(data_path, save_dir='ml/models', epochs=50, batch_size=64):
    print("Loading fertilizer data...")
    df = pd.read_csv(data_path)
    
    # Exclude scaled and target columns from features
    exclude_cols = [col for col in df.columns if '_scaled' in col or 'recommended_fertilizer_' in col or col == 'fertilizer_code']
    features = [col for col in df.columns if col not in exclude_cols]
    
    # Convert boolean to float
    for col in features:
        if df[col].dtype == bool:
            df[col] = df[col].astype(float)
            
    X = df[features].values
    y = df['fertilizer_code'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    os.makedirs(save_dir, exist_ok=True)
    joblib.dump(scaler, os.path.join(save_dir, 'fertilizer_scaler.pkl'))
    
    # Save the feature list so it can be loaded during inference
    joblib.dump(features, os.path.join(save_dir, 'fertilizer_features.pkl'))
    
    train_dataset = FertilizerDataset(X_train_scaled, y_train)
    test_dataset = FertilizerDataset(X_test_scaled, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # Remap labels to 0..num_classes-1 to avoid CUDA out of bounds if codes are not sequential
    unique_classes = np.unique(y)
    num_classes = len(unique_classes)
    
    label_map = {label: idx for idx, label in enumerate(unique_classes)}
    joblib.dump(label_map, os.path.join(save_dir, 'fertilizer_label_map.pkl'))
    
    y_train_mapped = np.array([label_map[label] for label in y_train])
    y_test_mapped = np.array([label_map[label] for label in y_test])
    
    train_dataset.y = torch.tensor(y_train_mapped, dtype=torch.long)
    test_dataset.y = torch.tensor(y_test_mapped, dtype=torch.long)
    
    input_dim = X.shape[1]
    
    model = FertilizerRecommendationModel(input_dim, num_classes)
    criterion = nn.CrossEntropyLoss()
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
            print(f"Epoch {epoch+1}/{epochs} - Loss: {running_loss/len(train_loader):.4f}")
            
    # Evaluation
    model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.numpy())
            all_labels.extend(labels.numpy())
            
    acc = accuracy_score(all_labels, all_preds)
    print(f"Test Accuracy: {acc * 100:.2f}%")
    
    # Save the model
    torch.save(model.state_dict(), os.path.join(save_dir, 'fertilizer_dl_model.pth'))
    print(f"Model and scaler saved to {save_dir}")

if __name__ == '__main__':
    train_fertilizer_model('ml/datasets/fertilizer_recommendation_preprocessed.csv')
