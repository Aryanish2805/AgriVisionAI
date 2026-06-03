# Dataset Structure for Crop Recommendation

This project expects a CSV dataset with the following columns:

- `soil_type`: Categorical soil type used for prediction.
- `rainfall_mm`: Numeric rainfall amount in millimeters.
- `temperature_c`: Numeric average temperature in degrees Celsius.
- `humidity_pct`: Numeric relative humidity percentage.
- `crop`: Target crop label to recommend.

## Example rows

```csv
soil_type,rainfall_mm,temperature_c,humidity_pct,crop
Loamy,120,22,60,Wheat
Clay,200,28,70,Rice
Sandy,90,26,65,Maize
```

## Notes

- The CSV file should be saved as `dataset/crop_recommendation.csv` to be used by the training script.
- The file can be replaced with a larger dataset once you have a more complete crop recommendation dataset.
- Valid soil types in the current model are: `Loamy`, `Sandy`, `Clay`, `Silty`, `Peaty`, `Chalky`.
