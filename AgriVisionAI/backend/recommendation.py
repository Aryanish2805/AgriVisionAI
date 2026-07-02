import pandas as pd
from backend.model_loader import get_model
from backend.validator import CropPredictionInput, CropPredictionResponse
import sys
from pathlib import Path

# Add project root to sys.path to import ml_model.crop_recommender rule fallback
sys.path.append(str(Path(__file__).resolve().parents[2]))
from ml_model.crop_recommender import recommend_crop_rule


def predict_crop(input_data: CropPredictionInput) -> CropPredictionResponse:
    """Predict crop from input data using ML model or fallback rule."""
    model = get_model()
    
    # Feature dictionary
    record = {
        "N": input_data.N,
        "P": input_data.P,
        "K": input_data.K,
        "temperature": input_data.temperature,
        "humidity": input_data.humidity,
        "ph": input_data.ph,
        "rainfall": input_data.rainfall,
    }

    if model is not None:
        try:
            df = pd.DataFrame([record])
            
            # If probabilistic prediction is available
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(df)
                classes = list(model.classes_)
                prob_row = probs[0]
                pairs = list(zip(classes, prob_row))
                pairs_sorted = sorted(pairs, key=lambda x: x[1], reverse=True)[:5]
                
                top_crop = pairs_sorted[0][0]
                top_prob = pairs_sorted[0][1]
                
                candidates = [{"crop": name, "probability": prob} for name, prob in pairs_sorted]
                
                return CropPredictionResponse(
                    recommended_crop=top_crop,
                    confidence=top_prob,
                    candidates=candidates
                )
            else:
                pred = model.predict(df)[0]
                return CropPredictionResponse(recommended_crop=pred)
                
        except Exception as e:
            print(f"[recommendation] ML Prediction error: {e}")
            # Fall through to rules

    # Fallback rule-based recommendation
    print("[recommendation] Using rule-based fallback")
    
    # Simple rule based fallback just needs soil type, rainfall and temperature
    # but since soil type isn't in kaggle schema, we make a default assumption
    # or just return a generic suggestion.
    rule_msg = recommend_crop_rule("Loamy", input_data.rainfall, input_data.temperature)
    suggestion = rule_msg.replace("Recommended crop (rules): ", "")
    
    if suggestion.startswith("No strong"):
        suggestion = "Unknown (Check conditions)"
        
    return CropPredictionResponse(
        recommended_crop=suggestion,
        confidence=None,
        candidates=[{"crop": suggestion, "probability": None}]
    )
