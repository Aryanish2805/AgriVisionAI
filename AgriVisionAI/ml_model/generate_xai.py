import os
import joblib
import pandas as pd
import shap
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

def ensure_dirs():
    os.makedirs(os.path.join('reports', 'figures'), exist_ok=True)

def load_data_and_model():
    data_path = os.path.join('ml_model', 'dataset', 'Crop_recommendation.csv')
    try:
        data = pd.read_csv(data_path)
    except FileNotFoundError:
        data = pd.read_csv(os.path.join('..', 'ml_model', 'dataset', 'Crop_recommendation.csv'))
    
    # We load traditional model or MLP for SHAP depending on what we want to explain
    # We will explain the MLP model here for the DL paper focus.
    
    X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = data['label']
    
    model_path = os.path.join('models', 'deep_learning', 'mlp_model.pkl')
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(os.path.join('models', 'deep_learning', 'dl_scaler.pkl'))
    except FileNotFoundError:
        print("MLP Model not found. Did you run train_dl_models.py?")
        return None, None, None, None
        
    # Scale all X for SHAP explaining
    X_scaled = scaler.transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns)
    
    return model, X_scaled_df, y, X.columns

def generate_shap_plots():
    ensure_dirs()
    model, X, y, columns = load_data_and_model()
    if model is None:
        return
        
    print("Initializing SHAP Explainer...")
    # Because MLP is a deep learning model but used from sklearn, KernelExplainer is standard.
    # To save time, use a subset of data for background
    background = shap.sample(X, 100)
    
    # explainer = shap.KernelExplainer(model.predict_proba, background)
    # KernelExplainer can be slow. For MLP, we can just use it on a small sample of 50.
    sample = X.iloc[:50]
    explainer = shap.KernelExplainer(model.predict_proba, background)
    
    print("Calculating SHAP values (this may take a moment)...")
    shap_values = explainer.shap_values(sample)
    
    print("Generating SHAP Summary Plot...")
    # For multiclass, shap_values is a list. Summary plot on a single class (e.g. 0) or bar plot for all
    plt.figure()
    shap.summary_plot(shap_values, sample, plot_type="bar", show=False)
    plt.tight_layout()
    plt.savefig(os.path.join('reports', 'figures', 'shap_summary.png'), dpi=300)
    plt.close()

    print("Generating Feature Importance Plot (overall)...")
    # Actually shap_summary with bar plot is feature importance. Let's do a standard mean(abs(shap))
    plt.figure()
    if isinstance(shap_values, list):
        # average over classes
        mean_abs_shap = np.mean([np.abs(sv).mean(0) for sv in shap_values], axis=0)
    else:
        mean_abs_shap = np.abs(shap_values).mean(0)
    
    pd.Series(mean_abs_shap, index=columns).sort_values(ascending=True).plot.barh()
    plt.title('Feature Importance via SHAP')
    plt.tight_layout()
    plt.savefig(os.path.join('reports', 'figures', 'feature_importance.png'), dpi=300)
    plt.close()
    
    print("Generating Waterfall Plot for first prediction...")
    
    plt.figure()
    try:
        if isinstance(shap_values, list):
            # We need an Explanation object for waterfall
            sv_class0 = shap_values[0]
            base_val = explainer.expected_value[0]
            exp = shap.Explanation(values=sv_class0[0], base_values=base_val, data=sample.iloc[0,:], feature_names=columns)
        else:
            exp = shap.Explanation(values=shap_values[0,:], base_values=explainer.expected_value, data=sample.iloc[0,:], feature_names=columns)
            
        shap.waterfall_plot(exp, show=False)
        plt.tight_layout()
        plt.savefig(os.path.join('reports', 'figures', 'waterfall_plot.png'), dpi=300)
    except Exception as e:
        print("Waterfall plot dimensional skip:", e)
    finally:
        plt.close()

    print("SHAP figures generated successfully in reports/figures/")

if __name__ == "__main__":
    generate_shap_plots()
