import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc, precision_recall_curve
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize

def ensure_dirs():
    os.makedirs(os.path.join('reports', 'figures'), exist_ok=True)

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

def generate_figures():
    ensure_dirs()
    _, X_test, _, y_test, _ = load_data()
    
    try:
        scaler = joblib.load(os.path.join('models', 'deep_learning', 'dl_scaler.pkl'))
        le = joblib.load(os.path.join('models', 'deep_learning', 'dl_label_encoder.pkl'))
        mlp = joblib.load(os.path.join('models', 'deep_learning', 'mlp_model.pkl'))
    except Exception as e:
        print("Required models/scalers missing:", e)
        return

    X_test_scaled = scaler.transform(X_test)
    y_test_encoded = le.transform(y_test)
    y_pred = mlp.predict(X_test_scaled)
    y_probs = mlp.predict_proba(X_test_scaled)
    
    classes = le.classes_
    
    # 1. Confusion Matrix
    print("Generating Confusion Matrix...")
    cm = confusion_matrix(y_test_encoded, y_pred)
    # We will plot directly to avoid large display issues with 22 classes
    fig, ax = plt.subplots(figsize=(12, 10))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
    disp.plot(cmap=plt.cm.Blues, ax=ax, xticks_rotation='vertical')
    plt.title("Confusion Matrix (MLP)")
    plt.tight_layout()
    plt.savefig(os.path.join('reports', 'figures', 'confusion_matrix.png'), dpi=300)
    plt.close()
    
    # 2. ROC Curve for top 5 classes (to avoid clutter)
    print("Generating ROC Curve...")
    y_test_bin = label_binarize(y_test_encoded, classes=range(len(classes)))
    plt.figure(figsize=(10, 8))
    for i in range(5): # Plot first 5 classes
        fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_probs[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label=f'ROC {classes[i]} (area = {roc_auc:0.2f})')
        
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (Top 5 Classes)')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join('reports', 'figures', 'roc_curve.png'), dpi=300)
    plt.close()
    
    # 3. Precision-Recall Curve (Top 5)
    print("Generating PR Curve...")
    plt.figure(figsize=(10, 8))
    for i in range(5):
        precision, recall, _ = precision_recall_curve(y_test_bin[:, i], y_probs[:, i])
        plt.plot(recall, precision, lw=2, label=f'PR {classes[i]}')
        
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve (Top 5 Classes)')
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(os.path.join('reports', 'figures', 'pr_curve.png'), dpi=300)
    plt.close()

if __name__ == "__main__":
    generate_figures()
