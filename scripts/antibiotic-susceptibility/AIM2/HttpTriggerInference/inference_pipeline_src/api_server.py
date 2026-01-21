"""
Local development server for antibiotic susceptibility inference.

Run with:
    cd AIM2 && source env_vars.sh && python HttpTriggerInference/inference_pipeline_src/api_server.py

Endpoints:
    GET  /health              - Health check
    POST /predict             - Get susceptibility scores
    POST /predict/details     - Get scores with feature details

Example:
    curl -X POST http://localhost:8000/predict \
      -H "Content-Type: application/json" \
      -d '{"patient_id": "5003122495"}'
"""
import os
import sys
import logging
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Add paths for imports
_this_dir = os.path.dirname(os.path.abspath(__file__))
_http_trigger_dir = os.path.dirname(_this_dir)
_aim2_dir = os.path.dirname(_http_trigger_dir)
sys.path.insert(0, _this_dir)

from feature_engineering import FeatureEngineer
from model_inference import AntibioticModelInference

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Antibiotic Susceptibility API",
    description="Predicts antibiotic susceptibility scores for patients based on FHIR data",
    version="1.0.0"
)

# ============================================================================
# Request/Response Models
# ============================================================================

class PredictRequest(BaseModel):
    """Request model for prediction endpoints."""
    patient_id: str  # Required: FHIR ID or MRN
    
    # Optional lookback parameters (with defaults)
    vitals_lookback_hours: Optional[int] = 48
    procedures_lookback_days: Optional[int] = 180
    abx_lookback_days: Optional[int] = 180
    resistance_lookback_days: Optional[int] = 180
    
    # Optional feature flags
    include_vitals: Optional[bool] = True
    include_antibiotics: Optional[bool] = True
    include_prior_resistance: Optional[bool] = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "5003122495",
                "vitals_lookback_hours": 48,
                "procedures_lookback_days": 180,
                "abx_lookback_days": 180,
                "resistance_lookback_days": 180,
                "include_vitals": True,
                "include_antibiotics": True,
                "include_prior_resistance": True
            }
        }
    
class PredictResponse(BaseModel):
    patient_id: str
    scores: Dict[str, Optional[float]]
    
class PredictDetailsResponse(BaseModel):
    patient_id: str
    scores: Dict[str, Optional[float]]
    features: Dict[str, Any]
    patient_data: Dict[str, Any]
    parameters_used: Dict[str, Any]  # Show what parameters were used

class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str

# ============================================================================
# FHIR Client
# ============================================================================

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

class FHIRClient:
    """FHIR API client for fetching patient data from Epic."""
    
    def __init__(self):
        self.api_prefix = os.environ.get('EPIC_ENV', '')
        self.client_id = os.environ.get('EPIC_CLIENT_ID', '')
        self.credentials = {
            'username': os.environ.get('secretID', ''),
            'password': os.environ.get('secretpass', ''),
        }
        
        if not self.api_prefix:
            logger.warning("EPIC_ENV not set - FHIR calls will fail")
    
    def _make_request(self, endpoint: str, params: dict = None, timeout: int = 30) -> dict:
        """Make authenticated request to FHIR API."""
        url = f"{self.api_prefix}{endpoint}"
        response = requests.get(
            url, 
            params=params,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "Epic-Client-ID": self.client_id,
            },
            auth=HTTPBasicAuth(
                self.credentials.get("username", ""),
                self.credentials.get("password", ""),
            ),
            timeout=timeout,
        )
        if response.status_code != 200:
            raise Exception(f"FHIR API error: {response.status_code} - {response.text[:200]}")
        return response.json()
    
    def get_patient(self, patient_id: str) -> tuple:
        """
        Get patient data. Accepts either FHIR ID or MRN.
        
        Returns:
            Tuple of (patient_data dict, patient_fhir_id)
        """
        logger.info(f"Fetching patient: {patient_id}")
        
        if patient_id.isdigit():
            # Search by MRN
            logger.info(f"Searching by MRN: {patient_id}")
            data = self._make_request("api/FHIR/R4/Patient", {"identifier": patient_id})
            entries = data.get('entry', [])
            if not entries:
                raise Exception(f"No patient found with MRN: {patient_id}")
            patient_fhir_id = entries[0].get('resource', {}).get('id')
            resource = entries[0].get('resource', {})
            logger.info(f"Found FHIR ID: {patient_fhir_id}")
        else:
            # Direct FHIR ID lookup
            patient_fhir_id = patient_id
            resource = self._make_request(f"api/FHIR/R4/Patient/{patient_fhir_id}")
        
        gender = 1 if resource.get('gender', '').lower() in ['male', 'm'] else 0
        
        patient_data = {
            'FHIR': patient_fhir_id,
            'gender': gender,
            'DOB': resource.get('birthDate'),
        }
        
        logger.info(f"Patient data: gender={gender}, DOB={patient_data['DOB']}")
        return patient_data, patient_fhir_id
    
    def get_procedures(self, patient_fhir_id: str, days_back: int = 180) -> list:
        """Fetch procedures from the last N days."""
        cutoff = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        try:
            data = self._make_request(
                "api/FHIR/R4/Procedure", 
                {"patient": patient_fhir_id, "date": f"ge{cutoff}"}, 
                timeout=60
            )
            procedures = [e.get('resource', {}) for e in data.get('entry', [])]
            return procedures
        except Exception as e:
            logger.warning(f"Error fetching procedures: {e}")
            return []

