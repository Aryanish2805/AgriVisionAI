import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load dataset
data = pd.read_csv("dataset/Crop_recommendation.csv")

print(data.head())

# Features
X = data[['soil_type', 'rainfall_mm', 'temperature_c', 'humidity_pct']]

# Target
y = data['crop']

# Convert soil_type text to numbers
X = pd.get_dummies(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)

print(f"Model Accuracy: {accuracy:.2f}")

# Save model
joblib.dump(model, "crop_model.pkl")

print("Model Saved Successfully!")