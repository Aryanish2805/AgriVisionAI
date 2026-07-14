"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional


class CropPredictionInput(BaseModel):
    """Input schema for crop prediction.

    Validates that all agronomic parameters are within physically
    plausible ranges so garbage data never reaches the model.
    """

    N: float = Field(..., ge=0, le=300, description="Nitrogen content in soil (kg/ha)")
    P: float = Field(..., ge=0, le=300, description="Phosphorus content in soil (kg/ha)")
    K: float = Field(..., ge=0, le=300, description="Potassium content in soil (kg/ha)")
    temperature: float = Field(
        ..., ge=-10, le=60, description="Average temperature in °C"
    )
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity in %")
    ph: float = Field(..., ge=0, le=14, description="Soil pH value")
    rainfall: float = Field(..., ge=0, le=500, description="Rainfall in mm")

    model_config = {"json_schema_extra": {
        "examples": [
            {
                "N": 90,
                "P": 42,
                "K": 43,
                "temperature": 20.8,
                "humidity": 82,
                "ph": 6.5,
                "rainfall": 202,
            }
        ]
    }}


class CropPredictionResponse(BaseModel):
    """Response schema for crop prediction."""

    recommended_crop: str
    confidence: Optional[float] = None
    candidates: Optional[list] = None


class FertilizerInput(BaseModel):
    """Input schema for fertilizer recommendation."""

    crop: str = Field(..., min_length=1, description="Crop name (e.g. Rice, Wheat)")
    soil_type: Optional[str] = Field(
        None, description="Optional soil type (e.g. Clay, Sandy, Loamy, Silt)"
    )
    N: Optional[float] = Field(None, ge=0, le=300, description="Optional nitrogen level")
    P: Optional[float] = Field(None, ge=0, le=300, description="Optional phosphorus level")
    K: Optional[float] = Field(None, ge=0, le=300, description="Optional potassium level")

    model_config = {"json_schema_extra": {
        "examples": [{"crop": "Rice"}]
    }}


class FertilizerResponse(BaseModel):
    """Response schema for fertilizer recommendation."""

    fertilizer: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str

class AgenticInput(BaseModel):
    """Input for the Agentic framework."""
    farmer_query: str = Field(..., description="The query from the farmer in natural language")
    sensor_data: dict = Field(..., description="Dictionary containing sensor data (N, P, K, pH, etc.)")
    
class AgenticResponse(BaseModel):
    """Response from the Agentic framework."""
    tasks: list
    reasoning: str
    predictions: dict
    xai_insights: dict
    final_recommendation: str
