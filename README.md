# Exoplanet AI

A full-stack machine learning web application for predicting whether an exoplanet candidate is likely to be confirmed based on NASA Kepler data.

## Features

* Predict whether a Kepler object is likely to be an exoplanet
* Manual input form for custom predictions
* Search and analytics dashboard
* Confidence score tracking
* Prediction history
* Interactive charts and statistics
* Light curve visualization support

## Tech Stack

### Frontend

* React
* JavaScript
* CSS

### Backend

* Python
* Flask
* XGBoost
* Pandas
* NumPy
* Scikit-learn

## Project Structure

```text
exoplanet-ai/
├── backend/
│   ├── app.py
│   ├── predict.py
│   ├── train_model.py
│   ├── lightcurve.py
│   ├── simple_lightcurve.py
│   ├── inspect_data.py
│   ├── requirements.txt
│   └── templates/
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── package-lock.json
├── data/
│   └── koi_data.csv
├── models/
│   └── my_xgb_model.pkl
└── .gitignore
```

## Installation

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## Running the Project

1. Start the backend server
2. Start the frontend server
3. Open the frontend in the browser
4. Enter exoplanet data or use search features
5. View prediction results and analytics

## Model Information

The machine learning model is trained using NASA Kepler exoplanet candidate data and uses XGBoost for classification.

## Future Improvements

* Add live NASA API integration
* Improve prediction explanations
* Add user authentication
* Store prediction history in a database
* Deploy frontend and backend online

## Author

Bahome Seraphin

* Elmhurst University
* Computer Science Major
* Minors in Mathematics and Physics
* GitHub: [https://github.com/Bahome-eng](https://github.com/Bahome-eng)

