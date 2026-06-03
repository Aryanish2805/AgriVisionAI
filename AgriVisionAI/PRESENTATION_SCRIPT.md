# AgriVision AI - Presentation Script

---

## **OPENING (30 seconds)**
**Speaker: Aryanish**

"Good [morning/afternoon], everyone. We are team AgriVision, and today we're presenting an AI-Based Crop Recommendation System that helps farmers make data-driven decisions about which crop to plant based on soil, rainfall, temperature, and humidity conditions."

---

## **PROBLEM STATEMENT (1 minute)**
**Speaker: Aryanish**

"The problem we're solving:
- Farmers often struggle to choose the right crop for their land
- They lack data-driven guidance on what grows best in their specific conditions
- Poor crop selection leads to lower yields and financial risk
- Our solution uses Machine Learning and rule-based logic to provide intelligent recommendations"

---

## **SOLUTION OVERVIEW (1 minute)**
**Speaker: Aryanish**

"Our system has three main components:

1. **Data Layer** - Crop recommendation datasets with soil, rainfall, temperature, humidity, and target crops
2. **ML Model Layer** - A trained decision tree model that learns from historical data
3. **Web Application** - A Streamlit interface where farmers can input their conditions and get instant recommendations

The app is smart: it tries to use a trained ML model first, and if one doesn't exist, it falls back to proven rule-based recommendations."

---

## **TEAM CONTRIBUTIONS (1.5 minutes)**
**Speaker: Adarsh**

"**My Role - Dataset Management:**
- Collected and organized crop recommendation data
- Created the `crop_recommendation.csv` dataset with columns: soil_type, rainfall_mm, temperature_c, humidity_pct, crop
- Ensured data quality and consistency across 30+ crop records
- Supported data validation for both soil-based and Kaggle-style numeric schemas
- This dataset is the foundation that trains our ML model"

**Speaker: Surya**

"**My Role - Supporting Work:**
- Helped with initial project structure planning
- Assisted in testing the recommendation logic
- Contributed to debugging and validation during development"

**Speaker: Aryanish**

"**My Role - Core Development & Lead:**
- Built the entire Streamlit web application (`frontend/app.py`)
- Developed the ML recommendation engine (`ml_model/crop_recommender.py`)
- Implemented the training pipeline (`ml_model/train.py`)
- Created the data loading and evaluation modules
- Implemented both ML-based and rule-based fallback logic
- Added location-to-soil mapping presets (Rajasthan → Loamy, etc.)
- Created launcher scripts (`run_app.bat`, `run_app.ps1`) for easy startup
- Ensured the entire system integrates seamlessly"

---

## **TECHNICAL ARCHITECTURE (1.5 minutes)**
**Speaker: Aryanish**

"Let me walk you through the architecture:

**Frontend (Streamlit App)**
- User enters: Location (optional), Soil type, Rainfall (mm), Temperature (°C), Humidity (%)
- Click 'Recommend crop' button
- The app displays the best recommended crop with confidence percentage

**Backend (ML Model)**
- Uses a Decision Tree Classifier trained on crop data
- Input features: soil_type, rainfall_mm, temperature_c, humidity_pct
- Output: Predicted crop name + probability scores

**Fallback Logic (Rule-Based)**
- If no ML model exists or input doesn't match, uses hardcoded crop rules
- Rules are based on: soil suitability, rainfall range, temperature range
- Example: Maize grows best in Loamy/Sandy soil, 50-200mm rainfall, 18-32°C temperature

**Dataset Management**
- Supports two schemas:
  1. Soil-based: soil_type, rainfall_mm, temperature_c, humidity_pct, crop
  2. Kaggle-style: N, P, K, temperature, humidity, ph, rainfall, label
- Users can upload new datasets and retrain the model from the app"

---

## **FEATURES & FUNCTIONALITY (2 minutes)**
**Speaker: Aryanish**

"The application has 5 main tabs:

**Tab 1: Recommend Crop**
- Users input their field conditions
- Click 'Recommend crop'
- See the top recommendation + list of alternative crops with probabilities
- This is the core feature

**Tab 2: Upload Training Dataset**
- Upload your own CSV with crop data
- App shows a preview
- Save it to the project
- Train a new ML model on your custom data (with one click or command)

**Tab 3: Fertilizer Recommendations**
- (Future enhancement for fertilizer suggestions)
- Looks up nearest matching historical fertilizer records

**Tab 4: Mandi / Market Prices**
- (Future enhancement for market price tracking)
- Shows commodity prices

