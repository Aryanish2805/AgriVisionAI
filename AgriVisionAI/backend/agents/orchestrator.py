import sys
import os

# Ensure the backend directory is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.agents.planning_agent import PlanningAgent
from backend.agents.weather_agent import WeatherAgent
from backend.agents.crop_agent import CropAgent
from backend.agents.fertilizer_agent import FertilizerAgent
from backend.agents.market_agent import MarketAgent
from backend.agents.reasoning_agent import ReasoningAgent
from backend.agents.explainability_agent import ExplainabilityAgent
from backend.agents.recommendation_agent import RecommendationAgent

class AgentOrchestrator:
    """Master Pipeline connecting all specialized AI Agents sequentially."""
    def __init__(self):
        self.planning_agent = PlanningAgent()
        self.weather_agent = WeatherAgent()
        self.crop_agent = CropAgent()
        self.fertilizer_agent = FertilizerAgent()
        self.market_agent = MarketAgent()
        self.reasoning_agent = ReasoningAgent()
        self.xai_agent = ExplainabilityAgent()
        self.recommendation_agent = RecommendationAgent()

    def process_query(self, farmer_query: str, sensor_data: dict) -> dict:
        print("\n--- Starting Autonomous Agentic Pipeline ---")
        
        # 1. Planning Layer
        plan = self.planning_agent.plan(farmer_query)
        
        # 2. Context Layer (Weather)
        weather_context = self.weather_agent.get_weather("Local Farm")
        
        # 3. Model Inference Layers
        crop_result = {}
        if plan['tasks'].get('needs_crop_rec'):
            crop_result = self.crop_agent.recommend(sensor_data, weather_context)
            
        fert_result = {}
        if plan['tasks'].get('needs_fertilizer_rec') and crop_result.get("recommended_crop"):
            fert_result = self.fertilizer_agent.recommend(sensor_data, crop_result.get("recommended_crop"))
            
        market_result = {}
        if plan['tasks'].get('needs_market_pricing') and crop_result.get("recommended_crop"):
            market_result = self.market_agent.predict_price(crop_result.get("recommended_crop"))
            
        # 4. Synthesizer Layers
        reasoning = self.reasoning_agent.reason(crop_result, fert_result, market_result, weather_context)
        
        xai_context = {}
        if crop_result:
            xai_context = self.xai_agent.explain(crop_result.get("recommended_crop"))
            
        # 5. Final Recommendation
        final_output = self.recommendation_agent.generate_final_response(
            plan, weather_context, crop_result, fert_result, market_result, reasoning, xai_context
        )
        
        print("--- Pipeline Execution Complete ---\n")
        return final_output

if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    sample_query = "What crop should I plant now and do I need fertilizer?"
    sample_sensors = {'N': 90, 'P': 42, 'K': 43, 'ph': 6.5}
    
    response = orchestrator.process_query(sample_query, sample_sensors)
    print("\nFINAL OUTPUT JSON:\n", response)
