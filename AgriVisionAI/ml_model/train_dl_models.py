import os
import time
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def ensure_dirs():
    os.makedirs('models/deep_learning', exist_ok=True)
    os.makedirs('reports', exist_ok=True)

def load_and_preprocess_data():
    # Load dataset
    data_path = os.path.join('ml_model', 'dataset', 'Crop_recommendation.csv')
    try:
        data = pd.read_csv(data_path)
    except FileNotFoundError:
        data = pd.read_csv(os.path.join('..', 'ml_model', 'dataset', 'Crop_recommendation.csv'))
        
    X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = data['label']
    
    # Label encoding for target
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save scaler and label encoder to use during inference
    joblib.dump(scaler, os.path.join('models', 'deep_learning', 'dl_scaler.pkl'))
    joblib.dump(le, os.path.join('models', 'deep_learning', 'dl_label_encoder.pkl'))
    
    return X_train_scaled, X_test_scaled, y_train, y_test, X.columns

def train_mlp(X_train, y_train, X_test, y_test):
    print("Training MLP (Deep Neural Network)...")
    start_time = time.time()
    
    model = MLPClassifier(hidden_layer_sizes=(128, 64, 32), max_iter=500, random_state=42)
    model.fit(X_train, y_train)
    
    train_time = time.time() - start_time
    
    # Inference
    start_time = time.time()
    y_pred = model.predict(X_test)
    inference_time = time.time() - start_time
    
    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
    
    # Save the model
    joblib.dump(model, os.path.join('models', 'deep_learning', 'mlp_model.pkl'))
    
    return {
        'Model': 'MLP (DNN)',
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1-score': f1,
        'Training Time (s)': train_time,
        'Inference Time (s)': inference_time
    }

# TabNet requires torch and pytorch-tabnet
def train_tabnet(X_train, y_train, X_test, y_test):
    print("Training TabNet...")
    from pytorch_tabnet.tab_model import TabNetClassifier
    import torch
    
    start_time = time.time()
    # TabNet uses fit with eval sets
    clf = TabNetClassifier(optimizer_fn=torch.optim.Adam,
                           optimizer_params=dict(lr=2e-2),
                           scheduler_params={"step_size":50, "gamma":0.9},
                           scheduler_fn=torch.optim.lr_scheduler.StepLR,
                           mask_type='entmax')
                           
    clf.fit(
        X_train=X_train, y_train=y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        eval_name=['train', 'valid'],
        eval_metric=['accuracy'],
        max_epochs=100, patience=20,
        batch_size=256, virtual_batch_size=128,
        num_workers=0, drop_last=False
    )
    
    train_time = time.time() - start_time
    
    # Inference
    start_time = time.time()
    y_pred = clf.predict(X_test)
    inference_time = time.time() - start_time
    
    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
    
    clf.save_model(os.path.join('models', 'deep_learning', 'tabnet_model'))
    
    return {
        'Model': 'TabNet',
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1-score': f1,
        'Training Time (s)': train_time,
        'Inference Time (s)': inference_time
    }

def train_ft_transformer(X_train, y_train, X_test, y_test):
    print("Training FT-Transformer...")
    import torch
    import rtdl
    import torch.nn as nn
    import torch.optim as optim
    
    # We will implement a straightforward FT-Transformer architecture with PyTorch
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    X_tr_t = torch.tensor(X_train, dtype=torch.float32).to(device)
    y_tr_t = torch.tensor(y_train, dtype=torch.long).to(device)
    X_te_t = torch.tensor(X_test, dtype=torch.float32).to(device)
    
    n_features = X_train.shape[1]
    n_classes = len(np.unique(y_train))
    
    # Rtdl FT-Transformer
    model = rtdl.FTTransformer.make_baseline(
        n_num_features=n_features,
        cat_cardinalities=None,
        d_token=192,
        n_blocks=3,
        attention_dropout=0.1,
        ffn_dropout=0.1,
        d_out=n_classes,
    ).to(device)
    
    optimizer = optim.AdamW(model.parameters(), lr=1e-4)
    criterion = nn.CrossEntropyLoss()
    
    dataset = torch.utils.data.TensorDataset(X_tr_t, y_tr_t)
    loader = torch.utils.data.DataLoader(dataset, batch_size=256, shuffle=True)
    
    start_time = time.time()
    model.train()
    for epoch in range(50):
        for bx, by in loader:
            optimizer.zero_grad()
            pred = model(bx, None)
            loss = criterion(pred, by)
            loss.backward()
            optimizer.step()
    
    train_time = time.time() - start_time
    
    # Inference
    start_time = time.time()
    model.eval()
    with torch.no_grad():
        preds = model(X_te_t, None).argmax(dim=1).cpu().numpy()
    inference_time = time.time() - start_time
    
    acc = accuracy_score(y_test, preds)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, preds, average='weighted')
    
    torch.save(model.state_dict(), os.path.join('models', 'deep_learning', 'ft_transformer.pt'))
    
    return {
        'Model': 'FT-Transformer',
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1-score': f1,
        'Training Time (s)': train_time,
        'Inference Time (s)': inference_time
    }


if __name__ == '__main__':
    ensure_dirs()
    X_tr, X_te, y_tr, y_te, features = load_and_preprocess_data()
    
    results = []
    
    # Train Modern DL architectures
    res_mlp = train_mlp(X_tr, y_tr, X_te, y_te)
    results.append(res_mlp)
    
    try:
        res_tabnet = train_tabnet(X_tr, y_tr, X_te, y_te)
        results.append(res_tabnet)
    except Exception as e:
        print(f"TabNet failed: {e}")
        
    try:
        res_ft = train_ft_transformer(X_tr, y_tr, X_te, y_te)
        results.append(res_ft)
    except Exception as e:
        print(f"FT-Transformer failed: {e}")
        
    df = pd.DataFrame(results)
    df.to_csv(os.path.join('reports', 'model_comparison.csv'), index=False)
    print("Training complete. Results saved to reports/model_comparison.csv")
