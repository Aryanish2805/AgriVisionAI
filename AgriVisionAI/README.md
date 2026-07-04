# AgriVisionAI: AI-Based Crop Recommendation System

## Overview
AgriVisionAI is a Machine Learning based intelligent agriculture assistant that helps farmers make data-driven decisions to increase yield and reduce risk. This repository is the single source of truth for the entire research project, containing the frontend, backend, machine learning models, datasets, and documentation.

## Problem Statement
Farmers need data-driven crop selection guidance to increase yield and reduce risk.

## Features
- **Crop Recommendation**: Predicts the most suitable crop based on Nitrogen, Phosphorus, Potassium, Temperature, Humidity, Soil pH, and Rainfall.
- **Fertilizer Recommendation**: Suggests suitable fertilizer using soil nutrients, soil properties, crop type, weather conditions, and previous farming data.
- **Crop Price Prediction**: Predicts crop market prices using location data, commodity information, and market history.

## Folder Structure
```
AgriVisionAI/
├── frontend/           # Streamlit User Interface
├── backend/            # Backend APIs
├── ml/                 # Machine Learning Module
│   ├── datasets/
│   ├── models/
│   ├── crops_training/
│   ├── fertilizer_training/
│   ├── price_training/
│   ├── app.py          # ML specific app
│   └── requirements.txt
├── docs/               # Documentation
├── dataset/            # Global Datasets
├── requirements.txt    # Main Requirements
└── README.md           # This File
```

## Tech Stack
- **Frontend**: Streamlit
- **Backend**: Python
- **Machine Learning**: Pandas, NumPy, Scikit-Learn, XGBoost, CatBoost, Joblib

## Machine Learning Pipeline & Dataset
- The project integrates multiple models (Decision Tree, Random Forest, XGBoost, CatBoost, etc.).
- Datasets include `dataset/crop_recommendation.csv` and other datasets under `ml/datasets/`.
- Training pipelines and notebooks are available in the `ml/` directory.

## Installation

1. Install dependencies for the main project:
```bash
python -m pip install -r requirements.txt
```

2. Install dependencies for the ML module:
```bash
cd ml
pip install -r requirements.txt
```

## Usage

1. Train the models (if required):
```bash
python ml_model/train.py
```

2. Run the main Streamlit app:
```bash
streamlit run frontend/app.py
```

3. Run the ML-specific Streamlit app:
```bash
cd ml
streamlit run app.py
```

## Results & Screenshots
- The system successfully integrates Crop Recommendation, Fertilizer Recommendation, and Crop Price Prediction.
- Model evaluation includes accuracy metrics and confusion matrix charts available via the Streamlit dashboard.

## Future Scope
- Add real-time weather API integration.
- Add farmer location-based recommendation.
- Deploy the application on a cloud platform.
- Improve model performance using larger datasets.

## Team Members
- Aryanish
- Surya
- Adarsh

## License
MIT License
