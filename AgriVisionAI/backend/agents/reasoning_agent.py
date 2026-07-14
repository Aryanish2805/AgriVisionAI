class ReasoningAgent:
    """Agent responsible for aggregating data and creating a rationale."""
    def __init__(self):
        self.name = "Reasoning Agent"
        
    def reason(self, crop_data: dict, fert_data: dict, market_data: dict, weather_data: dict) -> dict:
        print(f"[{self.name}] Synthesizing recommendations...")
        
        reasons = []
        if weather_data.get('rainfall_mm', 0) > 100:
            reasons.append("High rainfall expected, ensure proper drainage.")
        
        crop = crop_data.get("recommended_crop", "Unknown")
        trend = market_data.get("trend", "Stable")
        
        reasons.append(f"The chosen crop ({crop}) has a {trend.lower()} market trend.")
        
        return {
            "insights": reasons,
            "overall_confidence": 0.85
        }
