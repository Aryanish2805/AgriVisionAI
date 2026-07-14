import urllib.request
import os

urls = [
    'https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-processed/crop_recommendation.csv',
    'https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-raw/Crop_recommendation.csv',
    'https://raw.githubusercontent.com/aakashr02/Crop-Recommendation/main/Crop_recommendation.csv'
]

os.makedirs('dataset', exist_ok=True)
success = False

for u in urls:
    try:
        print(f"Trying {u}")
        urllib.request.urlretrieve(u, 'dataset/Crop_recommendation.csv')
        print('Downloaded from', u)
        success = True
        break
    except Exception as e:
        print(e)
        
if not success:
    print("Failed to download dataset.")
