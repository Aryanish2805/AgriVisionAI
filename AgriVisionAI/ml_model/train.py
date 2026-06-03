from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from ml_model.data_loader import load_crop_dataset

MODEL_PATH = Path(__file__).resolve().parent / "crop_model.joblib"


def build_pipeline(feature_columns: list[str], categorical: list[str], numeric: list[str]) -> Pipeline:
    transformers = []
    if categorical:
        transformers.append(("cat", OneHotEncoder(handle_unknown="ignore"), categorical))
    if numeric:
        transformers.append(("num", StandardScaler(), numeric))

    transformer = ColumnTransformer(transformers=transformers, remainder="passthrough")

    pipeline = Pipeline(
        steps=[("transform", transformer), ("classifier", DecisionTreeClassifier(random_state=42))]
    )
    return pipeline


def train_model(dataset_path: str | None = None) -> None:
    df, schema = load_crop_dataset(dataset_path)

    if schema == "kaggle":
        feature_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
        target_col = "label"
        categorical = []
        numeric = feature_cols
    elif schema == "simple":
        feature_cols = ["soil_type", "rainfall_mm", "temperature_c", "humidity_pct"]
        target_col = "crop"
        categorical = ["soil_type"]
        numeric = ["rainfall_mm", "temperature_c", "humidity_pct"]
    else:
        raise ValueError("Unknown dataset schema. Provide a supported dataset.")

    # normalize column names to match keys used below
    df_columns = {c.lower(): c for c in df.columns}
    # build X with correct casing
    X = df[[df_columns.get(c.lower(), c) for c in feature_cols]]
    y = df[df_columns.get(target_col.lower(), target_col)]

    pipeline = build_pipeline(feature_cols, categorical, numeric)
    pipeline.fit(X, y)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Trained ML model saved to {MODEL_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", help="Path to dataset CSV to use for training", default=None)
    args = parser.parse_args()
    train_model(args.dataset)
