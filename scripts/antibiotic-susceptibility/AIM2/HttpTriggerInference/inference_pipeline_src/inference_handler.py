"""
Antibiotic Susceptibility Inference Handler

Main orchestration module that provides the entry point for susceptibility predictions.
Takes a patient FHIR ID, fetches all required data from FHIR APIs, performs feature
engineering, and returns antibiotic susceptibility scores.

Usage:
    from HttpTriggerInference.inference_pipeline_src.inference_handler import get_susceptibility_scores
    
    scores = get_susceptibility_scores(
        patient_fhir_id="abc123",
        credentials={"username": "...", "password": "..."}
    )
    # Returns: {'ciprofloxacin': 0.85, 'ceftriaxone': 0.72, ...}
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from requests.auth import HTTPBasicAuth

from .feature_engineering import FeatureEngineer
from .model_inference import AntibioticModelInference

logger = logging.getLogger(__name__)


class FHIRClient:
    """
    FHIR API client for fetching patient data from Epic.
    Handles authentication and common request patterns.
    """
    
    def __init__(
        self,
        api_prefix: Optional[str] = None,
        client_id: Optional[str] = None,
        credentials: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the FHIR client.
        
        Args:
            api_prefix: Epic FHIR API base URL
            client_id: Epic Client ID for API calls
            credentials: Dict with 'username' and 'password' for authentication
        """
        self.api_prefix = api_prefix or os.environ.get('EPIC_ENV', '')
        self.client_id = client_id or os.environ.get('EPIC_CLIENT_ID', '')
        self.credentials = credentials or {
            'username': os.environ.get('secretID', ''),
            'password': os.environ.get('secretpass', ''),
        }
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict] = None,
        timeout: int = 30
    ) -> Dict:
        """Make an authenticated GET request to the FHIR API."""
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
            logger.error(f"FHIR API error: {response.status_code} - {response.text[:200]}")
            raise Exception(f"FHIR API error: {response.status_code}")
        
        return response.json()
    
    def get_patient(self, patient_fhir_id: str) -> Dict[str, Any]:
        """
        Fetch patient demographics from FHIR Patient resource.
        
        Args:
            patient_fhir_id: The patient's FHIR R4 ID
            
        Returns:
            Dict containing patient data with keys: FHIR, gender, DOB, identifiers
        """
        endpoint = f"api/FHIR/R4/Patient/{patient_fhir_id}"
        data = self._make_request(endpoint)
        
        # Extract relevant fields
        patient_data = {
            'FHIR': patient_fhir_id,
            'gender': self._extract_gender(data),
            'DOB': data.get('birthDate'),
        }
        
        # Extract additional identifiers (FHIR STU3, MRN, etc.)
        for identifier in data.get('identifier', []):
            id_type = identifier.get('type', {}).get('text', '')
            id_value = identifier.get('value', '')
            
            if id_type == 'FHIR STU3':
                patient_data['FHIR STU3'] = id_value
            elif id_type == 'INTERNAL' or id_type == 'EXTERNAL':
                patient_data['MRN'] = id_value.strip()
        
        return patient_data
    
    def _extract_gender(self, patient_data: Dict) -> int:
        """Extract and encode gender from patient resource (0=female, 1=male)."""
        gender = patient_data.get('gender', '').lower()
        
        if gender in ['male', 'm']:
            return 1
        elif gender in ['female', 'f']:
            return 0
        
        # Try to get from extensions if not in main field
        for ext in patient_data.get('extension', []):
            if 'legal-sex' in ext.get('url', '') or 'birthsex' in ext.get('url', ''):
                code = ext.get('valueCode', '') or ''
                value_concept = ext.get('valueCodeableConcept', {})
                
                if code.upper() == 'M' or 'male' in str(value_concept).lower():
                    return 1
                elif code.upper() == 'F' or 'female' in str(value_concept).lower():
                    return 0
        
        # Default to 0 if unknown
        logger.warning(f"Could not determine gender, defaulting to 0")
        return 0
    
    # NOTE: Encounter fetching is no longer used.
    # Pipeline assumes all patients are inpatients (hosp_ward_IP=1).
    # Hospital ward features are hardcoded in feature_engineering.py.
    # TODO: If ER status is needed in the future, find the appropriate FHIR endpoint.
    
    def get_procedures(
        self, 
        patient_fhir_id: str, 
        days_back: int = 180,
        include_surgical: bool = True
    ) -> List[Dict]:
        """
        Fetch procedures from the last N days.
        
        Args:
            patient_fhir_id: The patient's FHIR R4 ID
            days_back: Number of days to look back
            include_surgical: Whether to also fetch surgical procedures
            
        Returns:
            List of procedure resources
        """
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        procedures = []
        
        # Fetch ordered procedures
        try:
            endpoint = "api/FHIR/R4/Procedure"
            params = {
                "patient": patient_fhir_id,
                "date": f"ge{cutoff_date}",
            }
            data = self._make_request(endpoint, params, timeout=60)
            
            for entry in data.get('entry', []):
                procedures.append(entry.get('resource', {}))
                
        except Exception as e:
            logger.warning(f"Error fetching procedures: {e}")
        
        # Fetch surgical procedures (category=387713003)
        if include_surgical:
            try:
                params = {
                    "patient": patient_fhir_id,
                    "category": "387713003",
                    "date": f"ge{cutoff_date}",
                }
                data = self._make_request(endpoint, params, timeout=60)
                
                for entry in data.get('entry', []):
                    procedures.append(entry.get('resource', {}))
                    
            except Exception as e:
                logger.warning(f"Error fetching surgical procedures: {e}")
        
        return procedures


