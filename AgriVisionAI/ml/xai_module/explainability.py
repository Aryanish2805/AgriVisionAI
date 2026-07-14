import torch
import shap
import matplotlib.pyplot as plt
import os
import sys
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dl_models.dataset import CropDataset
from dl_models.cnn_attention import CNNAttentionModel

def explain_model():
    # Load dataset
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "dataset", "Crop_recommendation_kaggle.csv")
    dataset = CropDataset(dataset_path, is_train=True)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load model
    model = CNNAttentionModel(num_features=dataset.get_num_features(), num_classes=dataset.get_num_classes())
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dl_models", "saved_models", "cnn_attention.pth")
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    
    # Sample background data for SHAP
    # SHAP for deep learning usually requires a background dataset
    background_size = 100
    test_size = 50
    
    # Get random samples for background and test
    indices = np.random.permutation(len(dataset))
    
    bg_inputs = []
    for i in indices[:background_size]:
        x, _ = dataset[i]
        bg_inputs.append(x.unsqueeze(0))
    background = torch.cat(bg_inputs, dim=0).to(device)
    
    test_inputs = []
    for i in indices[background_size:background_size+test_size]:
        x, _ = dataset[i]
        test_inputs.append(x.unsqueeze(0))
    test_data = torch.cat(test_inputs, dim=0).to(device)

    # SHAP DeepExplainer
    explainer = shap.DeepExplainer(model, background)
    shap_values = explainer.shap_values(test_data, check_additivity=False)
    
    # Feature names
    feature_names = ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Temperature', 'Humidity', 'pH', 'Rainfall']
    
    # If shap_values is a list of arrays (one for each class)
    # We take the mean absolute SHAP value across all classes and samples for a global summary
    if isinstance(shap_values, list):
        shap_values = np.array(shap_values)
    mean_shap = np.mean(np.abs(shap_values), axis=tuple(range(len(shap_values.shape)-1)))

    # Plot
    plt.figure(figsize=(10, 6))
    plt.barh(feature_names, mean_shap, color='skyblue')
    plt.xlabel('Mean Absolute SHAP Value (Impact on Model Output)')
    plt.title('Feature Importance for Crop Recommendation (CNN + Attention)')
    plt.tight_layout()
    
    os.makedirs('reports/figures', exist_ok=True)
    plt.savefig('reports/figures/shap_feature_importance.png')
    print("SHAP explanation plot saved to reports/figures/shap_feature_importance.png")

if __name__ == "__main__":
    explain_model()
