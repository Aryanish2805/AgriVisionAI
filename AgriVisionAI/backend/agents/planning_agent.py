class PlanningAgent:
    """Agent responsible for understanding the farmer query and planning required actions."""
    def __init__(self):
        self.name = "Planning Agent"

    def plan(self, farmer_query: str) -> dict:
        """Parses user objectives and decides routing (crop, fertilizer, market)."""
        print(f"[{self.name}] Planning workflow for query: '{farmer_query}'")
        
        # Simplified logic for planning based on keywords
        query = farmer_query.lower()
        tasks = {
            'needs_crop_rec': 'crop' in query or 'grow' in query or 'plant' in query,
            'needs_fertilizer_rec': 'fertilizer' in query or 'nutrient' in query,
            'needs_market_pricing': 'price' in query or 'market' in query or 'sell' in query
        }
        
        # Default to crop recommendation if unclear
        if not any(tasks.values()):
            tasks['needs_crop_rec'] = True

        return {
            "query": farmer_query,
            "tasks": tasks,
            "status": "Planned"
        }
