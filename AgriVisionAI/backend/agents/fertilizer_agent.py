class FertilizerAgent:
    """Agent responsible for Fertilizer Recommendations."""
    def __init__(self):
        self.name = "Fertilizer Agent"
        
    def recommend(self, sensor_data: dict, crop: str) -> dict:
        print(f"[{self.name}] Executing fertilizer recommendation for crop {crop}")
        # Rule based engine or stub for DNN
        
        N = sensor_data.get('N', 0)
        P = sensor_data.get('P', 0)
        K = sensor_data.get('K', 0)
        
        recommendation = "Balanced NPK 10:10:10"
        if N < 50:
            recommendation = "High Nitrogen Fertilizer (e.g. Urea)"
        elif P < 40:
            recommendation = "High Phosphorus Fertilizer"
            
        return {
            "recommended_fertilizer": recommendation,
            "rationale": f"Based on N:{N}, P:{P}, K:{K} for crop {crop}"
        }
