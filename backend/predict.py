import pickle
import pandas as pd

# Load your trained model
with open("../models/my_xgb_model.pkl", "rb") as f:
    model = pickle.load(f)

print("✅ Model loaded!")

# Example input (MUST match feature order)
data = {
    "koi_period": 10,
    "koi_time0bk": 200,
    "koi_duration": 2.5,
    "koi_depth": 500,
    "koi_prad": 50,
    "koi_teq": 500,
    "koi_insol": 1.5,
    "koi_model_snr": 1,
    "koi_impact": 0.5,
    "koi_steff": 5500,
    "koi_slogg": 4.5,
    "koi_srad": 1,
    "ra": 290,
    "dec": 45,
    "koi_kepmag": 15
}

df = pd.DataFrame([data])

# Predict
prediction = model.predict(df)[0]
probability = model.predict_proba(df)[0][1]

print("\n🔮 Prediction Result:")
print("Is Exoplanet:", bool(prediction))
print("Confidence:", round(probability, 3))