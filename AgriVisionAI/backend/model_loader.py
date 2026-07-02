"""Load the trained ML model once at startup.

Searches for model files in this order:
1. backend/models/best_model.pkl
2. backend/models/crop_model.joblib
3. ml_model/crop_model.joblib  (existing project model)
"""

from pathlib import Path
from typing import Optional

import joblib

# Directories to search
_BACKEND_MODELS_DIR = Path(__file__).resolve().parent / "models"
_PROJECT_ML_DIR = Path(__file__).resolve().parent.parent / "ml_model"

# Module-level cache — the model is loaded once and reused
_model = None
_model_loaded = False


def _find_model_path() -> Optional[Path]:
    """Return the first valid model file path found, or None."""
    candidates = [
        _BACKEND_MODELS_DIR / "best_model.pkl",
        _BACKEND_MODELS_DIR / "crop_model.joblib",
        _PROJECT_ML_DIR / "crop_model.joblib",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def load_model():
    """Load the ML model from disk. Called once at server startup."""
    global _model, _model_loaded

    path = _find_model_path()
    if path is None:
        print("[model_loader] WARNING: No model file found. Prediction will use fallback rules.")
        _model = None
        _model_loaded = True
        return

    try:
        _model = joblib.load(path)
        _model_loaded = True
        print(f"[model_loader] Model loaded successfully from {path}")
    except Exception as exc:
        print(f"[model_loader] ERROR loading model from {path}: {exc}")
        _model = None
        _model_loaded = True


def get_model():
    """Return the cached model instance (may be None if no model found)."""
    if not _model_loaded:
        load_model()
    return _model
