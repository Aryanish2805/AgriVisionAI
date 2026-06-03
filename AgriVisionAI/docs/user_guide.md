# AgriVisionAI User Guide

## Project purpose

This application recommends crops to grow based on soil and weather conditions using a machine learning model.

## Workflow

1. Place or upload a training dataset into `dataset/crop_recommendation.csv`.
2. Train the model with:

```bash
python ml_model/train.py
```

3. Evaluate the model with:

```bash
python ml_model/evaluate.py
```

4. View the evaluation results in `reports/model_evaluation.txt`.
5. Run the web app:

```bash
streamlit run frontend/app.py
```

## Training dataset upload

- Use the frontend upload tab to add or replace the training dataset.
- Uploaded file must be a CSV with columns: `soil_type`, `rainfall_mm`, `temperature_c`, `humidity_pct`, `crop`.

## Recommended commands

```bash
python -m pip install -r requirements.txt
python ml_model/train.py
python ml_model/evaluate.py
streamlit run frontend/app.py
```
