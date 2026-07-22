import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.metrics import f1_score, confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
import time
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
import json
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dl_models.dataset import CropDataset
from dl_models.cnn_attention import CNNAttentionModel
from dl_models.lstm_model import LSTMModel

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
    
    acc = np.mean(np.array(all_preds) == np.array(all_labels))
    f1 = f1_score(all_labels, all_preds, average='weighted')
    cm = confusion_matrix(all_labels, all_preds).tolist()
    
    from sklearn.metrics import precision_score, recall_score
    precisions = precision_score(all_labels, all_preds, average=None, zero_division=0).tolist()
    recalls = recall_score(all_labels, all_preds, average=None, zero_division=0).tolist()
    f1s = f1_score(all_labels, all_preds, average=None, zero_division=0).tolist()
    
    mae = mean_absolute_error(all_labels, all_preds)
    rmse = np.sqrt(mean_squared_error(all_labels, all_preds))
    r2 = r2_score(all_labels, all_preds)
    
    return {
        'accuracy': float(acc),
        'f1': float(f1), 
        'mae': float(mae), 
        'rmse': float(rmse), 
        'r2': float(r2), 
        'inference_time': float(inference_time), 
        'fps': float(fps), 
        'cm': cm,
        'precisions': precisions,
        'recalls': recalls,
        'f1s': f1s
    }

if __name__ == "__main__":
    device = torch.device("cpu")
    print(f"Using device: {device}")
    
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ml_model", "dataset", "Crop_recommendation.csv")
    df = pd.read_csv(dataset_path)
    
    label_col = 'label' if 'label' in df.columns else 'crop'
    df = df.dropna(subset=[label_col])
    
    train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42, stratify=df.get(label_col))
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df.get(label_col))
    
    # 1. Clean data evaluation
    train_set = CropDataset(dataframe=train_df, is_train=True, noise_level=0.0)
    test_set = CropDataset(dataframe=test_df, scaler=train_set.scaler, is_train=False, noise_level=0.0)
    
    # 2. Noisy data evaluation (std=0.70)
    noisy_test_set = CropDataset(dataframe=test_df, scaler=train_set.scaler, is_train=False, noise_level=0.70)
    
    num_features = train_set.get_num_features()
    num_classes = train_set.get_num_classes()
    
    batch_size = 64
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=False)
    noisy_test_loader = DataLoader(noisy_test_set, batch_size=batch_size, shuffle=False)
    
    cnn_model = CNNAttentionModel(num_features=num_features, num_classes=num_classes)
    cnn_model.load_state_dict(torch.load('ml/dl_models/saved_models/cnn_attention.pth', map_location=device))
    
    lstm_model = LSTMModel(num_features=num_features, num_classes=num_classes)
    lstm_model.load_state_dict(torch.load('ml/dl_models/saved_models/lstm_model.pth', map_location=device))
    
    results = {}
    
    print("Evaluating CNN (Clean)...")
    results['cnn_clean'] = evaluate_model(cnn_model, test_loader, device)
    
    print("Evaluating CNN (Noisy std=0.70)...")
    results['cnn_noisy'] = evaluate_model(cnn_model, noisy_test_loader, device)
    
    print("Evaluating LSTM (Clean)...")
    results['lstm_clean'] = evaluate_model(lstm_model, test_loader, device)
    
    print("Evaluating LSTM (Noisy std=0.70)...")
    results['lstm_noisy'] = evaluate_model(lstm_model, noisy_test_loader, device)
    
    results['classes'] = list(train_set.label_encoder.classes_)
    
    with open('genuine_metrics.json', 'w') as f:
        json.dump(results, f)
    print("Saved genuine metrics to genuine_metrics.json")