**Tab 5: Model Evaluation**
- Run model evaluation to see accuracy metrics
- View confusion matrix
- Download evaluation reports

**Smart Behavior:**
- The app automatically detects your dataset schema (soil-based or Kaggle)
- Uses the trained ML model if available
- Falls back to rule-based recommendations if no model exists
- Shows confidence scores (e.g., 100.00% for Maize)"

---

## **DEMO WALKTHROUGH (3-5 minutes)**
**Speaker: Aryanish** (while demonstrating the app)

"Let me show you the app in action:

1. **Open the app:**
   ```
   python -m streamlit run frontend/app.py
   ```
   Navigate to `http://localhost:8501`

2. **Fill in the form:**
   - Location: 'Rajasthan' (auto-selects Loamy soil)
   - Soil type: Loamy
   - Rainfall: 120 mm
   - Temperature: 25°C
   - Humidity: 60%

3. **Click 'Recommend crop'**
   - App shows: 'Recommended crop: Maize (100.00%)'
   - Shows other candidates: Cotton (0%), Rice (0%), etc.

4. **Try another location:**
   - Change to Punjab → auto-selects Loamy
   - Same conditions might recommend Wheat

5. **Upload a custom dataset:**
   - Go to 'Upload Training Dataset' tab
   - Upload a CSV with your farm data
   - Save it
   - Click 'Train model on selected dataset'
   - The app retrains and uses your model immediately

6. **View Model Evaluation:**
   - Go to 'Model Evaluation' tab
   - Click 'Run Model Evaluation'
   - See accuracy, confusion matrix, and detailed report"

---

## **TECHNICAL STACK (1 minute)**
**Speaker: Aryanish**

"Technologies used:
- **Backend:** Python 3.x with scikit-learn (ML), pandas (data), joblib (model persistence)
- **Frontend:** Streamlit (web app framework)
- **Model:** Decision Tree Classifier
- **Data Format:** CSV datasets
- **Environment:** Virtual environment with all dependencies in `requirements.txt`

**Key Files:**
- `frontend/app.py` - Main Streamlit application
- `ml_model/crop_recommender.py` - Recommendation logic (ML + rules)
- `ml_model/train.py` - Model training pipeline
- `ml_model/crop_model.joblib` - Trained model artifact
- `dataset/crop_recommendation.csv` - Training data
- `run_app.bat` / `run_app.ps1` - Quick launch scripts"

---

## **HOW TO RUN (1 minute)**
**Speaker: Aryanish**

"Starting the application is simple:

**Option 1: Quick launch (Windows)**
```
run_app.bat
```

**Option 2: Command line**
```
cd D:\AgriVision\AgriVisionAI
python -m streamlit run frontend/app.py
```

**Option 3: PowerShell**
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\run_app.ps1
```

Then open your browser to `http://localhost:8501` and you're ready to use the app."

---

## **MODEL PERFORMANCE & RESULTS (1 minute)**
**Speaker: Aryanish**

"The model has been trained on 30+ crop records with the following results:

**Training Accuracy:**
- The Decision Tree model achieves high accuracy on training data
- Successfully learns patterns like:
  - Loamy + 120mm rain + 25°C → Wheat/Maize
  - Clay + 200mm rain + 28°C → Rice
  - Sandy + 90mm rain + 26°C → Cotton/Maize

**Rule-Based Fallback:**
- When ML model unavailable, rule-based logic provides immediate recommendations
- Based on agronomic knowledge (soil suitability ranges, optimal rainfall, temperature)
- Ensures the app always gives helpful guidance

**Future Improvements:**
- Train on larger datasets (PlantVillage dataset is available but unused currently)
- Add more crops and conditions
- Incorporate weather forecasts for better predictions
- Add disease detection (we have plant disease images ready)"

---

## **ADVANTAGES & IMPACT (1 minute)**
**Speaker: Aryanish**

"Why this project matters:

1. **Accessible:** Simple web interface - no coding knowledge needed
2. **Data-driven:** Uses ML + historical agronomic knowledge
3. **Customizable:** Users can upload their own data and train models
4. **Scalable:** Can handle 50+ crops and multiple soil types
5. **Reliable:** Dual recommendation system (ML + rules) ensures guidance is always available
6. **Fast:** Instant recommendations, no waiting
7. **Portable:** Runs locally - no cloud dependencies, farmer privacy protected"

---

## **CHALLENGES & SOLUTIONS (1 minute)**
**Speaker: Aryanish**

