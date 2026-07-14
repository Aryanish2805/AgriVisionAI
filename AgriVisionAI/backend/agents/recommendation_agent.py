class RecommendationAgent:
    """Agent responsible for packaging the final response to the farmer."""
    def __init__(self):
        self.name = "Recommendation Agent"
        
    def generate_final_response(self, plan: dict, weather: dict, crop: dict, fert: dict, market: dict, rationale: dict, xai: dict) -> dict:
        print(f"[{self.name}] Compiling final agentic response...")
        return {
            "status": "Success",
            "query": plan.get("query"),
            "weather_context": weather,
            "crop_recommendation": crop,
            "fertilizer_recommendation": fert,
            "market_forecast": market,
            "reasoning": rationale,
            "xai_artifacts": xai,
            "message": "Based on current soil conditions and a forecasted upward market trend, we recommend planting " + crop.get("recommended_crop", "the specified crop") + ". " + fert.get("recommended_fertilizer", "")
        }
