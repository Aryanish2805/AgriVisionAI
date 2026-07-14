class WeatherAgent:
    """Agent responsible for gathering weather context (Mocked for current scope)."""
    def __init__(self):
        self.name = "Weather Agent"
        
    def get_weather(self, location: str = "Unknown") -> dict:
        print(f"[{self.name}] Fetching weather for location: {location}")
        # Mock weather response
        return {
            "temperature_c": 28.5,
            "humidity_pct": 72.0,
            "rainfall_mm": 150.0,
            "status": "Sunny, Expecting rain"
        }
