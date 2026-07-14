import joblib
import pandas as pd
import os
import time

class CropAgent:
    """Agent responsible for Crop Recommendation Models."""
    def __init__(self):
        self.name = "Crop Agent"
        # Load the best DL model (MLP for now, fallback to RF)
        self.dl_model_path = os.path.join('models', 'deep_learning', 'mlp_model.pkl')
        self.ml_model_path = os.path.join('ml_model', 'crop_model.pkl')
        self.scaler_path = os.path.join('models', 'deep_learning', 'dl_scaler.pkl')
        self.le_path = os.path.join('models', 'deep_learning', 'dl_label_encoder.pkl')
        
    def recommend(self, sensor_data: dict, weather_data: dict) -> dict:
        print(f"[{self.name}] Executing crop model prediction...")
        
        # Combine sensor and weather
        features = {
            'N': sensor_data.get('N', 0),
            'P': sensor_data.get('P', 0),
            'K': sensor_data.get('K', 0),
            'temperature': weather_data.get('temperature_c', 25.0),
            'humidity': weather_data.get('humidity_pct', 60.0),
            'ph': sensor_data.get('ph', 6.5),
            'rainfall': weather_data.get('rainfall_mm', 100.0)
        }
        
        df = pd.DataFrame([features])
        
        start_time = time.time()
        # Try Deep Learning Model First
        if os.path.exists(self.dl_model_path):
            try:
                model = joblib.load(self.dl_model_path)
                scaler = joblib.load(self.scaler_path)
                le = joblib.load(self.le_path)
                
                df_scaled = scaler.transform(df)
                pred_encoded = model.predict(df_scaled)[0]
                prediction = le.inverse_transform([pred_encoded])[0]
                model_used = "Deep Learning (MLP)"
            except Exception as e:
                print(f"[{self.name}] DL Model Error: {e}, falling back to ML")
                prediction, model_used = self._fallback_ml(df)
        else:
            prediction, model_used = self._fallback_ml(df)
            
        inf_time = time.time() - start_time
        return {
            "recommended_crop": prediction,
            "model_used": model_used,
            "inference_time_s": inf_time
        }
        
    def _fallback_ml(self, df):
        if os.path.exists(self.ml_model_path):
            model = joblib.load(self.ml_model_path)
            prediction = model.predict(df)[0]
            return prediction, "Traditional ML (Random Forest)"
        return "Unknown", "None"
