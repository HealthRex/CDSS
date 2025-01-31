from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import pandas as pd  
import plotly.graph_objs as go
import plotly.io as pio
import urllib.request
import os
from pathlib import Path
from models import SurvivalFunction  # Import the class from models.py

app = Flask(__name__)

# Define model loading function
def load_model():
    try:
        # URL to the model file hosted on Google Drive
        model_url = "https://drive.google.com/uc?id=1fLjbWxe0jSiYj9x5JpgLR3STFrzyXXou"
        model_filename = "rsf_model.pkl"
        
        # Create absolute path for model file
        model_path = Path(__file__).parent / model_filename
        
        # Check if the model file exists locally, otherwise download it
        if not model_path.exists():
            print(f"Downloading model to {model_path}")
            urllib.request.urlretrieve(model_url, model_path)
        
        print(f"Loading model from {model_path}")
        return joblib.load(model_path)
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

# Load model and curves at startup
try:
    model = load_model()
    high_risk_sf = model.high_risk_sf
    low_risk_sf = model.low_risk_sf
    median_sf = model.median_sf
    print("Model and curves loaded successfully")
except Exception as e:
    print(f"Failed to load model or curves: {str(e)}")
    raise

# Define the column names that match the training data
feature_columns = [
    "438120",  # Opioid Dependence (Diagnosis)
    "938268",  # Limb Swelling (Diagnosis)
    "986417",  # Polyethylene Glycol-based Laxative
    "1124957",  # Oxycodone Extended Release
    "1125315",  # Acetaminophen
    "chronic_pain",  # Chronic Pain
    "liver_disease",  # Liver Disease
    "age_at_drug_start",  # Age at BUP-NAL Initiation
    "4145308",  # 12-Lead ECG
    "1129625",  # Diphenhydramine
    "941258",  # Docusate
    "4336384",  # Opioid Withdrawal (Diagnosis)
    "1112807",  # Aspirin
    "major_depression",  # Major Depression
    "1133201",  # Buprenorphine (Low Dose)
]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Get the JSON data from the POST request
        data = request.get_json()
        features = data["features"]

        # Convert features to a DataFrame for compatibility with the pipeline
        features_df = pd.DataFrame([features], columns=feature_columns)

        # Predict survival function (survival probabilities over time)
        survival_function = model.predict_survival_function(features_df)[0]

        # Rest of your prediction code remains the same...
        time_points = np.linspace(0, 180, num=180)
        survival_probabilities = survival_function(time_points)

        fig = go.Figure()
        # ... (rest of your plotting code remains the same)

        graphJSON = pio.to_json(fig)
        return jsonify(graphJSON=graphJSON)
    
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "localhost")
    port = int(os.getenv("PORT", 5000))
    app.run(host=host, port=port, debug=True)
