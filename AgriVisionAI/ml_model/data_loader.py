from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd

DEFAULT_DATASET_PATH = Path(__file__).resolve().parent.parent / "dataset" / "crop_recommendation.csv"


def load_crop_dataset(path: str | Path | None = None) -> Tuple[pd.DataFrame, str]:
    """Load a dataset and return (DataFrame, schema_type).

    schema_type is one of: 'kaggle' (N,P,K,...,label), 'simple' (soil_type,...,crop), or 'unknown'.
    """
    p = Path(path) if path is not None else DEFAULT_DATASET_PATH
    if not p.exists():
        raise FileNotFoundError(f"Training dataset not found. Create or place a file at: {p}")

    df = pd.read_csv(p)
    cols = {c.strip().lower() for c in df.columns}

    kaggle_cols = {"n", "p", "k", "temperature", "humidity", "ph", "rainfall", "label"}
    simple_cols = {"soil_type", "rainfall_mm", "temperature_c", "humidity_pct", "crop"}

    if kaggle_cols.issubset(cols):
        schema = "kaggle"
    elif simple_cols.issubset(cols):
        schema = "simple"
    else:
        schema = "unknown"

    return df, schema
