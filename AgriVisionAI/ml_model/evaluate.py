from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from ml_model.data_loader import load_crop_dataset

MODEL_PATH = Path(__file__).resolve().parent / "crop_model.joblib"
REPORT_PATH = Path(__file__).resolve().parent.parent / "reports" / "model_evaluation.txt"


def evaluate_model() -> tuple[str, dict]:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    model = joblib.load(MODEL_PATH)
    df, schema = load_crop_dataset()
    if schema == "kaggle":
        feature_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
        target_col = "label"
    elif schema == "simple":
        feature_cols = ["soil_type", "rainfall_mm", "temperature_c", "humidity_pct"]
        target_col = "crop"
    else:
        raise ValueError("Unknown dataset schema for evaluation.")

    # preserve original column names (casing)
    df_columns = {c.lower(): c for c in df.columns}
    X = df[[df_columns.get(c.lower(), c) for c in feature_cols]]
    y_true = df[df_columns.get(target_col.lower(), target_col)]

    y_pred = model.predict(X)
    accuracy = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, output_dict=True)
    report_text = classification_report(y_true, y_pred)
    labels = sorted(y_true.unique())
    matrix = confusion_matrix(y_true, y_pred, labels=labels)

    lines = [
        "AI-Based Crop Recommendation Model Evaluation",
        "==========================================",
        f"Model path: {MODEL_PATH}",
        f"Dataset path: {Path(__file__).resolve().parents[1] / 'dataset' / 'crop_recommendation.csv'}",
        "",
        f"Accuracy: {accuracy:.4f}",
        "",
        "Classification Report:",
        report_text,
        "Confusion Matrix:",
        str(matrix),
    ]

    metrics = {
        "accuracy": accuracy,
        "classification_report": report,
        "confusion_matrix": matrix,
        "labels": labels,
    }
    return "\n".join(lines), metrics


def save_report(content: str) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(content, encoding="utf-8")


def main() -> None:
    report, _ = evaluate_model()
    save_report(report)
    print(report)
    print()
    print(f"Saved evaluation report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