def get_susceptibility_scores(
    patient_fhir_id: str,
    credentials: Optional[Dict[str, str]] = None,
    api_prefix: Optional[str] = None,
    client_id: Optional[str] = None,
    model_dir: Optional[str] = None,
) -> Dict[str, float]:
    """
    Main entry point: Get antibiotic susceptibility scores for a patient.
    
    This function orchestrates the full inference pipeline:
    1. Fetches patient data from FHIR APIs
    2. Constructs patient_data dictionary
    3. Generates feature vector via FeatureEngineer
    4. Runs inference on all antibiotic models
    5. Returns susceptibility scores
    
    Args:
        patient_fhir_id: The patient's FHIR R4 ID
        credentials: Optional dict with 'username' and 'password'
        api_prefix: Optional Epic FHIR API base URL
        client_id: Optional Epic Client ID
        model_dir: Optional path to model files directory
        
    Returns:
        Dict mapping antibiotic name to susceptibility score (0.0 to 1.0)
        e.g., {'ciprofloxacin': 0.85, 'ceftriaxone': 0.72, ...}
    """
    logger.info(f"Starting susceptibility inference for patient: {patient_fhir_id}")
    
    # Initialize FHIR client
    fhir_client = FHIRClient(
        api_prefix=api_prefix,
        client_id=client_id,
        credentials=credentials,
    )
    
    # Step 1: Fetch patient demographics
    logger.info("Fetching patient data...")
    patient_data = fhir_client.get_patient(patient_fhir_id)
    logger.info(f"Patient data retrieved: DOB={patient_data.get('DOB')}, gender={patient_data.get('gender')}")
    
    # NOTE: Encounter fetching skipped - pipeline assumes inpatient (hosp_ward_IP=1)
    # Hospital ward features are hardcoded in feature_engineering.py
    
    # Step 2: Fetch procedures
    logger.info("Fetching procedure data...")
    procedures = fhir_client.get_procedures(patient_fhir_id)
    patient_data['procedures'] = procedures
    logger.info(f"Found {len(procedures)} procedures")
    
    # Step 4: Initialize feature engineer and generate features
    logger.info("Generating feature vector...")
    feature_engineer = FeatureEngineer(
        patient_data=patient_data,
        credentials=credentials or fhir_client.credentials,
        api_prefix=api_prefix or fhir_client.api_prefix,
        client_id=client_id or fhir_client.client_id,
    )
    
    feature_df = feature_engineer.generate_features()
    logger.info(f"Generated {len(feature_df.columns)} features")
    
    # Step 5: Initialize model inference and predict
    logger.info("Running model inference...")
    if model_dir is None:
        # Default to models directory relative to this file
        model_dir = os.path.join(os.path.dirname(__file__), "models")
    
    inference = AntibioticModelInference(model_dir=model_dir)
    scores = inference.predict(feature_df)
    
    logger.info(f"Inference complete. Scores: {scores}")
    return scores


def get_susceptibility_scores_with_details(
    patient_fhir_id: str,
    credentials: Optional[Dict[str, str]] = None,
    api_prefix: Optional[str] = None,
    client_id: Optional[str] = None,
    model_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Extended version that returns scores along with feature data for debugging.
    
    Returns:
        Dict with 'scores', 'features', and 'patient_data' keys
    """
    logger.info(f"Starting susceptibility inference for patient: {patient_fhir_id}")
    
    # Initialize FHIR client
    fhir_client = FHIRClient(
        api_prefix=api_prefix,
        client_id=client_id,
        credentials=credentials,
    )
    
    # Fetch patient and procedure data
    # NOTE: Encounter fetching skipped - pipeline assumes inpatient (hosp_ward_IP=1)
    patient_data = fhir_client.get_patient(patient_fhir_id)
    procedures = fhir_client.get_procedures(patient_fhir_id)
    patient_data['procedures'] = procedures
    
    # Generate features
    feature_engineer = FeatureEngineer(
        patient_data=patient_data,
        credentials=credentials or fhir_client.credentials,
        api_prefix=api_prefix or fhir_client.api_prefix,
        client_id=client_id or fhir_client.client_id,
    )
    
    feature_df = feature_engineer.generate_features()
    
    # Run inference
    if model_dir is None:
        model_dir = os.path.join(os.path.dirname(__file__), "models")
    
    inference = AntibioticModelInference(model_dir=model_dir)
    scores = inference.predict(feature_df)
    
    return {
        'scores': scores,
        'features': feature_df.to_dict(orient='records')[0],
        'patient_data': {
            'fhir_id': patient_fhir_id,
            'gender': patient_data.get('gender'),
            'dob': patient_data.get('DOB'),
            'encounter_class': 'Inpatient (hardcoded)',  # Pipeline assumes inpatient
            'procedure_count': len(procedures),
        }
    }