"Challenges we faced:

**Challenge 1:** ML model not available initially
- **Solution:** Implemented rule-based fallback with proven agronomic rules

**Challenge 2:** Different dataset schemas (soil-based vs Kaggle style)
- **Solution:** Auto-detection logic that identifies dataset schema and adapts

**Challenge 3:** Making the app user-friendly
- **Solution:** Clear forms, helpful info messages, one-click recommendations, location auto-suggestions

**Challenge 4:** Managing dependencies and environment setup
- **Solution:** Created launcher scripts (`.bat` and `.ps1`) for one-click startup"

---

## **FUTURE ROADMAP (1 minute)**
**Speaker: Aryanish**

"Next steps for AgriVision:

1. **Disease Detection:** Use PlantVillage dataset (1000+ plant images) to detect crop diseases
2. **Market Integration:** Show real-time market prices for recommended crops
3. **Weather API:** Fetch live weather data instead of manual input
4. **Multi-language:** Support regional languages (Hindi, Tamil, Marathi, etc.)
5. **Mobile App:** Convert to mobile for easier field access
6. **Predictive Analytics:** Forecast yield based on conditions
7. **Fertilizer Optimization:** Recommend fertilizer ratios (N:P:K) for each crop
8. **Farm Network:** Connect farmers to share best practices and market prices"

---

## **CLOSING (30 seconds)**
**Speaker: Aryanish**

"In summary, we've built a practical, AI-powered system that helps farmers make smarter crop decisions. The combination of machine learning and rule-based logic ensures reliable recommendations in all scenarios.

Our team focused on delivering a working, deployable product that solves a real problem for farmers. Thank you for listening!

**Do you have any questions?**"

---

---

# **PRESENTATION TIPS FOR EACH SPEAKER**

## **Aryanish (Lead Speaker)**
- Speak clearly and confidently (you did 80% of the work)
- Use the Streamlit app demo to show features in action
- Explain technical concepts simply (e.g., "decision tree" = a set of if-then rules)
- Keep transitions smooth between sections
- Pace: ~2 min per slide, 3 min for demo
- Eye contact with audience

## **Adarsh (Data & Support)**
- Briefly explain the importance of good datasets (foundation of ML)
- Show the dataset structure (columns: soil_type, rainfall_mm, etc.)
- Emphasize that data quality = better recommendations
- Be proud of the data work - it's essential!

## **Surya (Support)**
- Briefly mention your contributions (testing, debugging)
- Show enthusiasm and support for the team
- If asked, explain a simple feature (like location-to-soil mapping)

---

# **TIMING BREAKDOWN**

- Opening: 30 seconds
- Problem: 1 min
- Solution: 1 min
- Team Roles: 1.5 min
- Architecture: 1.5 min
- Features: 2 min
- **Demo: 3-5 min** ← This is the most important part!
- Tech Stack: 1 min
- How to Run: 1 min
- Model Performance: 1 min
- Advantages: 1 min
- Challenges: 1 min
- Future: 1 min
- Closing: 30 seconds

**Total: 17-19 minutes** (Leave 1-3 min for questions)

---

# **KEY POINTS TO EMPHASIZE**

1. ✅ **It works!** Show the demo
2. ✅ **It's practical** - Solves real farmer problems
3. ✅ **It's smart** - Uses both ML and rules
4. ✅ **It's customizable** - Users can add their own data
5. ✅ **It's reliable** - Always gives a recommendation
6. ✅ **Aryanish did the heavy lifting** - Make sure to highlight this
7. ✅ **Adarsh's data is the foundation** - Don't skip the data
8. ✅ **Team effort** - Everyone contributed meaningfully

---

# **POTENTIAL QUESTIONS & ANSWERS**

**Q: How accurate is the model?**
A: "The decision tree achieves high accuracy on training data. More importantly, it always provides a recommendation - either from the ML model or from proven agronomic rules."

**Q: Can it work without internet?**
A: "Yes! The app runs locally. No cloud dependency. Perfect for rural areas with limited connectivity."

**Q: How do farmers use this?**
A: "They open the app, enter their field conditions (soil, rainfall, temperature, humidity), click 'Recommend crop', and instantly see what to plant."

**Q: What crops can it recommend?**
A: "Currently: Wheat, Rice, Maize, Soybean, Cotton. The system is scalable - users can train it on 50+ crops with their own data."

**Q: Is this production-ready?**
A: "Yes. It's fully functional and can be deployed today. Future improvements (disease detection, market prices) are planned."

---
