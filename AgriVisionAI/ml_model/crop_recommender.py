from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    import joblib
    import pandas as pd
except ImportError:  # pragma: no cover
    joblib = None  # type: ignore
    pd = None  # type: ignore

SOIL_OPTIONS = [
    "Loamy",
    "Sandy",
    "Clay",
    "Silty",
    "Peaty",
    "Chalky"
]

MODEL_PATH = Path(__file__).resolve().parent / "crop_model.joblib"

CROP_RULES = [
    {
        "name": "Wheat",
        "soils": ["Loamy", "Clay"],
        "min_rainfall": 100,
        "max_rainfall": 250,
        "min_temp": 15,
        "max_temp": 25,
    },
    {
        "name": "Rice",
        "soils": ["Clay", "Silty"],
        "min_rainfall": 200,
        "max_rainfall": 300,
        "min_temp": 20,
        "max_temp": 35,
    },
    {
        "name": "Maize",
        "soils": ["Loamy", "Sandy"],
        "min_rainfall": 50,
        "max_rainfall": 200,
        "min_temp": 18,
        "max_temp": 32,
    },
    {
        "name": "Soybean",
        "soils": ["Loamy", "Silty"],
        "min_rainfall": 50,
        "max_rainfall": 180,
        "min_temp": 15,
        "max_temp": 30,
    },
    {
        "name": "Cotton",
        "soils": ["Sandy", "Loamy"],
        "min_rainfall": 50,
        "max_rainfall": 180,
        "min_temp": 20,
        "max_temp": 35,
    },
]


def load_model():
    if joblib is None:
        return None
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def recommend_crop(
    soil_type: str,
    rainfall_mm: float,
    temperature_c: float,
    humidity_pct: Optional[float] = None,
) -> str:
    model = load_model()
    if model is not None and pd is not None:
        features = pd.DataFrame([
            {
                "soil_type": soil_type,
                "rainfall_mm": rainfall_mm,
                "temperature_c": temperature_c,
                "humidity_pct": humidity_pct if humidity_pct is not None else 0.0,
            }
        ])
        prediction = model.predict(features)[0]
        return f"Recommended crop (ML model): {prediction}"

    return recommend_crop_rule(soil_type, rainfall_mm, temperature_c)


def _extract_rule_input(record: dict) -> tuple[Optional[str], Optional[float], Optional[float]]:
    soil = record.get("soil_type") or record.get("soil")
    rain = record.get("rainfall_mm") or record.get("rainfall")
    temp = record.get("temperature_c") or record.get("temperature")

    try:
        rain_val = float(rain) if rain is not None else None
    except (TypeError, ValueError):
        rain_val = None
    try:
        temp_val = float(temp) if temp is not None else None
    except (TypeError, ValueError):
        temp_val = None

    return soil, rain_val, temp_val


def recommend_from_record(record: dict) -> dict:
    """Attempt recommendation given a dict-like record. Returns a dict with suggestions.

    Returns example:
      {"type": "ml", "suggestions": [("rice", 0.82), ("wheat", 0.10), ...], "message": "..."}
    """
    model = load_model()
    if model is not None and pd is not None:
        df = pd.DataFrame([record])
        try:
            # try probabilistic prediction if available
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(df)
                classes = list(model.classes_)
                prob_row = probs[0]
                pairs = list(zip(classes, prob_row))
                pairs_sorted = sorted(pairs, key=lambda x: x[1], reverse=True)[:5]
                return {"type": "ml", "suggestions": pairs_sorted, "message": "Suggestions (probabilistic)"}
            else:
                pred = model.predict(df)[0]
                return {"type": "ml", "suggestions": [(pred, None)], "message": f"Recommended (model): {pred}"}
        except Exception:
            # fall through to rule-based fallback
            pass

    soil, rain, temp = _extract_rule_input(record)
    if soil and rain is not None and temp is not None:
        rule = recommend_crop_rule(soil, rain, temp)
        suggestion = rule.replace("Recommended crop (rules): ", "")
        return {"type": "rule", "suggestions": [(suggestion, None)], "message": "Rule-based suggestion"}

    if model is None or pd is None:
        return {"type": "none", "suggestions": [], "message": "No ML model available. Upload or train a model and try again."}

    return {"type": "error", "suggestions": [], "message": "Model could not predict for provided record. Check feature schema."}


def recommend_crop_rule(
    soil_type: str,
    rainfall_mm: float,
    temperature_c: float,
) -> str:
    for rule in CROP_RULES:
        if soil_type in rule["soils"]:
            if rule["min_rainfall"] <= rainfall_mm <= rule["max_rainfall"]:
                if rule["min_temp"] <= temperature_c <= rule["max_temp"]:
                    return f"Recommended crop (rules): {rule['name']}"

    return "No strong recommendation available. Consider improving soil, water, or temperature conditions."


def sample_run() -> None:
    print("AI-Based Crop Recommendation System")
    print(recommend_crop("Loamy", 120, 22, 60))


if __name__ == "__main__":
    sample_run()
