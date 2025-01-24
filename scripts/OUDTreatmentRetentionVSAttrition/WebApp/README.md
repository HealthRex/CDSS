# Buprenorphine-Naloxone Attrition Prediction Web App

## Overview
This web app predicts treatment retention probabilities for patients using Buprenorphine-Naloxone, leveraging machine learning models and interactive visualizations.

## Features
- Predict retention probabilities based on input features.
- Visualize patient-specific retention curves compared to high-risk, low-risk, and median reference curves.
- User-friendly interface with explanations for each input feature.

## Project Structure
- `app.py`: The main Flask backend for the app.
- `templates/index.html`: The frontend HTML for the web app.
- `static/style.css`: The CSS file for styling.
- `static/app.js`: JavaScript for frontend functionality.
- `rsf_model.pkl`: Pre-trained Random Survival Forest (RSF) machine learning model.
- `requirements.txt`: Python dependencies for the project.

## Requirements
- Python 3.8 or newer.
- Required Python packages are listed in `requirements.txt`.

## Installation
1. Clone the repository or extract the files.
2. Set up a Python virtual environment:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
3. Install the required dependencies:
   pip install -r requirements.txt


## Usage
1. Ensure the rsf_model.pkl file is present in the project directory.
2. Start the Flask app:
   python app.py
3. Open your web browser and navigate to http://127.0.0.1:5000.


