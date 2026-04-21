import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
import pickle
import os

print("🚀 Starting Exoplanet Model Training...")

# Load dataset
df = pd.read_csv("../data/koi_data.csv", comment="#", engine="python")

print("✅ Dataset loaded!")
print("Original shape:", df.shape)

# Features (VALID for your dataset)
features = [
    "koi_period",
    "koi_time0bk",
    "koi_duration",
    "koi_depth",
    "koi_prad",
    "koi_teq",
    "koi_insol",
    "koi_model_snr",
    "koi_impact",
    "koi_steff",
    "koi_slogg",
    "koi_srad",
    "ra",
    "dec",
    "koi_kepmag"
]

print("🧹 Cleaning data...")

# Convert to numeric
for col in features:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Fill missing values (KEY FIX)
df[features] = df[features].fillna(df[features].median())

# Target
df["target"] = df["koi_disposition"].map({
    "CONFIRMED": 1,
    "CANDIDATE": 1,
    "FALSE POSITIVE": 0
})

df = df.dropna(subset=["target"])

print("After cleaning:", df.shape)

# Split
X = df[features]
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Train size:", len(X_train))
print("Test size:", len(X_test))

# Train model
print("🤖 Training model...")

model = XGBClassifier(
    random_state=42,
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    use_label_encoder=False,
    eval_metric="logloss"
)

model.fit(X_train, y_train)

print("✅ Model trained!")

# Save
os.makedirs("../models", exist_ok=True)

with open("../models/my_xgb_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("💾 Model saved!")

# Evaluate
print("\n📊 RESULTS:")
print("Train Accuracy:", model.score(X_train, y_train))
print("Test Accuracy:", model.score(X_test, y_test))

print("\n🎉 DONE!")