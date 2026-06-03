# AgriVisionAI

## Project
AI-Based Crop Recommendation System Using Machine Learning

## Status
- Project refocused for crop recommendation
- Created model logic: `ml_model/crop_recommender.py`
- Created training pipeline: `ml_model/train.py`
- Created sample dataset: `dataset/crop_recommendation.csv`
- Created recommendation entrypoint: `recommend.py`
- Created Streamlit UI: `frontend/app.py`
- The dataset directory still contains the extracted PlantVillage dataset, but the crop recommender uses a separate `crop_recommendation.csv` sample dataset.

## How to use
1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Train the model:

```bash
python ml_model/train.py
```

3. Evaluate the trained model:

```bash
python ml_model/evaluate.py
```

4. Run the command-line example:

```bash
python recommend.py
```

5. Run the Streamlit app:

```bash
streamlit run frontend/app.py
```

## Dataset upload
- The Streamlit app includes an upload tab for replacing the training CSV dataset.
- Uploaded dataset must use the columns: `soil_type`, `rainfall_mm`, `temperature_c`, `humidity_pct`, `crop`.
- The app saves uploaded data to `dataset/crop_recommendation.csv`.
## Model evaluation dashboard
- The Streamlit app now includes a `Model Evaluation` tab.
- Click `Run Model Evaluation` to compute metrics and save a report to `reports/model_evaluation.txt`.
- If the report exists, it will be displayed in the dashboard.
- The app also displays accuracy and a confusion matrix chart after evaluation.
## Notes
- `ml_model/train.py` trains a simple decision tree model using the current CSV dataset.
- `ml_model/evaluate.py` writes a performance report to `reports/model_evaluation.txt`.
- `frontend/app.py` uses the trained model automatically if `ml_model/crop_model.joblib` exists.
- You can replace `dataset/crop_recommendation.csv` with a larger crop recommendation dataset when ready.

## Teacher slides
- Slide 1: Project Name — AI-Based Crop Recommendation System Using Machine Learning
- Slide 2: Problem — Farmers need data-driven crop selection guidance to increase yield and reduce risk.
