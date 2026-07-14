import os
import sys
import torch
import pandas as pd
from sklearn.model_selection import train_test_split

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml"))

from ml.dl_models.dataset import CropDataset
from ml.dl_models.cnn_attention import CNNAttentionModel

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "dataset", "Crop_recommendation_kaggle.csv")
    model_path = os.path.join(base_dir, "ml", "dl_models", "saved_models", "cnn_attention.pth")
    
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        print("Please run the training script first: python ml/dl_models/train.py")
        return
        
    print("Loading dataset to initialize scaler and classes...")
    df = pd.read_csv(dataset_path)
    label_col = 'label' if 'label' in df.columns else 'crop'
    df = df.dropna(subset=[label_col])
    
    # We must replicate the same split used in train.py to get the exact same scaler
    train_df, _ = train_test_split(df, test_size=0.3, random_state=42, stratify=df.get(label_col))
    train_set = CropDataset(dataframe=train_df, is_train=True)
    
    num_features = train_set.get_num_features()
    num_classes = train_set.get_num_classes()
    
    print("Loading CNN + Attention model...")
    model = CNNAttentionModel(num_features=num_features, num_classes=num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    model.to(device)
    model.eval()
    
    print("\n--- Testing Model on a Random Sample ---")
    # Take a random row from the dataframe
    sample = df.sample(1, random_state=123)
    
    # The features are: N, P, K, temperature, humidity, ph, rainfall
    feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    if 'N' not in sample.columns:
        feature_cols = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']
        
    raw_features = sample[feature_cols].values
    true_label = sample[label_col].values[0]
    
    # Scale the features using the scaler fit on the training set
    scaled_features = train_set.scaler.transform(raw_features)
    
    # Convert to tensor
    inputs = torch.tensor(scaled_features, dtype=torch.float32).to(device)
    
    # Predict
    with torch.no_grad():
        outputs = model(inputs)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        _, predicted_idx = torch.max(outputs.data, 1)
        
    predicted_class = train_set.classes[predicted_idx.item()]
    confidence = probabilities[0][predicted_idx.item()].item() * 100
    
    print("Input Features:")
    for col, val in zip(feature_cols, raw_features[0]):
        print(f"  {col}: {val}")
        
    print(f"\nTrue Crop: {true_label}")
    print(f"Predicted Crop: {predicted_class}")
    print(f"Confidence: {confidence:.2f}%")
    
    if true_label == predicted_class:
        print("✅ Prediction is CORRECT!")
    else:
        print("❌ Prediction is INCORRECT.")

if __name__ == "__main__":
    main()
