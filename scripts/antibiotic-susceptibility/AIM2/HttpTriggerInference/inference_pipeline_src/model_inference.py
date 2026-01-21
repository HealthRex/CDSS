"""
Antibiotic Model Inference Module

This module provides a unified interface for loading and running antibiotic
susceptibility prediction models. Each antibiotic has its own .pkl model file
containing the trained model and metadata about expected features.

Architecture:
- Each .pkl file contains: {'model': model_obj, 'expected_features': [...], 'metadata': {...}}
- Models are loaded on initialization
- Feature validation ensures required features are present
- Only required features are selected for each model's prediction
"""

import os
import pickle
import logging
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import numpy as np

# Try to import joblib for loading models saved with joblib
try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False

logger = logging.getLogger(__name__)


class AntibioticModelInference:
    """
    Multi-antibiotic model inference class.
    
    Loads multiple antibiotic models from separate .pkl files and provides
    a unified prediction interface. Each model specifies its required features,
    enabling feature engineering to evolve independently.
    
    Attributes:
        models: Dict mapping antibiotic name to model object
        expected_features: Dict mapping antibiotic name to list of required feature names
        metadata: Dict mapping antibiotic name to model metadata
    """
    
    # Default list of antibiotics to load if none specified
    DEFAULT_ANTIBIOTICS = [
        'amoxicillin_clavulanic_acid',
        'ceftriaxone',
        'ciprofloxacin',
        'doxycycline',
        'nitrofurantoin',
    ]
    
    def __init__(
        self,
        model_dir: str,
        antibiotics: Optional[List[str]] = None,
        credentials: Optional[Dict[str, str]] = None,
        databricks_endpoint: Optional[str] = None,
    ):
        """
        Initialize the antibiotic model inference engine.
        
        Args:
            model_dir: Path to directory containing .pkl model files.
                       Each file should be named {antibiotic}.pkl
            antibiotics: List of antibiotic names to load. If None, loads DEFAULT_ANTIBIOTICS.
            credentials: Optional credentials dict for Databricks endpoint.
            databricks_endpoint: Optional Databricks endpoint URL. If provided,
                                predictions will be fetched from Databricks instead of local models.
        """
        self.model_dir = model_dir
        self.antibiotics = antibiotics or self.DEFAULT_ANTIBIOTICS
        self.credentials = credentials
        self.databricks_endpoint = databricks_endpoint
        
        # Storage for loaded models and their metadata
        self.models: Dict[str, Any] = {}
        self.expected_features: Dict[str, List[str]] = {}
        self.metadata: Dict[str, Dict] = {}
        
        # Load models from local .pkl files (skip if using Databricks)
        if self.databricks_endpoint is None:
            self._load_models()
        else:
            logger.info(f"Using Databricks endpoint: {databricks_endpoint}")
    
    def _load_models(self) -> None:
        """Load all antibiotic models from .pkl files."""
        for antibiotic in self.antibiotics:
            pkl_path = os.path.join(self.model_dir, f"{antibiotic}.pkl")
            
            if not os.path.exists(pkl_path):
                logger.warning(f"Model file not found: {pkl_path}")
                continue
            
            try:
                model_dict = self._load_pickle(pkl_path)
                
                # Extract components from the pickle
                self.models[antibiotic] = model_dict.get('model')
                self.expected_features[antibiotic] = model_dict.get('expected_features', [])
                self.metadata[antibiotic] = model_dict.get('metadata', {})
                
                logger.info(
                    f"Loaded model for {antibiotic}: "
                    f"{len(self.expected_features[antibiotic])} features"
                )
                
            except Exception as e:
                logger.error(f"Failed to load model for {antibiotic}: {e}")
                raise
    
    def _load_pickle(self, path: str) -> Dict[str, Any]:
        """
        Load a pickle file, trying both standard pickle and joblib.
        
        Args:
            path: Path to the pickle file
            
        Returns:
            Loaded dictionary
        """
        # Try standard pickle first
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception as pickle_error:
            # Try joblib if available
            if HAS_JOBLIB:
                try:
                    return joblib.load(path)
                except Exception as joblib_error:
                    logger.error(f"Failed to load with pickle: {pickle_error}")
                    logger.error(f"Failed to load with joblib: {joblib_error}")
                    raise
            else:
                raise pickle_error
    
    def _validate_features(
        self, 
        feature_df: pd.DataFrame, 
        antibiotic: str
    ) -> None:
        """
        Validate that all required features for a model are present.
        
        Args:
            feature_df: DataFrame containing features
            antibiotic: Name of the antibiotic model
            
        Raises:
            ValueError: If required features are missing
        """
        required = set(self.expected_features.get(antibiotic, []))
        available = set(feature_df.columns)
        missing = required - available
        
        if missing:
            raise ValueError(
                f"Model '{antibiotic}' is missing required features: {sorted(missing)}"
            )
    
    def _select_features(
        self, 
        feature_df: pd.DataFrame, 
        antibiotic: str
    ) -> pd.DataFrame:
        """
        Select only the features required by a specific model.
        
        Args:
            feature_df: DataFrame containing all features (superset)
            antibiotic: Name of the antibiotic model
            
        Returns:
            DataFrame with only the required features in correct order
        """
        required_features = self.expected_features.get(antibiotic, [])
        
        if not required_features:
            logger.warning(
                f"No expected_features defined for {antibiotic}, using all columns"
            )
            return feature_df
        
        return feature_df[required_features]
    
    def predict(
        self, 
        feature_df: pd.DataFrame,
        antibiotics: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Generate susceptibility predictions for all loaded antibiotics.
        
        Args:
            feature_df: DataFrame containing patient features (superset of all possible features)
            antibiotics: Optional list of specific antibiotics to predict. 
                        If None, predicts for all loaded models.
            
        Returns:
            Dict mapping antibiotic name to susceptibility score (probability)
        """
        if self.databricks_endpoint is not None:
            return self._predict_from_databricks(feature_df)
        
        return self._predict_local(feature_df, antibiotics)
    
    def _predict_local(
        self, 
        feature_df: pd.DataFrame,
        antibiotics: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Generate predictions using locally loaded models.
        
        Args:
            feature_df: DataFrame containing patient features
            antibiotics: Optional list of specific antibiotics to predict
            
        Returns:
            Dict mapping antibiotic name to susceptibility score
        """
        target_antibiotics = antibiotics or list(self.models.keys())
        predictions = {}
        
        for antibiotic in target_antibiotics:
            if antibiotic not in self.models:
                logger.warning(f"No model loaded for {antibiotic}, skipping")
                continue
            
            try:
                # Validate and select features
                self._validate_features(feature_df, antibiotic)
                selected_features = self._select_features(feature_df, antibiotic)
                # Get model and make prediction
                model = self.models[antibiotic]
                
                # Support different model interfaces
                if hasattr(model, 'predict_proba'):
                    # sklearn-style model
                    proba = model.predict_proba(selected_features)
                    # Assume binary classification, take probability of positive class
                    score = float(proba[0, 1]) if proba.ndim > 1 else float(proba[0])
                elif hasattr(model, 'pred_dist'):
                    # Custom model with pred_dist method (like existing EmpricABX)
                    result = model.pred_dist(selected_features)
                    # Handle dict return format
                    if isinstance(result, dict):
                        key = f'label_empiric_{antibiotic}'
                        score = float(result.get(key, result.get(antibiotic, 0.0)))
                    else:
                        score = float(result)
                elif hasattr(model, 'predict'):
                    # Basic predict method
                    score = float(model.predict(selected_features)[0])
                else:
                    raise ValueError(
                        f"Model for {antibiotic} has no supported prediction method"
                    )
                
                predictions[antibiotic] = score
                
            except Exception as e:
                logger.error(f"Prediction failed for {antibiotic}: {e}")
                predictions[antibiotic] = None
        
        return predictions
    
    def _predict_from_databricks(
        self, 
        feature_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Placeholder for Databricks endpoint prediction.
        
        TODO: Implement actual Databricks API call when endpoint is ready.
        
        Args:
            feature_df: DataFrame containing patient features
            
        Returns:
            Dict mapping antibiotic name to susceptibility score
        """
        # PLACEHOLDER: Implement Databricks API call
        # 
        # Example implementation:
        # import requests
        # 
        # response = requests.post(
        #     self.databricks_endpoint,
        #     headers={
        #         "Content-Type": "application/json",
        #         "Authorization": f"Bearer {self.credentials.get('password', '')}",
        #     },
        #     json={"data": feature_df.to_dict(orient='records')},
        # )
        # 
        # if response.status_code != 200:
        #     raise Exception(f"Databricks request failed: {response.text}")
        # 
        # return response.json()["predictions"]
        
        raise NotImplementedError(
            "Databricks endpoint prediction not yet implemented. "
            "Please use local model inference by not providing databricks_endpoint."
        )
    
    def get_model_info(self, antibiotic: str) -> Dict[str, Any]:
        """
        Get information about a specific antibiotic model.
        
        Args:
            antibiotic: Name of the antibiotic
            
        Returns:
            Dict containing model metadata and expected features
        """
        return {
            'antibiotic': antibiotic,
            'loaded': antibiotic in self.models,
            'expected_features': self.expected_features.get(antibiotic, []),
            'num_features': len(self.expected_features.get(antibiotic, [])),
            'metadata': self.metadata.get(antibiotic, {}),
        }
    
    def list_loaded_models(self) -> List[str]:
        """Return list of successfully loaded antibiotic models."""
        return list(self.models.keys())
    
    def __repr__(self) -> str:
        return (
            f"AntibioticModelInference("
            f"model_dir='{self.model_dir}', "
            f"loaded_models={list(self.models.keys())})"
        )
