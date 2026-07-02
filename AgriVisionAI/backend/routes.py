from fastapi import APIRouter, HTTPException
from backend.validator import CropPredictionInput, CropPredictionResponse, FertilizerInput, FertilizerResponse
from backend.recommendation import predict_crop
from backend.fertilizer import recommend_fertilizer
from backend.database import save_prediction, get_history

router = APIRouter()

@router.get("/health")
def health_check():
    """Simple health check endpoint to verify backend is running."""
    return {"status": "Backend Running"}

@router.post("/predict", response_model=CropPredictionResponse)
def predict(input_data: CropPredictionInput):
    """Predict the best crop based on soil and weather parameters."""
    try:
        # Perform prediction
        result = predict_crop(input_data)
        
        # Save to history
        save_prediction(input_data.model_dump(), result.recommended_crop)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fertilizer", response_model=FertilizerResponse)
def fertilizer(input_data: FertilizerInput):
    """Get a fertilizer recommendation for a given crop."""
    try:
        result = recommend_fertilizer(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def history():
    """Retrieve prediction history."""
    try:
        records = get_history()
        return {"history": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
