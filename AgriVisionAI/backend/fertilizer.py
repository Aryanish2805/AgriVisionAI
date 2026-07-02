from pathlib import Path
import pandas as pd
from backend.validator import FertilizerInput, FertilizerResponse

# Path to the dataset
_FERTILIZER_CSV = Path(__file__).resolve().parent.parent.parent / "fertilizer_recommendation.csv"
_df_fert = None


def load_fertilizer_data():
    """Load fertilizer dataset on startup."""
    global _df_fert
    if _FERTILIZER_CSV.exists():
        try:
            _df_fert = pd.read_csv(_FERTILIZER_CSV)
            print(f"[fertilizer] Loaded {_FERTILIZER_CSV.name}")
        except Exception as e:
            print(f"[fertilizer] Error loading dataset: {e}")
    else:
        print(f"[fertilizer] WARNING: {_FERTILIZER_CSV} not found.")


def recommend_fertilizer(input_data: FertilizerInput) -> FertilizerResponse:
    """Recommend fertilizer based on crop, and optionally soil and NPK."""
    
    if _df_fert is None or _df_fert.empty:
        # Fallback if no dataset
        return FertilizerResponse(
            fertilizer="Urea", 
            details={"message": "No dataset found, returning default."}
        )

    df = _df_fert.copy()
    
    # Filter by crop if present
    # Assuming Crop_Type column exists
    crop_col_exists = "Crop_Type" in df.columns
    if crop_col_exists:
        # Case insensitive match if possible, or exact
        df_crop = df[df["Crop_Type"].str.lower() == input_data.crop.lower()]
        if not df_crop.empty:
            df = df_crop

    # Filter by soil if provided
    soil_col_exists = "Soil_Type" in df.columns
    if soil_col_exists and input_data.soil_type:
        df_soil = df[df["Soil_Type"].str.lower() == input_data.soil_type.lower()]
        if not df_soil.empty:
            df = df_soil

    # If NPK provided and we have NPK columns, we could do nearest neighbor
    # But for a simple approach, we'll just take the mode of the remaining filtered set
    if "Recommended_Fertilizer" in df.columns:
        mode = df["Recommended_Fertilizer"].mode()
        if not mode.empty:
            rec = mode.iloc[0]
            return FertilizerResponse(
                fertilizer=rec,
                details={"message": "Based on historical recommendations."}
            )

    return FertilizerResponse(
        fertilizer="Urea",
        details={"message": "Could not determine from dataset, returning default."}
    )
