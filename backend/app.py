from flask import Flask, request, jsonify, render_template, send_file
from lightcurve import generate_lightcurve as generate_real_lightcurve
import pickle
import pandas as pd
from flask_cors import CORS
import json
import os
from datetime import datetime
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Load model
with open("../models/my_xgb_model.pkl", "rb") as f:
    model = pickle.load(f)

print("✅ Model loaded!")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "predictions.json")


def load_predictions():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print("Error loading predictions:", e)
        return []


def save_predictions(predictions):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(predictions, f, indent=2)
        return True
    except Exception as e:
        print("Error saving predictions:", e)
        return False


def find_kepler_csv():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    possible_paths = [
        os.path.join(current_dir, "../data/koi_data.csv"),
        os.path.join(current_dir, "data/koi_data.csv"),
        os.path.join(current_dir, "../../data/koi_data.csv"),
    ]

    for path in possible_paths:
        normalized_path = os.path.abspath(path)

        if os.path.exists(normalized_path):
            print(f"✅ Using Kepler dataset: {normalized_path}")
            return normalized_path

    raise FileNotFoundError(
        "Kepler dataset not found. Expected data/koi_data.csv."
    )

def load_kepler_dataframe():
    csv_path = find_kepler_csv()

    if not csv_path:
        raise FileNotFoundError(
            "Kepler dataset not found. Expected data/koi_data.csv."
        )

    return pd.read_csv(
        csv_path,
        comment="#",
        on_bad_lines="skip"
    )


