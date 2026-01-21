"""
End-to-end test for the antibiotic susceptibility inference pipeline.

This test makes real FHIR API calls and requires environment variables to be set.

Run with:
    cd AIM2 && source env_vars.sh && python3 HttpTriggerInference/inference_pipeline_src/tests/test_inference.py
"""
import os
from re import search
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directories to path for direct module imports
_this_dir = os.path.dirname(os.path.abspath(__file__))
_james_dir = os.path.dirname(_this_dir)
sys.path.insert(0, _james_dir)

# Import directly from module files (avoid HttpTriggerInference/__init__.py which has azure deps)
from feature_engineering import FeatureEngineer
from model_inference import AntibioticModelInference

# Re-implement the inference function inline to avoid relative import issues
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class FHIRClient:
    """FHIR API client for fetching patient data from Epic."""
    
    def __init__(self, api_prefix=None, client_id=None, credentials=None):
        self.api_prefix = api_prefix or os.environ.get('EPIC_ENV', '')
        self.client_id = client_id or os.environ.get('EPIC_CLIENT_ID', '')
        self.credentials = credentials or {
            'username': os.environ.get('secretID', ''),
            'password': os.environ.get('secretpass', ''),
        }
    
    def _make_request(self, endpoint, params=None, timeout=30):
        url = f"{self.api_prefix}{endpoint}"
        response = requests.get(
            url, params=params,
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
            raise Exception(f"FHIR API error: {response.status_code}")
        return response.json()
    
    def get_patient(self, patient_id):
        """Get patient data. Accepts either FHIR ID or MRN."""
        # If ID is numeric, it's likely an MRN - search first to get FHIR ID
        if patient_id.isdigit():
            logger.info(f"Searching for patient by MRN: {patient_id}")
            search_data = self._make_request("api/FHIR/R4/Patient", {"identifier": patient_id})
            entries = search_data.get('entry', [])
            if not entries:
                raise Exception(f"No patient found with MRN: {patient_id}")
            # Get the FHIR ID from the first result
            patient_fhir_id = entries[0].get('resource', {}).get('id')
            data = entries[0].get('resource', {})
            logger.info(f"Found FHIR ID: {patient_fhir_id}")
        else:
            # It's a FHIR ID, fetch directly
            patient_fhir_id = patient_id
            endpoint = f"api/FHIR/R4/Patient/{patient_fhir_id}"
            data = self._make_request(endpoint)
        
        gender_raw = data.get('gender', '').lower()
        gender = 1 if gender_raw in ['male', 'm'] else 0
        patient_data = {
            'FHIR': patient_fhir_id,
            'gender': gender,
            'DOB': data.get('birthDate'),
        }

        # for identifier in data.get('identifier', []):
        #     id_type = identifier.get('type', {}).get('text', '')
        #     if id_type == 'FHIR STU3':
        #         patient_data['FHIR STU3'] = identifier.get('value', '')
        #     elif id_type in ['INTERNAL', 'EXTERNAL']:
        #         patient_data['MRN'] = identifier.get('value', '').strip()

        return patient_data, patient_fhir_id
    
    # NOTE: Encounter fetching removed - pipeline assumes all patients are inpatients
    # Hospital ward features are hardcoded in feature_engineering.py:
    #   hosp_ward_IP = 1 (always inpatient)
    #   hosp_ward_OP = 0 
    #   hosp_ward_ER = 0 (TODO: find FHIR endpoint for ER status)
    
    def get_procedures(self, patient_fhir_id, days_back=180):
        """
        NOTE: No access to procedure endpoint response - The authenticated client's search request 
        applies to a sub-resource that the client is not authorized for. 
        Tried both category "order" (103693007) and "surgical" (387713003), neither has access to.
        API Documentation: order: https://fhir.epic.com/Specifications?api=976
                          surgical: https://fhir.epic.com/specifications?api=10042
        """
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        procedures = []
        try:
            data = self._make_request("api/FHIR/R4/Procedure", 
                {"patient": patient_fhir_id, 
                # "category": "103693007", 
                # "category": "387713003",
                "date": [f"ge{cutoff_date}", 
                f"lt{today}"]}, timeout=60)
            for entry in data.get('entry', []):
                procedures.append(entry.get('resource', {}))
        except Exception as e:
            print(f'error: ${e}')
            pass

        return procedures


def get_susceptibility_scores_with_details(patient_id, credentials=None, api_prefix=None, client_id=None, model_dir=None):
    """Get susceptibility scores with full details. Accepts FHIR ID or MRN."""
    fhir_client = FHIRClient(api_prefix=api_prefix, client_id=client_id, credentials=credentials)
    
    # Get patient data (handles both MRN and FHIR ID)
    patient_data, patient_fhir_id = fhir_client.get_patient(patient_id)
    
    # NOTE: Encounter fetching skipped - pipeline assumes inpatient (hosp_ward_IP=1)
    # Hospital ward features are hardcoded in feature_engineering.py

    procedures = fhir_client.get_procedures(patient_fhir_id)
    patient_data['procedures'] = procedures
    
    feature_engineer = FeatureEngineer(
        patient_data=patient_data,
        credentials=credentials or fhir_client.credentials,
        api_prefix=api_prefix or fhir_client.api_prefix,
        client_id=client_id or fhir_client.client_id,
    )
    feature_df = feature_engineer.generate_features()
    
    if model_dir is None:
        model_dir = os.path.join(_james_dir, "models")
    
    inference = AntibioticModelInference(model_dir=model_dir)
    scores = inference.predict(feature_df)
    
    return {
        'scores': scores,
        'features': feature_df.to_dict(orient='records')[0],
        'patient_data': {
            'fhir_id': patient_fhir_id,
            'gender': patient_data.get('gender'),
            'dob': patient_data.get('DOB'),
            'encounter_class': 'Inpatient (default)',  # Pipeline assumes inpatient
        }
    }


def test_full_pipeline(patient_id: str = None):
    """
    Test the complete inference flow with a real patient.
    
    Args:
        patient_id: Patient FHIR ID or MRN to test with. 
                   Defaults to EXAMPLE_MRN environment variable.
    """
    if patient_id is None:
        patient_id = os.environ.get('EXAMPLE_MRN')
    
    if not patient_id:
        print("ERROR: No patient ID provided.")
        print("Set EXAMPLE_MRN environment variable or pass patient_id argument.")
        return None
    
    credentials = {
        'username': os.environ.get('secretID'),
        'password': os.environ.get('secretpass'),
    }
    
    if not credentials['username'] or not credentials['password']:
        print("ERROR: Missing credentials.")
        print("Make sure to run: source env_vars.sh")
        return None
    
    print("=" * 60)
    print("ANTIBIOTIC SUSCEPTIBILITY INFERENCE - END-TO-END TEST")
    print("=" * 60)
    print(f"\nPatient ID: {patient_id}")
    print("-" * 60)
    
    try:
        result = get_susceptibility_scores_with_details(
            patient_id=patient_id,
            credentials=credentials,
        )
        
        print("\n✓ PATIENT INFO")
        print("-" * 40)
        for k, v in result['patient_data'].items():
            print(f"  {k}: {v}")
        
        print("\n✓ FEATURES GENERATED")
        print("-" * 40)
        features = result['features']
        print(f"  Total features: {len(features)}")
        print("\n  Feature values:")
        for name, value in sorted(features.items()):
            # Format the value nicely
            if isinstance(value, float):
                print(f"    {name}: {value:.4f}")
            else:
                print(f"    {name}: {value}")
        
        print("\n✓ SUSCEPTIBILITY SCORES")
        print("-" * 40)
        for antibiotic, score in sorted(result['scores'].items()):
            if score is not None:
                # Show as percentage with bar visualization
                bar_length = int(score * 20)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                print(f"  {antibiotic:30s} {bar} {score:.1%}\n")
            else:
                print(f"  {antibiotic:30s} [FAILED - missing features]")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE - SUCCESS")
        print("=" * 60)
        
        return result
        
    except Exception as e:
        logger.exception("Test failed with error")
        print(f"\n✗ TEST FAILED: {e}")
        return None


def main():
    """Main entry point for command-line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test antibiotic susceptibility inference pipeline"
    )
    parser.add_argument(
        "--patient-id",
        "-p",
        help="Patient FHIR ID to test with (defaults to EXAMPLE_MRN env var)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    result = test_full_pipeline(patient_id=args.patient_id)
    
    if result is None:
        sys.exit(1)


if __name__ == "__main__":
    main()
