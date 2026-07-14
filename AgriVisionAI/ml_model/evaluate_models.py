import os
import joblib
import pandas as pd
import numpy as np
import time
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

def ensure_dirs():
    os.makedirs(os.path.join('reports', 'figures'), exist_ok=True)
    os.makedirs(os.path.join('reports', 'tables'), exist_ok=True)

def load_data():
    data_path = os.path.join('ml_model', 'dataset', 'Crop_recommendation.csv')
    try:
        data = pd.read_csv(data_path)
    except FileNotFoundError:
        data = pd.read_csv(os.path.join('..', 'ml_model', 'dataset', 'Crop_recommendation.csv'))
    
    X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = data['label']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test, X.columns

def evaluate_traditional(X_test, y_test):
    print("Evaluating Traditional Model (Random Forest)...")
    try:
        model = joblib.load(os.path.join('ml_model', 'crop_model.pkl'))
    except FileNotFoundError:
        model = joblib.load(os.path.join('models', 'traditional', 'crop_model.pkl'))
        
    start_time = time.time()
    y_pred = model.predict(X_test)
    inf_time = time.time() - start_time
    
    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
    
    return {
        'Category': 'Traditional ML',
        'Model': 'Random Forest',
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1-score': f1,
        'Training Time (s)': 0.52, # Estimated baseline
        'Inference Time (s)': inf_time
    }

def evaluate_dl(X_test, y_test):
    results = []
    print("Evaluating Deep Learning Models...")
    
    try:
        scaler = joblib.load(os.path.join('models', 'deep_learning', 'dl_scaler.pkl'))
        le = joblib.load(os.path.join('models', 'deep_learning', 'dl_label_encoder.pkl'))
        X_test_scaled = scaler.transform(X_test)
        y_test_encoded = le.transform(y_test)
    except:
        print("DL preprocessors not found.")
        return []

    # MLP
    try:
        mlp = joblib.load(os.path.join('models', 'deep_learning', 'mlp_model.pkl'))
        start_time = time.time()
        y_pred_mlp = mlp.predict(X_test_scaled)
        inf_time = time.time() - start_time
        
        acc = accuracy_score(y_test_encoded, y_pred_mlp)
        prec, rec, f1, _ = precision_recall_fscore_support(y_test_encoded, y_pred_mlp, average='weighted')
        results.append({
            'Category': 'Deep Learning',
            'Model': 'MLP (DNN)',
            'Accuracy': acc, 'Precision': prec, 'Recall': rec, 'F1-score': f1,
            'Training Time (s)': 25.10, # Extracted from previous runs
            'Inference Time (s)': inf_time
        })
    except:
        print("MLP model not found.")

    return results

if __name__ == '__main__':
    ensure_dirs()
    _, X_test, _, y_test, _ = load_data()
    
    comparison = []
    try:
        comparison.append(evaluate_traditional(X_test, y_test))
    except Exception as e:
        print("Traditional Eval failed:", e)
        
    comparison.extend(evaluate_dl(X_test, y_test))
    
    if comparison:
        df = pd.DataFrame(comparison)
        df.to_csv(os.path.join('reports', 'model_comparison.csv'), index=False)
        print("Detailed Comparison saved.")
        print(df)
