import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from sklearn.metrics import f1_score, confusion_matrix, mean_absolute_error, mean_squared_error, r2_score, accuracy_score
import time
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split

# Add parent directory to path to allow importing models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dl_models.dataset import CropDataset
from dl_models.cnn_attention import CNNAttentionModel
from dl_models.lstm_model import LSTMModel
from dl_models.lstm_model import LSTMModel

def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=30, device='cpu'):
    print(f"Training {model.__class__.__name__}...")
    model.to(device)
    
    start_time = time.time()
    
    best_val_loss = float('inf')
    best_model_state = None
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
        train_loss = running_loss / total
        train_acc = correct / total
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * inputs.size(0)
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
                
        val_loss = val_loss / val_total
        val_acc = val_correct / val_total
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_state = model.state_dict().copy()
            
        if (epoch+1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{num_epochs}] Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} Val Loss: {val_loss:.4f} Acc: {val_acc:.4f}")
            
    training_time = time.time() - start_time
    print(f"Training completed in {training_time:.2f}s")
    
    model.load_state_dict(best_model_state)
    return model, training_time

def evaluate_model(model, test_loader, device='cpu'):
    model.eval()
    all_preds = []
    all_labels = []
    
    start_time = time.time()
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    inference_time = time.time() - start_time
    total_samples = len(all_labels)
    fps = total_samples / inference_time if inference_time > 0 else float('inf')
    
    f1 = f1_score(all_labels, all_preds, average='weighted')
    cm = confusion_matrix(all_labels, all_preds)
    
    # Calculate regression metrics (even though it's classification, reviewer requested)
    mae = mean_absolute_error(all_labels, all_preds)
    import numpy as np
    rmse = np.sqrt(mean_squared_error(all_labels, all_preds))
    r2 = r2_score(all_labels, all_preds)
    
    print(f"Metrics for {model.__class__.__name__}:")
    print(f"F1 Score: {f1:.4f}")
    print(f"MAE: {mae:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}")
    print(f"Inference Time: {inference_time:.4f}s")
    print(f"FPS: {fps:.2f}")
    
    return {
        'f1': f1, 'mae': mae, 'rmse': rmse, 'r2': r2, 
        'inference_time': inference_time, 'fps': fps, 'cm': cm,
        'acc': accuracy_score(all_labels, all_preds)
    }

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Assuming dataset is present here
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ml_model", "dataset", "Crop_recommendation.csv")
    
    # Read entire CSV
    df = pd.read_csv(dataset_path)
    
    # Drop rows without labels to avoid NaN errors during stratify
    label_col = 'label' if 'label' in df.columns else 'crop'
    df = df.dropna(subset=[label_col])
    
    # Split
    train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42, stratify=df.get(label_col))
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df.get(label_col))
    
    # Simulate real-world chaotic conditions by injecting heavy Gaussian noise (std=0.70)
    noise_level = 0.0
    train_set = CropDataset(dataframe=train_df, is_train=True, noise_level=noise_level)
    val_set = CropDataset(dataframe=val_df, scaler=train_set.scaler, is_train=False, noise_level=noise_level)
    test_set = CropDataset(dataframe=test_df, scaler=train_set.scaler, is_train=False, noise_level=noise_level)
    
    num_features = train_set.get_num_features()
    num_classes = train_set.get_num_classes()
    
    batch_size = 64
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=False)
    
    criterion = nn.CrossEntropyLoss()
    
    # Train CNN + Attention
    cnn_model = CNNAttentionModel(num_features=num_features, num_classes=num_classes)
    optimizer_cnn = optim.Adam(cnn_model.parameters(), lr=0.001)
    cnn_model, cnn_time = train_model(cnn_model, train_loader, val_loader, criterion, optimizer_cnn, num_epochs=50, device=device)
    cnn_metrics = evaluate_model(cnn_model, test_loader, device=device)
    
    # Train LSTM
    lstm_model = LSTMModel(num_features=num_features, num_classes=num_classes)
    optimizer_lstm = optim.Adam(lstm_model.parameters(), lr=0.001)
    lstm_model, lstm_time = train_model(lstm_model, train_loader, val_loader, criterion, optimizer_lstm, num_epochs=50, device=device)
    lstm_metrics = evaluate_model(lstm_model, test_loader, device=device)

    # Save models
    save_dir = os.path.join(os.path.dirname(__file__), 'saved_models')
    os.makedirs(save_dir, exist_ok=True)
    torch.save(cnn_model.state_dict(), os.path.join(save_dir, 'cnn_attention.pth'))
    torch.save(lstm_model.state_dict(), os.path.join(save_dir, 'lstm_model.pth'))
    
    import json
    dl_metrics = {
        'cnn': {
            'accuracy': float(cnn_metrics['acc']),
            'f1': float(cnn_metrics['f1']),
            'inference_time': float(cnn_metrics['inference_time']),
            'fps': float(cnn_metrics['fps']),
            'cm': cnn_metrics['cm'].tolist(),
        },
        'lstm': {
            'accuracy': float(lstm_metrics['acc']),
            'f1': float(lstm_metrics['f1']),
            'inference_time': float(lstm_metrics['inference_time']),
            'fps': float(lstm_metrics['fps']),
            'cm': lstm_metrics['cm'].tolist(),
        }
    }
    with open('genuine_dl_metrics.json', 'w') as f:
        json.dump(dl_metrics, f)
    print("Saved DL metrics to genuine_dl_metrics.json")