# ============================================================================
# Core Inference Logic
# ============================================================================

def log_inference_results(patient_id: str, result: dict) -> None:
    """Log inference results in a readable format (similar to test_inference.py)."""
    print("\n" + "=" * 60)
    print("ANTIBIOTIC SUSCEPTIBILITY INFERENCE")
    print("=" * 60)
    print(f"\nPatient ID: {patient_id}")
    print("-" * 60)
    
    # Patient info
    print("\n✓ PATIENT INFO")
    print("-" * 40)
    for k, v in result['patient_data'].items():
        print(f"  {k}: {v}")
    
    # Features
    print("\n✓ FEATURES GENERATED")
    print("-" * 40)
    features = result['features']
    print(f"  Total features: {len(features)}")
    print("\n  Feature values:")
    for name, value in sorted(features.items()):
        if isinstance(value, float):
            print(f"    {name}: {value:.4f}")
        else:
            print(f"    {name}: {value}")
    
    # Scores
    print("\n✓ SUSCEPTIBILITY SCORES")
    print("-" * 40)
    for antibiotic, score in sorted(result['scores'].items()):
        if score is not None:
            bar_length = int(score * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"  {antibiotic:30s} {bar} {score:.1%}\n")
        else:
            print(f"  {antibiotic:30s} [FAILED - missing features]")
    
    print("\n" + "=" * 60)
    print("INFERENCE COMPLETE")
    print("=" * 60 + "\n")


