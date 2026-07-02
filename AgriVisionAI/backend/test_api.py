import requests

BASE_URL = "http://localhost:8000"

def test_health():
    res = requests.get(f"{BASE_URL}/health")
    print("Health:", res.json())

def test_predict():
    payload = {
        "N": 90, "P": 42, "K": 43,
        "temperature": 20.8,
        "humidity": 82,
        "ph": 6.5,
        "rainfall": 202
    }
    res = requests.post(f"{BASE_URL}/predict", json=payload)
    print("Predict valid:", res.json())

def test_predict_invalid():
    payload = {
        "N": 90, "P": 42, "K": 43,
        "temperature": -100, # invalid
        "humidity": 500, # invalid
        "ph": 6.5,
        "rainfall": -25 # invalid
    }
    res = requests.post(f"{BASE_URL}/predict", json=payload)
    print("Predict invalid (status):", res.status_code)
    print("Predict invalid (error):", res.text)

def test_fertilizer():
    payload = {"crop": "Rice"}
    res = requests.post(f"{BASE_URL}/fertilizer", json=payload)
    print("Fertilizer:", res.json())

def test_history():
    res = requests.get(f"{BASE_URL}/history")
    print("History:", res.json())

if __name__ == "__main__":
    test_health()
    test_predict()
    test_predict_invalid()
    test_fertilizer()
    test_history()
