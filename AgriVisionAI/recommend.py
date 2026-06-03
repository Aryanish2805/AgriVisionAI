from pathlib import Path

from ml_model.crop_recommender import recommend_crop

if __name__ == "__main__":
    print("AI-Based Crop Recommendation System")
    print("This script demonstrates the current crop recommendation logic.")
    print(recommend_crop("Loamy", 120, 22, 60))
    print()
    print("To train the ML model with sample data, run:")
    print("  python ml_model/train.py")
    print("Then rerun this script or use frontend/app.py.")