def run_inference(
    patient_id: str,
    vitals_lookback_hours: int = 48,
    procedures_lookback_days: int = 180,
    abx_lookback_days: int = 180,
    resistance_lookback_days: int = 180,
    include_vitals: bool = True,
    include_antibiotics: bool = True,
    include_prior_resistance: bool = True,
    log_details: bool = False
) -> dict:
    """
    Run the full inference pipeline for a patient.
    
    Args:
        patient_id: Patient FHIR ID or MRN
        vitals_lookback_hours: Hours to look back for vital signs (default: 48)
        procedures_lookback_days: Days to look back for procedures (default: 180)
        abx_lookback_days: Days to look back for prior antibiotics (default: 180)
        resistance_lookback_days: Days to look back for prior resistance (default: 180)
        include_vitals: Whether to include vital sign features (default: True)
        include_antibiotics: Whether to include prior antibiotic features (default: True)
        include_prior_resistance: Whether to include prior resistance features (default: True)
        log_details: If True, log detailed results to console
        
    Returns:
        Dict with 'scores', 'features', 'patient_data', and 'parameters_used'
    """
    # Store parameters for response
    parameters_used = {
        'vitals_lookback_hours': vitals_lookback_hours,
        'procedures_lookback_days': procedures_lookback_days,
        'abx_lookback_days': abx_lookback_days,
        'resistance_lookback_days': resistance_lookback_days,
        'include_vitals': include_vitals,
        'include_antibiotics': include_antibiotics,
        'include_prior_resistance': include_prior_resistance,
    }
    
    logger.info(f"Running inference with parameters: {parameters_used}")
    
    fhir_client = FHIRClient()
    
    # Fetch patient data
    patient_data, patient_fhir_id = fhir_client.get_patient(patient_id)
    
    # Fetch procedures with configurable lookback
    procedures = fhir_client.get_procedures(patient_fhir_id, days_back=procedures_lookback_days)
    patient_data['procedures'] = procedures
    
    # Generate features with configurable parameters
    logger.info("Generating features...")
    fe = FeatureEngineer(
        patient_data=patient_data,
        credentials=fhir_client.credentials,
        api_prefix=fhir_client.api_prefix,
        client_id=fhir_client.client_id,
    )
    feature_df = fe.generate_features(
        include_vitals=include_vitals,
        include_antibiotics=include_antibiotics,
        include_prior_resistance=include_prior_resistance,
        vitals_lookback_hours=vitals_lookback_hours,
        abx_lookback_days=abx_lookback_days,
        resistance_lookback_days=resistance_lookback_days,
    )
    logger.info(f"Generated {len(feature_df.columns)} features")
    
    # Run model inference
    logger.info("Running model inference...")
    model_dir = os.path.join(_this_dir, "models")
    inference = AntibioticModelInference(model_dir=model_dir)
    scores = inference.predict(feature_df)
    
    result = {
        'scores': scores,
        'features': feature_df.to_dict(orient='records')[0],
        'patient_data': {
            'fhir_id': patient_fhir_id,
            'gender': patient_data.get('gender'),
            'dob': patient_data.get('DOB')
        },
        'parameters_used': parameters_used,
    }
    
    # Log detailed results if requested
    if log_details:
        log_inference_results(patient_id, result)
    else:
        # Just log the scores summary
        logger.info(f"Scores: {scores}")
    
    return result

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    env = os.environ.get('EPIC_ENV', 'not set')
    env_name = 'production' if 'background' in env.lower() else 'test' if 'test' in env.lower() else 'unknown'
    return HealthResponse(
        status="healthy",
        service="antibiotic-susceptibility",
        environment=env_name
    )

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """
    Get susceptibility scores for a patient.
    
    Args:
        request: JSON body with:
            - patient_id (required): FHIR ID or MRN
            - vitals_lookback_hours (optional): Hours to look back for vitals (default: 48)
            - procedures_lookback_days (optional): Days to look back for procedures (default: 180)
            - abx_lookback_days (optional): Days to look back for antibiotics (default: 180)
            - resistance_lookback_days (optional): Days to look back for resistance (default: 180)
            - include_vitals (optional): Include vital features (default: True)
            - include_antibiotics (optional): Include antibiotic features (default: True)
            - include_prior_resistance (optional): Include resistance features (default: True)
        
    Returns:
        Susceptibility scores for each antibiotic (0.0 to 1.0)
    """
    try:
        logger.info(f"Predict request for patient: {request.patient_id}")
        result = run_inference(
            patient_id=request.patient_id,
            vitals_lookback_hours=request.vitals_lookback_hours,
            procedures_lookback_days=request.procedures_lookback_days,
            abx_lookback_days=request.abx_lookback_days,
            resistance_lookback_days=request.resistance_lookback_days,
            include_vitals=request.include_vitals,
            include_antibiotics=request.include_antibiotics,
            include_prior_resistance=request.include_prior_resistance,
            log_details=True
        )
        return PredictResponse(
            patient_id=request.patient_id,
            scores=result['scores']
        )
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/details", response_model=PredictDetailsResponse)
def predict_with_details(request: PredictRequest):
    """
    Get susceptibility scores with full feature details.
    
    Args:
        request: JSON body with:
            - patient_id (required): FHIR ID or MRN
            - vitals_lookback_hours (optional): Hours to look back for vitals (default: 48)
            - procedures_lookback_days (optional): Days to look back for procedures (default: 180)
            - abx_lookback_days (optional): Days to look back for antibiotics (default: 180)
            - resistance_lookback_days (optional): Days to look back for resistance (default: 180)
            - include_vitals (optional): Include vital features (default: True)
            - include_antibiotics (optional): Include antibiotic features (default: True)
            - include_prior_resistance (optional): Include resistance features (default: True)
        
    Returns:
        Scores, feature vector, patient metadata, and parameters used
    """
    try:
        logger.info(f"Predict (details) request for patient: {request.patient_id}")
        result = run_inference(
            patient_id=request.patient_id,
            vitals_lookback_hours=request.vitals_lookback_hours,
            procedures_lookback_days=request.procedures_lookback_days,
            abx_lookback_days=request.abx_lookback_days,
            resistance_lookback_days=request.resistance_lookback_days,
            include_vitals=request.include_vitals,
            include_antibiotics=request.include_antibiotics,
            include_prior_resistance=request.include_prior_resistance,
            log_details=True
        )
        return PredictDetailsResponse(
            patient_id=request.patient_id,
            scores=result['scores'],
            features=result['features'],
            patient_data=result['patient_data'],
            parameters_used=result['parameters_used']
        )
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Start the development server."""
    print("=" * 60)
    print("ANTIBIOTIC SUSCEPTIBILITY API - Local Development Server")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()
