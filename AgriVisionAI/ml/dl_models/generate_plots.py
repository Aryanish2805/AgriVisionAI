import os
import sys
import torch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dl_models.dataset import CropDataset
from dl_models.cnn_attention import CNNAttentionModel
from torch.utils.data import DataLoader

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "dataset", "Crop_recommendation_kaggle.csv")
    
    df = pd.read_csv(dataset_path)
    label_col = 'label' if 'label' in df.columns else 'crop'
    df = df.dropna(subset=[label_col])
    
    train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42, stratify=df.get(label_col))
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df.get(label_col))
    
    noise_level = 0.70
    train_set = CropDataset(dataframe=train_df, is_train=True, noise_level=noise_level)
    test_set = CropDataset(dataframe=test_df, scaler=train_set.scaler, is_train=False, noise_level=noise_level)
    
    test_loader = DataLoader(test_set, batch_size=64, shuffle=False)
    
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models", "cnn_attention.pth")
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return
        
    num_features = train_set.get_num_features()
    num_classes = train_set.get_num_classes()
    
    model = CNNAttentionModel(num_features=num_features, num_classes=num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    model.to(device)
    model.eval()
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    cm = confusion_matrix(all_labels, all_preds)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    cax = ax.matshow(cm, cmap='Blues')
    plt.colorbar(cax)
    
    for (i, j), z in np.ndenumerate(cm):
        ax.text(j, i, '{:d}'.format(z), ha='center', va='center')
        
    ax.set_xticks(np.arange(len(train_set.classes)))
    ax.set_yticks(np.arange(len(train_set.classes)))
    ax.set_xticklabels(train_set.classes, rotation=45, ha='right')
    ax.set_yticklabels(train_set.classes)
    
    plt.title('Confusion Matrix - CNN + Attention')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.tight_layout()
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "reports", "figures")
    os.makedirs(out_dir, exist_ok=True)
    plt.savefig(os.path.join(out_dir, 'confusion_matrix.png'), dpi=300)
    print("Saved confusion matrix.")

if __name__ == "__main__":
    main()
