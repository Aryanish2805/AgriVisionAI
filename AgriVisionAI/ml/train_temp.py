import os

os.chdir(
    "d:/AgriVision/AgriVisionAI/ml"
)

import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.preprocessing import LabelEncoder

from xgboost import XGBClassifier

from sklearn.metrics import accuracy_score

import joblib
df = pd.read_csv(
    "datasets/fertilizer_recommendation_preprocessed.csv"
)

df.head()
fertilizer_columns = [
    "recommended_fertilizer_compost",
    "recommended_fertilizer_dap",
    "recommended_fertilizer_mop",
    "recommended_fertilizer_npk",
    "recommended_fertilizer_ssp",
    "recommended_fertilizer_urea",
    "recommended_fertilizer_zinc sulphate"
]


y = df[fertilizer_columns].idxmax(axis=1)


y = y.str.replace(
    "recommended_fertilizer_",
    ""
)


X = df.drop(
    fertilizer_columns + ["fertilizer_code"],
    axis=1
)


print(X.shape)
print(y.shape)
encoder = LabelEncoder()


y_encoded = encoder.fit_transform(
    y
)


print(
    encoder.classes_
)
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42
)

fertilizer_xgb = XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)


fertilizer_xgb.fit(
    X_train,
    y_train
)
prediction = fertilizer_xgb.predict(
    X_test
)


accuracy = accuracy_score(
    y_test,
    prediction
)


print(
    "Fertilizer XGBoost Accuracy:",
    accuracy * 100
)
joblib.dump(
    fertilizer_xgb,
    "models/fertilizer_xgboost.pkl"
)


joblib.dump(
    encoder,
    "models/fertilizer_label_encoder.pkl"
)
