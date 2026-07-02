# AgriVision AI Backend

This is the FastAPI backend for the AgriVision AI project. It serves as the bridge between the Streamlit frontend and the Machine Learning model.

## Features
- **Health Check API**: `/health` to verify status.
- **Crop Prediction API**: `/predict` to predict crops based on NPK, temperature, humidity, pH, and rainfall.
- **Fertilizer Recommendation API**: `/fertilizer` for basic fertilizer suggestions.
- **Input Validation**: Uses Pydantic to ensure all data is valid before hitting the ML model.
- **Prediction History**: Stores past predictions in a local SQLite database (`data/history.db`).

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the backend:
   ```bash
   uvicorn backend.app:app --reload
   ```

## API Docs
Once running, visit `http://localhost:8000/docs` for the interactive Swagger UI.

## Testing with Curl

### Health Check
```bash
curl http://localhost:8000/health
```

### Predict
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d "{\"N\":90, \"P\":42, \"K\":43, \"temperature\":20.8, \"humidity\":82, \"ph\":6.5, \"rainfall\":202}"
```

### Fertilizer
```bash
curl -X POST http://localhost:8000/fertilizer \
  -H "Content-Type: application/json" \
  -d "{\"crop\":\"Rice\"}"
```
