from fastapi import APIRouter, HTTPException
from backend.validator import CropPredictionInput, CropPredictionResponse, FertilizerInput, FertilizerResponse, AgenticInput, AgenticResponse
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.controller import AgenticController

agent_controller = AgenticController()
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

@router.post("/agent/recommend", response_model=AgenticResponse)
def agent_recommend(input_data: AgenticInput):
    """Invoke the full Agentic framework for comprehensive agricultural recommendation."""
    try:
        result = agent_controller.process_request(input_data.farmer_query, input_data.sensor_data)
        
        # Save to history can be added here
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
