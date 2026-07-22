import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from sklearn.metrics import precision_score, recall_score
import time
import json
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def evaluate_sklearn(model, X_test, y_test, name):
    start_time = time.time()
    preds = model.predict(X_test)
    inference_time = time.time() - start_time
    total_samples = len(y_test)
    fps = total_samples / inference_time if inference_time > 0 else float('inf')
    
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds, average='weighted')
    cm = confusion_matrix(y_test, preds).tolist()
    
    precisions = precision_score(y_test, preds, average=None, zero_division=0).tolist()
    recalls = recall_score(y_test, preds, average=None, zero_division=0).tolist()
    f1s = f1_score(y_test, preds, average=None, zero_division=0).tolist()
    
    return {
        'accuracy': float(acc),
        'f1': float(f1),
        'inference_time': float(inference_time),
        'fps': float(fps),
        'cm': cm,
        'precisions': precisions,
        'recalls': recalls,
        'f1s': f1s,
        'feature_importances': getattr(model, 'feature_importances_', []).tolist() if hasattr(model, 'feature_importances_') else []
    }

if __name__ == "__main__":
    df = pd.read_csv('/Users/adarsh/Desktop/RESEARCH/AgriVisionAI/AgriVisionAI/ml_model/dataset/Crop_recommendation.csv')
    label_col = 'label' if 'label' in df.columns else 'crop'
    
    X = df.drop(columns=[label_col])
    y = df[label_col]
    
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)
    
    results = {}
    
    try:
        rf_model = joblib.load('/Users/adarsh/Desktop/RESEARCH/AgriVisionAI/AgriVisionAI/ml_model/crop_model.pkl')
        print("Loaded Random Forest!")
        results['rf'] = evaluate_sklearn(rf_model, X_test, y_test, "Random Forest")
    except Exception as e:
        print("Failed to load RF:", e)
        
    try:
        scaler = joblib.load('/Users/adarsh/Desktop/RESEARCH/AgriVisionAI/AgriVisionAI/models/deep_learning/dl_scaler.pkl')
        encoder = joblib.load('/Users/adarsh/Desktop/RESEARCH/AgriVisionAI/AgriVisionAI/models/deep_learning/dl_label_encoder.pkl')
        X_test_scaled = scaler.transform(X_test)
        mlp_model = joblib.load('/Users/adarsh/Desktop/RESEARCH/AgriVisionAI/AgriVisionAI/models/deep_learning/mlp_model.pkl')
        print("Loaded MLP!")
        
        start_time = time.time()
        preds = mlp_model.predict(X_test_scaled)
        inference_time = time.time() - start_time
        
        preds_labels = encoder.inverse_transform(preds)
        
        acc = accuracy_score(y_test, preds_labels)
        f1 = f1_score(y_test, preds_labels, average='weighted')
        cm = confusion_matrix(y_test, preds_labels).tolist()
        
        precisions = precision_score(y_test, preds_labels, average=None, zero_division=0).tolist()
        recalls = recall_score(y_test, preds_labels, average=None, zero_division=0).tolist()
        f1s = f1_score(y_test, preds_labels, average=None, zero_division=0).tolist()
        
        results['mlp'] = {
            'accuracy': float(acc),
            'f1': float(f1),
            'inference_time': float(inference_time),
            'fps': float(len(y_test) / inference_time if inference_time > 0 else float('inf')),
            'cm': cm,
            'precisions': precisions,
            'recalls': recalls,
            'f1s': f1s,
            'feature_importances': getattr(mlp_model, 'feature_importances_', []).tolist() if hasattr(mlp_model, 'feature_importances_') else []
        }
    except Exception as e:
        print("Failed to load MLP:", e)
        
    results['classes'] = list(np.unique(y))
    
    with open('/Users/adarsh/Desktop/RESEARCH/AgriVisionAI/AgriVisionAI/genuine_ml_metrics.json', 'w') as f:
        json.dump(results, f)
    print("Saved to genuine_ml_metrics.json")
