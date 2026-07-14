"""
5-Fold Cross-Validation with Statistical Significance Testing
Generates mean ± std for all models and runs paired Wilcoxon signed-rank tests.
"""
import os
import pandas as pd
import numpy as np
import joblib
import time
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from scipy.stats import wilcoxon

def load_data():
    data_path = os.path.join('ml_model', 'dataset', 'Crop_recommendation.csv')
    try:
        data = pd.read_csv(data_path)
    except FileNotFoundError:
        data = pd.read_csv(os.path.join('..', 'ml_model', 'dataset', 'Crop_recommendation.csv'))
    X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].values
    y = data['label'].values
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    return X, y_encoded, le

def run_cross_validation():
    os.makedirs('reports', exist_ok=True)
    X, y, le = load_data()
    
    models = {
        'Random Forest': lambda: RandomForestClassifier(n_estimators=100, random_state=42),
        'Decision Tree': lambda: DecisionTreeClassifier(random_state=42),
        'Extra Trees': lambda: ExtraTreesClassifier(n_estimators=100, random_state=42),
        'MLP (DNN)': lambda: MLPClassifier(hidden_layer_sizes=(128, 64, 32), max_iter=500, random_state=42),
    }
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # Store per-fold results
    all_fold_results = {name: {'accuracy': [], 'precision': [], 'recall': [], 'f1': [], 'train_time': [], 'infer_time': []} 
                        for name in models}
    
    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        print(f"\n=== Fold {fold_idx + 1}/5 ===")
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        for name, model_fn in models.items():
            print(f"  Training {name}...")
            model = model_fn()
            
            # Use scaled data for MLP, raw for tree-based
            if 'MLP' in name:
                Xtr, Xte = X_train_scaled, X_test_scaled
            else:
                Xtr, Xte = X_train, X_test
            
            start = time.time()
            model.fit(Xtr, y_train)
            train_time = time.time() - start
            
            start = time.time()
            y_pred = model.predict(Xte)
            infer_time = time.time() - start
            
            acc = accuracy_score(y_test, y_pred)
            prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
            
            all_fold_results[name]['accuracy'].append(acc)
            all_fold_results[name]['precision'].append(prec)
            all_fold_results[name]['recall'].append(rec)
            all_fold_results[name]['f1'].append(f1)
            all_fold_results[name]['train_time'].append(train_time)
            all_fold_results[name]['infer_time'].append(infer_time)
    
    # Generate summary table
    print("\n" + "="*80)
    print("5-FOLD CROSS-VALIDATION RESULTS (Mean ± Std)")
    print("="*80)
    
    summary_rows = []
    for name in models:
        r = all_fold_results[name]
        row = {
            'Model': name,
            'Accuracy (Mean)': np.mean(r['accuracy']),
            'Accuracy (Std)': np.std(r['accuracy']),
            'Precision (Mean)': np.mean(r['precision']),
            'F1 (Mean)': np.mean(r['f1']),
            'F1 (Std)': np.std(r['f1']),
            'Train Time (Mean s)': np.mean(r['train_time']),
            'Infer Time (Mean ms)': np.mean(r['infer_time']) * 1000,
        }
        summary_rows.append(row)
        print(f"{name:20s}  Acc: {row['Accuracy (Mean)']:.4f} ± {row['Accuracy (Std)']:.4f}  "
              f"F1: {row['F1 (Mean)']:.4f} ± {row['F1 (Std)']:.4f}")
    
    df = pd.DataFrame(summary_rows)
    df.to_csv(os.path.join('reports', 'cross_validation_results.csv'), index=False)
    
    # Statistical Significance Tests (Wilcoxon signed-rank)
    print("\n" + "="*80)
    print("STATISTICAL SIGNIFICANCE TESTS (Wilcoxon Signed-Rank)")
    print("="*80)
    
    model_names = list(models.keys())
    sig_rows = []
    for i in range(len(model_names)):
        for j in range(i+1, len(model_names)):
            a_acc = all_fold_results[model_names[i]]['accuracy']
            b_acc = all_fold_results[model_names[j]]['accuracy']
            try:
                stat, p_val = wilcoxon(a_acc, b_acc)
                sig = "Yes (p < 0.05)" if p_val < 0.05 else "No (p >= 0.05)"
            except ValueError:
                # All differences are zero
                stat, p_val, sig = 0, 1.0, "No (identical)"
            
            sig_rows.append({
                'Model A': model_names[i],
                'Model B': model_names[j],
                'W-statistic': stat,
                'p-value': round(p_val, 6),
                'Significant': sig
            })
            print(f"  {model_names[i]:20s} vs {model_names[j]:20s}  p={p_val:.6f}  {sig}")
    
    sig_df = pd.DataFrame(sig_rows)
    sig_df.to_csv(os.path.join('reports', 'statistical_tests.csv'), index=False)
    
    print("\nResults saved to reports/cross_validation_results.csv")
    print("Significance tests saved to reports/statistical_tests.csv")

if __name__ == '__main__':
    run_cross_validation()
