"""
inference_pipeline_src - Antibiotic Susceptibility Model Inference Module

This module provides a decoupled architecture for antibiotic susceptibility prediction:
- Feature engineering produces a superset of all possible features
- Each model specifies which features it requires via metadata in the .pkl file
- Models can be updated independently without breaking the pipeline

Usage (end-to-end inference with patient ID):
    from HttpTriggerInference.inference_pipeline_src import get_susceptibility_scores
    
    scores = get_susceptibility_scores(
        patient_fhir_id="abc123",
        credentials={"username": "...", "password": "..."}
    )
    # Returns: {'ciprofloxacin': 0.85, 'ceftriaxone': 0.72, ...}

Usage (with pre-fetched patient data):
    from HttpTriggerInference.inference_pipeline_src import FeatureEngineer, AntibioticModelInference
    
    # Generate features
    fe = FeatureEngineer(patient_data=patient_dict, credentials=creds)
    feature_df = fe.generate_features()
    
    # Load models and predict
    inference = AntibioticModelInference(model_dir="path/to/models")
    scores = inference.predict(feature_df)
"""

from .model_inference import AntibioticModelInference
from .feature_engineering import FeatureEngineer
from .inference_handler import (
    FHIRClient,
    get_susceptibility_scores,
    get_susceptibility_scores_with_details,
)

__all__ = [
    'AntibioticModelInference',
    'FeatureEngineer',
    'FHIRClient',
    'get_susceptibility_scores',
    'get_susceptibility_scores_with_details',
]
