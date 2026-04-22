# Exoplanet Detector

A full-stack web application that predicts whether a Kepler Object of Interest (KOI) is an exoplanet using a trained XGBoost machine learning model.

The platform allows users to:

- search and autocomplete Kepler candidates
- generate exoplanet predictions with confidence scores
- compare predictions with NASA classifications
- generate light curves for selected candidates
- save prediction history
- view analytics and prediction trends

---

## Overview

This project uses NASA Kepler candidate data and a trained machine learning model to classify exoplanet candidates. It combines a React frontend with a Flask backend and supports real-time predictions, analytics, and light curve visualization.

---

## Features

### Prediction Engine
- Predicts whether a selected KOI is an exoplanet
- Uses a trained XGBoost classifier
- Returns a confidence score for every prediction
- Displays NASA classification for comparison

### Candidate Search
- Autocomplete search for KOI names
- Uses Kepler dataset records from `koi_data.csv`
- Supports quick candidate lookup and prediction

### Light Curve Generation
- Generates light curves for selected candidates
- Maps `kepoi_name` to `kepid`
- Uses `lightkurve` to retrieve Kepler light curve data
- Includes fallback light curve generation when needed

### Prediction History
- Saves predictions to `predictions.json`
- Keeps track of:
  - candidate ID
  - dataset
  - timestamp
  - prediction result
  - confidence score
  - NASA classification

### Analytics Dashboard
- Total predictions
- Exoplanets found
- Non-exoplanets
- Confidence score distribution
- Prediction activity over time

---

## Model Training

The prediction model was trained using NASA Kepler Objects of Interest (KOI) data.

### Dataset
The training pipeline uses Kepler candidate data containing astrophysical measurements for known confirmed planets, candidates, and false positives.

### Selected Features
The model uses the following key numerical features:

- `koi_period`
- `koi_time0bk`
- `koi_duration`
- `koi_depth`
- `koi_prad`
- `koi_teq`
- `koi_insol`
- `koi_model_snr`
- `koi_impact`
- `koi_steff`
- `koi_slogg`
- `koi_srad`
- `ra`
- `dec`
- `koi_kepmag`

### Training Process
- cleaned and prepared the dataset
- selected relevant numerical features
- split the data into 80% training and 20% testing sets
- trained an XGBoost classifier
- evaluated performance on unseen test data
- exported the trained model to `my_xgb_model.pkl`
  
### Performance
- model accuracy: about **91%**
- confidence scores are derived from prediction probabilities

---

## Tech Stack

### Frontend
- React
- Styled Components
- Recharts

### Backend
- Flask
- Flask-CORS
- Pandas
- NumPy
- Matplotlib
- Lightkurve

### Machine Learning
- XGBoost
- Scikit-learn

---

## Project Structure

```text
exoplanet-ai/
├── backend/
│   ├── app.py
│   ├── lightcurve.py
│   ├── simple_lightcurve.py
│   ├── predictions.json
│   ├── lightcurves/
│   └── ...
│
├── data/
│   └── koi_data.csv
│
├── models/
│   └── my_xgb_model.pkl
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.js
│   └── package.json
│
└── README.md
How It Works
The user selects a KOI candidate from autocomplete.
The frontend sends the KOI name to the Flask backend.
The backend finds the matching row in the dataset.
The trained XGBoost model predicts whether the candidate is an exoplanet.
The backend returns:
predicted class
confidence score
NASA classification
The prediction is saved to history.
Analytics and charts update automatically.
The user can also generate a light curve for the same candidate.
Installation
1. Clone the repository
git clone <your-repo-url>
cd exoplanet-ai
2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install lightkurve
python app.py

Backend runs on:

http://127.0.0.1:5000
3. Frontend setup

Open a new terminal:

cd frontend
npm install
npm start

Frontend runs on:

http://localhost:3000
API Endpoints
Prediction
POST /api/predict/kepler
Autocomplete
GET /api/autocomplete/kepler
Prediction History
POST /api/predictions/save
GET /api/predictions
GET /api/predictions/stats
Light Curves
POST /api/lightcurve/generate
GET /api/lightcurve/<filename>
Example Use Case
Search for a KOI candidate such as K00752.01
Generate prediction
Review confidence score and NASA classification
Generate the light curve
Save the prediction
Open Analytics to view updated charts
Deployment Notes

Before deployment:

make sure requirements.txt is complete
make sure frontend API URLs point to the deployed backend, not localhost
add ignored files to .gitignore
remove unused debug prints
confirm predictions.json and lightcurves/ are handled properly in production

Recommended deployment:

Frontend: Vercel or Netlify
Backend: Render or Railway
Future Improvements
add support for more datasets
compare multiple ML models
improve analytics visuals
add filtering by date and candidate
add user accounts and saved sessions
deploy persistent database storage instead of JSON history
Author

Bahome Seraphin
Elmhurst University
B.S. in Computer Science, minors in Mathematics and Physics

GitHub: Bahome-eng
