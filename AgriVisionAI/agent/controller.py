import os
import json
import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Placeholder for LLM - can be replaced with ChatOpenAI or ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOpenAI 

# Import DL models
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml"))
try:
    from ml.dl_models.dataset import CropDataset
    from ml.dl_models.cnn_attention import CNNAttentionModel
except ImportError:
    pass

class PlanningAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an agricultural planning agent. Given a farmer's request, determine which AI models need to be invoked. Available models: 'crop_recommendation', 'fertilizer_recommendation', 'price_prediction'. Return a JSON array of model names."),
            ("user", "{farmer_input}")
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()
        
    def plan(self, farmer_input):
        response = self.chain.invoke({"farmer_input": farmer_input})
        try:
            # Basic parsing, assuming LLM returns JSON array
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response.strip())
        except:
            return ["crop_recommendation", "fertilizer_recommendation"] # fallback

class ReasoningAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an agricultural reasoning agent. Analyze the following soil and weather data, and point out any critical constraints or anomalies (e.g., highly acidic soil, low rainfall). Keep it brief."),
            ("user", "{data}")
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()
        
    def reason(self, data_dict):
        return self.chain.invoke({"data": json.dumps(data_dict)})

class ToolAgent:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load dataset to get scaler and classes
        dataset_path = os.path.join(base_dir, "dataset", "Crop_recommendation_kaggle.csv")
        try:
            df = pd.read_csv(dataset_path)
            label_col = 'label' if 'label' in df.columns else 'crop'
            df = df.dropna(subset=[label_col])
            train_df, _ = train_test_split(df, test_size=0.3, random_state=42, stratify=df.get(label_col))
            self.train_set = CropDataset(dataframe=train_df, is_train=True)
            
            # Load CNN model
            model_path = os.path.join(base_dir, "ml", "dl_models", "saved_models", "cnn_attention.pth")
            self.crop_model = CNNAttentionModel(num_features=self.train_set.get_num_features(), num_classes=self.train_set.get_num_classes())
            self.crop_model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
            self.crop_model.to(self.device)
            self.crop_model.eval()
            self.model_loaded = True
        except Exception as e:
            print(f"Warning: Could not load real DL model. Error: {e}")
            self.model_loaded = False
        
    def invoke_crop_model(self, data):
        if not self.model_loaded:
            return "Rice (Mock)"
            
        try:
            feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
            # Extract features safely
            raw_features = [
                data.get('N', 0), data.get('P', 0), data.get('K', 0),
                data.get('temperature', 0), data.get('humidity', 0), 
                data.get('ph', 0), data.get('rainfall', 0)
            ]
            
            scaled_features = self.train_set.scaler.transform([raw_features])
            inputs = torch.tensor(scaled_features, dtype=torch.float32).to(self.device)
            
            with torch.no_grad():
                outputs = self.crop_model(inputs)
                _, predicted_idx = torch.max(outputs.data, 1)
                
            predicted_class = self.train_set.classes[predicted_idx.item()]
            return predicted_class
        except Exception as e:
            print(f"Error in inference: {e}")
            return "Rice (Fallback)"
        
    def invoke_fertilizer_model(self, data):
        # TODO: Load fertilizer_dl_model.pth, run inference, return fertilizer
        return "Urea"
        
    def invoke_price_model(self, data):
        # TODO: Load price_dl_model.pth, run inference, return price
        return 2050.0

class RecommendationAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the final agricultural recommendation agent. Combine the reasoning analysis, model predictions, and SHAP XAI insights into a clear, trustworthy, and actionable recommendation for the farmer."),
            ("user", "Reasoning: {reasoning}\nPredictions: {predictions}\nXAI Insights: {xai_insights}")
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()
        
    def recommend(self, reasoning, predictions, xai_insights):
        return self.chain.invoke({
            "reasoning": reasoning, 
            "predictions": json.dumps(predictions),
            "xai_insights": json.dumps(xai_insights)
        })

class AgenticController:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY", "mock_key")
        
        # In a real deployment, initialize the actual LLM here
        self.llm = ChatOpenAI(temperature=0, openai_api_key=api_key) if api_key != "mock_key" else None
        
        # If no API key is provided, we use a mock LLM for testing
        if self.llm is None:
            from langchain_core.language_models import FakeListLLM
            self.llm = FakeListLLM(responses=[
                '["crop_recommendation", "fertilizer_recommendation"]',
                'The soil has low nitrogen, which is a constraint for nitrogen-hungry crops.',
                'Based on the deep learning model, Rice is recommended. The SHAP explanation shows that high rainfall and neutral pH were the top driving factors for this recommendation. Apply Urea fertilizer to address the low nitrogen.'
            ])
            
        self.planner = PlanningAgent(self.llm)
        self.reasoner = ReasoningAgent(self.llm)
        self.tool_agent = ToolAgent()
        self.recommender = RecommendationAgent(self.llm)
        
    def process_request(self, farmer_input, sensor_data):
        print("1. Planning Agent is analyzing the request...")
        tasks = self.planner.plan(farmer_input)
        print(f"   Tasks planned: {tasks}")
        
        print("2. Reasoning Agent is analyzing sensor data...")
        reasoning_result = self.reasoner.reason(sensor_data)
        print(f"   Reasoning: {reasoning_result}")
        
        print("3. Tool Agent is invoking Deep Learning models...")
        predictions = {}
        if "crop_recommendation" in tasks:
            predictions['crop'] = self.tool_agent.invoke_crop_model(sensor_data)
        if "fertilizer_recommendation" in tasks:
            predictions['fertilizer'] = self.tool_agent.invoke_fertilizer_model(sensor_data)
        if "price_prediction" in tasks:
            predictions['price'] = self.tool_agent.invoke_price_model(sensor_data)
            
        print(f"   Predictions: {predictions}")
        
        print("4. XAI Module is generating insights (Mocked)...")
        # In a real run, this calls explainer.explain_single_prediction()
        xai_insights = {
            "top_features": ["rainfall: 0.85", "nitrogen: 0.62", "ph: 0.41"]
        }
        
        print("5. Recommendation Agent is synthesizing the final output...")
        final_recommendation = self.recommender.recommend(reasoning_result, predictions, xai_insights)
        
        return {
            "tasks": tasks,
            "reasoning": reasoning_result,
            "predictions": predictions,
            "xai_insights": xai_insights,
            "final_recommendation": final_recommendation
        }

if __name__ == "__main__":
    controller = AgenticController()
    
    farmer_query = "I want to know what crop to plant this season and what fertilizer to use."
    sensor_data = {
        "nitrogen": 40,
        "phosphorus": 50,
        "potassium": 40,
        "temperature": 25.0,
        "humidity": 80.0,
        "ph": 6.5,
        "rainfall": 200.0
    }
    
    result = controller.process_request(farmer_query, sensor_data)
    print("\n--- FINAL OUTPUT ---")
    print(result["final_recommendation"])