def normalize_columns(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        df = pd.DataFrame([data])

        prediction = model.predict(df)[0]
        probability = model.predict_proba(df)[0][1]

        return jsonify({
            "is_exoplanet": bool(prediction),
            "confidence": round(float(probability) * 100, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/autocomplete/kepler", methods=["GET"])
def get_autocomplete_suggestions():
    try:
        df = normalize_columns(load_kepler_dataframe())
        print("ALL COLUMNS:")
        print(df.columns.tolist())
        

        candidate_column = None
        for col in ["kepoi_name", "kepler_name", "koi_name", "KOI Name", "kepid_name"]:
            if col in df.columns:
                candidate_column = col
                break

        if candidate_column is None:
            return jsonify({"error": "No KOI name column found in dataset"}), 400

        suggestions = (
            df[candidate_column]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        query = request.args.get("q", "").lower().strip()
        if query:
            suggestions = [s for s in suggestions if query in s.lower()][:20]

        return jsonify({
            "suggestions": suggestions,
            "dataset": "kepler",
            "total_count": len(suggestions)
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to load Kepler options: {str(e)}"}), 500


@app.route("/api/predict/kepler", methods=["POST"])
def predict_kepler():
    try:
        data = request.get_json()
        koi_name = data.get("koi_name")

        if not koi_name:
            return jsonify({"error": "KOI name is required"}), 400

        df = normalize_columns(load_kepler_dataframe())
        print("AUTOCOMPLETE COLUMNS:", df.columns.tolist())
        

        candidate_column = None
        for col in ["kepoi_name", "koi_name", "KOI Name", "kepid_name", "kepler_name"]:
            if col in df.columns:
                candidate_column = col
                break

        if candidate_column is None:
            return jsonify({"error": "No KOI name column found in dataset"}), 400

        matching_rows = df[df[candidate_column].astype(str) == str(koi_name)]

        if matching_rows.empty:
            return jsonify({"error": f"KOI name {koi_name} not found in dataset"}), 404

        matching_row = matching_rows.iloc[[0]]

        nasa_classification = "UNKNOWN"
        for col in ["koi_disposition", "koi_pdisposition", "disposition", "label"]:
            if col in matching_row.columns:
                nasa_classification = str(matching_row[col].iloc[0])
                break

        expected_params = [
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

        missing = [col for col in expected_params if col not in matching_row.columns]
        if missing:
            return jsonify({
                "error": f"Dataset is missing required model columns: {missing}"
            }), 400

        data_point = matching_row[expected_params].copy()

        for col in expected_params:
            data_point[col] = pd.to_numeric(data_point[col], errors="coerce")

        data_point = data_point.fillna(0)

        prediction = model.predict(data_point)[0]
        probability = model.predict_proba(data_point)[0][1]

        return jsonify({
            "message": "Kepler prediction completed",
            "prediction": {
                "is_exoplanet": bool(prediction),
                "confidence": round(float(probability) * 100, 2),
                "koi_name": koi_name,
                "model_version": "my_xgb_model.pkl"
            },
            "nasa_classification": nasa_classification
        }), 200

    except Exception as e:
        print("predict_kepler error:", str(e))
        return jsonify({"error": f"Kepler prediction failed: {str(e)}"}), 500
    
@app.route("/api/predictions/save", methods=["POST", "OPTIONS"])
def save_prediction():
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    try:
        prediction_data = request.json

        if not prediction_data:
            return jsonify({"error": "No prediction data provided"}), 400

        predictions = load_predictions()

        if "timestamp" not in prediction_data:
            prediction_data["timestamp"] = datetime.now().isoformat()

        predictions.append(prediction_data)

        if save_predictions(predictions):
            print(f"✅ Saved prediction. Total saved: {len(predictions)}")
            return jsonify({
                "message": "Prediction saved successfully",
                "count": len(predictions)
            }), 200
        else:
            return jsonify({"error": "Failed to save prediction"}), 500

    except Exception as e:
        print("save_prediction error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/api/predictions", methods=["GET"])
def get_predictions():
    try:
        predictions = load_predictions()
        return jsonify({
            "predictions": predictions,
            "count": len(predictions)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/predictions/stats", methods=["GET"])
def get_prediction_stats():
    try:
        predictions = load_predictions()

        total_predictions = len(predictions)

        exoplanets_found = sum(
            1 for p in predictions
            if (
                p.get("prediction", {}).get("is_exoplanet", False)
                or p.get("is_exoplanet", False)
            )
        )

        confidence_values = []

        for p in predictions:
            if "prediction" in p and "confidence" in p["prediction"]:
                confidence_values.append(p["prediction"]["confidence"])
            elif "confidence" in p:
                confidence_values.append(p["confidence"])

        average_confidence = round(
            sum(confidence_values) / len(confidence_values),
            2
        ) if confidence_values else 0

        dataset_breakdown = {}
        for p in predictions:
            dataset = p.get("dataset", "unknown")
            dataset_breakdown[dataset] = dataset_breakdown.get(dataset, 0) + 1

        success_rate = round(
            (exoplanets_found / total_predictions) * 100,
            2
        ) if total_predictions > 0 else 0

        return jsonify({
            "total_predictions": total_predictions,
            "exoplanets_found": exoplanets_found,
            "average_confidence": average_confidence,
            "dataset_breakdown": dataset_breakdown,
            "success_rate": success_rate,
            "predictions": predictions
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/lightcurve/generate", methods=["POST"])
def generate_lightcurve():
    try:
        data = request.get_json()
        koi_name = data.get("koi_name")

        if not koi_name:
            return jsonify({"error": "KOI name is required"}), 400

        success, image_data, filename, kepid = generate_real_lightcurve(koi_name)

        if not success or not image_data:
            return jsonify({"error": f"Failed to generate real lightcurve for {koi_name}"}), 500

        lightcurve_dir = os.path.join(BASE_DIR, "lightcurves")
        os.makedirs(lightcurve_dir, exist_ok=True)

        filepath = os.path.join(lightcurve_dir, filename)
        with open(filepath, "wb") as f:
            f.write(image_data)

        return jsonify({
            "success": True,
            "filename": filename,
            "title": f"Light Curve for KIC {kepid}",
            "url": f"/api/lightcurve/{filename}"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Lightcurve generation failed: {str(e)}"}), 500


@app.route("/api/lightcurve/<filename>", methods=["GET"])
def get_lightcurve(filename):
    try:
        filepath = os.path.join(BASE_DIR, "lightcurves", filename)

        if not os.path.exists(filepath):
            return jsonify({"error": "Lightcurve not found"}), 404

        return send_file(filepath, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": f"Failed to serve lightcurve: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)