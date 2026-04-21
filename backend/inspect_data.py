import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

print("Loading dataset...")

# ✅ NORMAL read (no comment="#")
df = pd.read_csv("../data/koi_data.csv")

print("Dataset loaded!")
print("Shape:", df.shape)

# -----------------------------
# Features
# -----------------------------
features = [
    "koi_period",
    "koi_time0bk",
    "koi_duration",
    "koi_depth",
    "koi_kepmag"
]

X = df[features]

# -----------------------------
# Target
# -----------------------------
df["target"] = df["koi_disposition"].map({
    "CONFIRMED": 1,
    "CANDIDATE": 1,
    "FALSE POSITIVE": 0
})

y = df["target"]

print("Class distribution:")
print(y.value_counts())

# -----------------------------
# Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# -----------------------------
# Train
# -----------------------------
model = XGBClassifier(
    random_state=42,
    use_label_encoder=False,
    eval_metric="logloss"
)

model.fit(X_train, y_train)

print("Model trained!")

# -----------------------------
# Save
# -----------------------------
os.makedirs("../model", exist_ok=True)

joblib.dump(model, "../model/exoplanet_model.pkl")

print("Model saved!")

# -----------------------------
# Evaluate
# -----------------------------
print("Train accuracy:", model.score(X_train, y_train))
print("Test accuracy:", model.score(X_test, y_test))

print("✅ DONE")