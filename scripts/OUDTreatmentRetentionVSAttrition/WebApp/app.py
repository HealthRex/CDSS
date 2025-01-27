from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import urllib.request
import os




# Include the custom class definition
class SurvivalFunction:
    def __init__(self, x, y):
        self.x = x
        self.y = y


app = Flask(__name__)

# URL to the model file hosted on Google Drive
model_url = "https://drive.google.com/uc?id=1fLjbWxe0jSiYj9x5JpgLR3STFrzyXXou"
model_filename = "rsf_model.pkl"

# Check if the model file exists locally, otherwise download it
if not os.path.exists(model_filename):
    urllib.request.urlretrieve(model_url, model_filename)

# Load the trained RandomSurvivalForest model with additional curves
model = joblib.load(model_filename)

# Load the high-risk, low-risk, and median curves from the model
high_risk_sf = model.high_risk_sf
low_risk_sf = model.low_risk_sf
median_sf = model.median_sf

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
    # Get the JSON data from the POST request
    data = request.get_json()
    features = data["features"]

    # Convert features to a DataFrame for compatibility with the pipeline
    features_df = pd.DataFrame([features], columns=feature_columns)

    # Predict survival function (survival probabilities over time)
    survival_function = model.predict_survival_function(features_df)[0]

    # Define time points to evaluate the survival function at
    time_points = np.linspace(0, 180, num=180)  # Example: 1 year in days

    # Evaluate the survival function at the specified time points
    survival_probabilities = survival_function(time_points)

    # Create the survival plot using Plotly
    fig = go.Figure()

    # Add patient-specific survival curve
    fig.add_trace(
        go.Scatter(
            x=np.round(time_points),
            y=survival_probabilities,
            mode="lines+markers",
            name="Patient Prediction",
            line=dict(width=3, color="blue"),
            marker=dict(size=6),
            hovertemplate="Day: %{x}<br>Retention Probability: %{y:.2f}<extra></extra>",
        )
    )

    # Add high-risk curve
    fig.add_trace(
        go.Scatter(
            x=high_risk_sf.x,
            y=high_risk_sf.y,
            mode="lines",
            name="High Risk",
            line=dict(width=2, color="red", dash="dash"),
            hovertemplate="Day: %{x}<br>Retention Probability: %{y:.2f}<extra></extra>",
        )
    )

    # Add low-risk curve
    fig.add_trace(
        go.Scatter(
            x=low_risk_sf.x,
            y=low_risk_sf.y,
            mode="lines",
            name="Low Risk",
            line=dict(width=2, color="green", dash="dash"),
            hovertemplate="Day: %{x}<br>Retention Probability: %{y:.2f}<extra></extra>",
        )
    )

    # Add median curve
    fig.add_trace(
        go.Scatter(
            x=median_sf.x,
            y=median_sf.y,
            mode="lines",
            name="Median",
            line=dict(width=2, color="gray", dash="dot"),
            hovertemplate="Day: %{x}<br>Retention Probability: %{y:.2f}<extra></extra>",
        )
    )

    # Update layout
    fig.update_layout(
        xaxis_title="Time (Days in Treatment)",
        yaxis_title="Retention Probability",
        xaxis=dict(range=[0, 180]),  # Limit x-axis to 180 days
        template="plotly_white",
        hovermode="x",
        showlegend=True,
    )

    # Convert the Plotly figure to JSON for rendering in the frontend
    graphJSON = pio.to_json(fig)

    return jsonify(graphJSON=graphJSON)


if __name__ == "__main__":
    # This runs the app locally for development
    app.run(debug=True, port=5000)
else:
    # This exports the Flask app for Vercel
    app = app
