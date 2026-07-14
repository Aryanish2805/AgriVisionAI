import torch
import shap
import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt

def get_shap_explainer(model, X_train_scaled, feature_names, model_type='classification'):
    """
    Creates and returns a SHAP DeepExplainer for the given PyTorch model.
    """
    model.eval()
    # We use a background dataset for DeepExplainer (e.g., 100 random samples)
    if len(X_train_scaled) > 100:
        background_indices = np.random.choice(len(X_train_scaled), 100, replace=False)
        background = X_train_scaled[background_indices]
    else:
        background = X_train_scaled
        
    background_tensor = torch.tensor(background, dtype=torch.float32)
    
    explainer = shap.DeepExplainer(model, background_tensor)
    return explainer

def generate_shap_plots(model, X_test_scaled, feature_names, save_dir='reports/xai', prefix='crop'):
    """
    Generates and saves SHAP summary plots for interpretability.
    """
    os.makedirs(save_dir, exist_ok=True)
    
    explainer = get_shap_explainer(model, X_test_scaled, feature_names)
    
    # Take a sample for generating plots to save computation
    sample_size = min(len(X_test_scaled), 50)
    sample_indices = np.random.choice(len(X_test_scaled), sample_size, replace=False)
    test_tensor = torch.tensor(X_test_scaled[sample_indices], dtype=torch.float32)
    
    shap_values = explainer.shap_values(test_tensor)
    
    # For PyTorch multi-class, shap_values is a list of arrays (one for each class).
    # We can plot the summary plot for the first class or the mean absolute SHAP values across all classes.
    plt.figure(figsize=(10, 6))
    
    if isinstance(shap_values, list):
        # Multi-class classification
        shap.summary_plot(shap_values, test_tensor.numpy(), feature_names=feature_names, show=False)
    else:
        # Regression or binary classification
        shap.summary_plot(shap_values, test_tensor.numpy(), feature_names=feature_names, show=False)
        
    plt.tight_layout()
    plot_path = os.path.join(save_dir, f'{prefix}_shap_summary.png')
    plt.savefig(plot_path)
    plt.close()
    
    print(f"SHAP summary plot saved to {plot_path}")
    return plot_path

def explain_single_prediction(model, input_features, feature_names, background_data):
    """
    Returns SHAP feature importances for a single prediction to be consumed by the Reasoning Agent.
    """
    explainer = get_shap_explainer(model, background_data, feature_names)
    input_tensor = torch.tensor(input_features, dtype=torch.float32)
    
    shap_values = explainer.shap_values(input_tensor)
    
    # Return top 3 most important features for this specific prediction
    # If multi-class, take the sum across classes or the specific predicted class
    if isinstance(shap_values, list):
        # Taking mean absolute SHAP across classes for simplicity
        mean_shap = np.mean(np.abs(shap_values), axis=0)[0]
    else:
        mean_shap = np.abs(shap_values)[0]
        
    importance_dict = {feature_names[i]: float(mean_shap[i]) for i in range(len(feature_names))}
    sorted_importance = dict(sorted(importance_dict.items(), key=lambda item: item[1], reverse=True))
    
    return sorted_importance
