"""
Feature Engineering Module for Antibiotic Susceptibility Prediction

This module provides a modular, extensible feature engineering pipeline.
Each feature category (demographics, vitals, labs, etc.) is implemented as
a separate method, making it easy to update individual components.

Key Design Principles:
- Output is a DataFrame with named columns (not positional)
- Features are a superset of what any model might need
- Models select only the features they require via expected_features metadata
- Adding new features doesn't break existing models
"""

import collections
import json
import logging
import os
import pickle
import re
import string
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import pytz
import requests
import xmltodict
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Modular feature engineering for antibiotic susceptibility prediction.
    
    Generates a comprehensive feature DataFrame from patient data.
    Each feature category is handled by a separate method for easy updates.
    
    Usage:
        fe = FeatureEngineer(patient_data=patient_dict, credentials=creds)
        feature_df = fe.generate_features()
    """
    
    # Vital sign name mappings (FHIR name -> model feature name)
    VITAL_SIGN_MAP = {
        "Systolic blood pressure": "sysbp",
        "Diastolic blood pressure": "diasbp",
        "Temp": "temp",
        "Pulse": "heartrate",
        "Resp Rate": "resprate",
        "SpO2": "spo2",
        "Heart Rate": "heartrate",
    }
    
    # =========================================================================
    # EXPECTED FEATURE CONSTANTS - All features must be initialized to 0
    # =========================================================================
    
    # All vital sign features expected by models (25 features)
    VITAL_FEATURES = [
        'Q25_diasbp', 'Q25_heartrate', 'Q25_resprate', 'Q25_sysbp', 'Q25_temp',
        'Q75_diasbp', 'Q75_heartrate', 'Q75_resprate', 'Q75_sysbp', 'Q75_temp',
        'first_diasbp', 'first_heartrate', 'first_resprate', 'first_sysbp', 'first_temp',
        'last_diasbp', 'last_heartrate', 'last_resprate', 'last_sysbp', 'last_temp',
        'median_diasbp', 'median_heartrate', 'median_resprate', 'median_sysbp', 'median_temp',
    ]
    
    # All prior antibiotic class features expected by models (12 features)
    PRIOR_ABX_CLASS_FEATURES = [
        'prior_abx_class_Aminoglycoside',
        'prior_abx_class_Ansamycin',
        'prior_abx_class_Antitubercular',
        'prior_abx_class_Beta_Lactam',
        'prior_abx_class_Combination_Antibiotic',
        'prior_abx_class_Fluoroquinolone',
        'prior_abx_class_Fosfomycin',
        'prior_abx_class_Glycopeptide',
        'prior_abx_class_Macrolide_Lincosamide',
        'prior_abx_class_Nitrofuran',
        'prior_abx_class_Tetracycline',
        'prior_abx_class_Urinary_Antiseptic',
    ]
    
    # All prior infected organism features expected by models (11 features)
    PRIOR_INFECTED_FEATURES = [
        'prior_infected_Citrobacter',
        'prior_infected_CONS',
        'prior_infected_Enterobacter',
        'prior_infected_Enterococcus',
        'prior_infected_Escherichia',
        'prior_infected_Klebsiella',
        'prior_infected_Morganella',
        'prior_infected_Proteus',
        'prior_infected_Pseudomonas',
        'prior_infected_Serratia',
        'prior_infected_Streptococcus',
    ]
    
    # All prior medication features expected by models (7 features)
    PRIOR_MED_FEATURES = [
        'prior_med_Ampicillin',
        'prior_med_Cefazolin',
        'prior_med_Ceftriaxone',
        'prior_med_Ciprofloxacin',
        'prior_med_Ertapenem',
        'prior_med_Metronidazole',
        'prior_med_Vancomycin',
    ]
    
    # Lab name mappings (base name -> display name)
    LAB_MAP = {
        "wbc": "WBC",
        "neut": "Neutrophils",
        "lymph": "Lymphocytes",
        "hgb": "HGB",
        "plt": "PLT",
        "hco3": "Bicarbonate",
        "na": "Sodium",
        "lac": "Lactate",
        "cr": "Creatinine",
        "bun": "BUN",
        "pct": "Procalcitonin",
    }
    
    # Antibiotic class/subtype lookup
    ANTIBIOTIC_LOOKUP = {
        'Nitrofurantoin': ('Nitrofuran', 'Nitrofuran'),
        'Cephalexin': ('Beta Lactam', 'Cephalosporin Gen1'),
        'Piperacillin-Tazobactam-Dextrs': ('Beta Lactam', 'Beta Lactam Combo'),
        'Sulfamethoxazole-Trimethoprim': ('Combination Antibiotic', 'Sulfonamide Combo'),
        'Ciprofloxacin Hcl': ('Fluoroquinolone', 'Fluoroquinolone'),
        'Cefazolin': ('Beta Lactam', 'Cephalosporin Gen1'),
        'Cefazolin In Dextrose': ('Beta Lactam', 'Cephalosporin Gen1'),
        'Levofloxacin': ('Fluoroquinolone', 'Fluoroquinolone'),
        'Azithromycin': ('Macrolide Lincosamide', 'Macrolide'),
        'Amoxicillin-Pot Clavulanate': ('Beta Lactam', 'Beta Lactam Combo'),
        'Metronidazole In Nacl': ('Nitroimidazole', 'Nitroimidazole'),
        'Ceftriaxone': ('Beta Lactam', 'Cephalosporin Gen3'),
        'Vancomycin': ('Glycopeptide', 'Glycopeptide'),
        'Levofloxacin In': ('Fluoroquinolone', 'Fluoroquinolone'),
        'Vancomycin In Dextrose': ('Glycopeptide', 'Glycopeptide'),
        'Metronidazole': ('Nitroimidazole', 'Nitroimidazole'),
        'Ciprofloxacin In': ('Fluoroquinolone', 'Fluoroquinolone'),
        'Doxycycline Hyclate': ('Tetracycline', 'Tetracycline'),
        'Cefpodoxime': ('Beta Lactam', 'Cephalosporin Gen3'),
        'Piperacillin-Tazobactam': ('Beta Lactam', 'Beta Lactam Combo'),
        'Rifaximin': ('Ansamycin', 'Ansamycin'),
        'Vancomycin-Diluent Combo': ('Glycopeptide', 'Glycopeptide'),
        'Clindamycin In': ('Macrolide Lincosamide', 'Lincosamide'),
        'Amoxicillin': ('Beta Lactam', 'Penicillin'),
        'Nitrofurantoin Macrocrystal': ('Nitrofuran', 'Nitrofuran'),
        'Macrobid': ('Nitrofuran', 'Nitrofuran'),
        'Cefdinir': ('Beta Lactam', 'Cephalosporin Gen3'),
        'Gentamicin-Sodium Citrate': ('Aminoglycoside', 'Aminoglycoside'),
        'Clindamycin Phosphate': ('Macrolide Lincosamide', 'Lincosamide'),
        'Cefoxitin': ('Beta Lactam', 'Cephalosporin Gen2'),
        'Cipro': ('Fluoroquinolone', 'Fluoroquinolone'),
        'Clindamycin Hcl': ('Macrolide Lincosamide', 'Lincosamide'),
        'Vancomycin In': ('Glycopeptide', 'Glycopeptide'),
        'Moxifloxacin': ('Fluoroquinolone', 'Fluoroquinolone'),
        'Gentamicin': ('Aminoglycoside', 'Aminoglycoside'),
        'Linezolid': ('Oxazolidinone', 'Oxazolidinone'),
        'Zithromax': ('Macrolide Lincosamide', 'Macrolide'),
        'Erythromycin': ('Macrolide Lincosamide', 'Macrolide'),
        'Bactrim Ds': ('Combination Antibiotic', 'Sulfonamide Combo'),
        'Fosfomycin Tromethamine': ('Fosfomycin', 'Fosfomycin'),
        'Cefepime': ('Beta Lactam', 'Cephalosporin Gen4'),
        'Keflex': ('Beta Lactam', 'Cephalosporin Gen1'),
        'Doxycycline Monohydrate': ('Tetracycline', 'Tetracycline'),
        'Colistin': ('Polymyxin, Lipopeptide', 'Polymyxin'),
        'Clarithromycin': ('Macrolide Lincosamide', 'Macrolide'),
        'Levaquin': ('Fluoroquinolone', 'Fluoroquinolone'),
        'Rifampin': ('Ansamycin', 'Ansamycin'),
        'Ciprofloxacin': ('Fluoroquinolone', 'Fluoroquinolone'),
        'Cefuroxime Axetil': ('Beta Lactam', 'Cephalosporin Gen2'),
        'Augmentin': ('Beta Lactam', 'Beta Lactam Combo'),
        'Cefadroxil': ('Beta Lactam', 'Cephalosporin Gen1'),
        'Methenamine Hippurate': ('Urinary Antiseptic', 'Urinary Antiseptic'),
        'Ertapenem': ('Beta Lactam', 'Carbapenem'),
        'Ofloxacin': ('Fluoroquinolone', 'Fluoroquinolone'),
        'Linezolid In Dextrose': ('Oxazolidinone', 'Oxazolidinone'),
        'Penicillin': ('Beta Lactam', 'Penicillin'),
        'Silver Sulfadiazine': ('Sulfonamide', 'Sulfonamide'),
        'Dapsone': ('Sulfonamide', 'Sulfonamide'),
        'Ciprofloxacin-Dexamethasone': ('Fluoroquinolone', 'Fluoroquinolone'),
        'Ampicillin Sodium': ('Beta Lactam', 'Penicillin'),
        'Isoniazid': ('Antitubercular', 'Antitubercular'),
        'Bactrim': ('Combination Antibiotic', 'Sulfonamide Combo'),
        'Fidaxomicin': ('Macrolide Lincosamide', 'Macrolide'),
        'Aztreonam In': ('Monobactam', 'Monobactam'),
        'Ethambutol': ('Antitubercular', 'Antitubercular'),
        'Tobramycin Sulfate': ('Aminoglycoside', 'Aminoglycoside'),
        'Cefepime In': ('Beta Lactam', 'Cephalosporin Gen4'),
        'Ampicillin': ('Beta Lactam', 'Penicillin'),
        'Minocycline': ('Tetracycline', 'Tetracycline'),
        'Ceftazidime-Dextrose': ('Beta Lactam', 'Cephalosporin Gen3'),
        'Aztreonam': ('Monobactam', 'Monobactam'),
        'Xifaxan': ('Ansamycin', 'Ansamycin'),
        'Erythromycin Ethylsuccinate': ('Macrolide Lincosamide', 'Macrolide'),
        'Gentamicin In Nacl': ('Aminoglycoside', 'Aminoglycoside'),
        'Meropenem': ('Beta Lactam', 'Carbapenem'),
        'Gatifloxacin': ('Fluoroquinolone', 'Fluoroquinolone'),
        'Flagyl': ('Nitroimidazole', 'Nitroimidazole'),
        'Macrodantin': ('Nitrofuran', 'Nitrofuran'),
        'Amikacin': ('Aminoglycoside', 'Aminoglycoside'),
        'Trimethoprim': ('Folate Synthesis Inhibitor', 'Folate Synthesis Inhibitor'),
        'Tobramycin-Dexamethasone': ('Aminoglycoside', 'Aminoglycoside'),
        'Dicloxacillin': ('Beta Lactam', 'Penicillin'),
        'Moxifloxacin-Sod.Chloride(Iso)': ('Fluoroquinolone', 'Fluoroquinolone'),
        'Hiprex': ('Urinary FAntiseptic', 'Urinary Antiseptic'),
        'Ceftazidime': ('Beta Lactam', 'Cephalosporin Gen3'),
        'Zyvox': ('Oxazolidinone', 'Oxazolidinone'),
        'Methenamine Mandelate': ('Urinary Antiseptic', 'Urinary Antiseptic'),
        'Rifabutin': ('Ansamycin', 'Ansamycin'),
        'Tedizolid': ('Oxazolidinone', 'Oxazolidinone'),
    }
    
    # Common organisms for prior culture history
    ORGANISMS = [
        'ESCHERICHIA COLI',
        'KLEBSIELLA PNEUMONIAE',
        'KLEBSIELLA OXYTOCA',
        'PSEUDOMONAS AERUGINOSA',
        'STAPHYLOCOCCUS AUREUS',
        'ENTEROCOCCUS SPECIES',
        'ENTEROCOCCUS FAECALIS',
        'ENTEROCOCCUS FAECIUM',
        'PROTEUS MIRABILIS',
        'ENTEROBACTER CLOACAE COMPLEX',
        'ENTEROBACTER CLOACAE',
        'COAG NEGATIVE STAPHYLOCOCCUS',
        'SERRATIA MARCESCENS',
        'CITROBACTER FREUNDII',
        'CITROBACTER KOSERI',
        'MORGANELLA MORGANII',
        'STREPTOCOCCUS AGALACTIAE',
        'STREPTOCOCCUS PYOGENES',
    ]
    
    # Mapping from organism patterns to feature name suffix
    # This maps full organism names to the genus used in model features
    ORGANISM_TO_FEATURE = {
        'ESCHERICHIA': 'Escherichia',
        'KLEBSIELLA': 'Klebsiella',
        'PSEUDOMONAS': 'Pseudomonas',
        'STAPHYLOCOCCUS': 'Staphylococcus',
        'ENTEROCOCCUS': 'Enterococcus',
        'PROTEUS': 'Proteus',
        'ENTEROBACTER': 'Enterobacter',
        'COAG NEGATIVE': 'CONS',  # Special case
        'SERRATIA': 'Serratia',
        'CITROBACTER': 'Citrobacter',
        'MORGANELLA': 'Morganella',
        'STREPTOCOCCUS': 'Streptococcus',
    }
    
    def __init__(
        self,
        patient_data: Dict[str, Any],
        credentials: Optional[Dict[str, str]] = None,
        api_prefix: Optional[str] = None,
        client_id: Optional[str] = None,
        abx_list_path: Optional[str] = None,
    ):
        """
        Initialize the feature engineer.
        
        Args:
            patient_data: Dict containing patient information.
                         Expected keys: 'FHIR', 'FHIR STU3', 'DOB', 'MRN', etc.
            credentials: Optional dict with 'username' and 'password' for API calls.
            api_prefix: Optional API prefix for Epic FHIR endpoints.
            client_id: Optional Epic client ID for API calls.
            abx_list_path: Path to antibiotics list pkl file.
        """
        self.patient_data = patient_data.copy()
        self.credentials = credentials or {}
        self.api_prefix = api_prefix or os.environ.get('EPIC_ENV', '')
        self.client_id = client_id or os.environ.get('EPIC_CLIENT_ID', '')
        
        # Paths for reference data
        self.abx_list_path = abx_list_path
        
        # Internal feature storage
        self._features: Dict[str, Any] = {}
    
    def generate_features(
        self,
        include_vitals: bool = True,
        include_antibiotics: bool = True,
        include_prior_resistance: bool = True,
        vitals_lookback_hours: int = 48,
        abx_lookback_days: int = 180,
        resistance_lookback_days: int = 180,
    ) -> pd.DataFrame:
        """
        Generate all features as a DataFrame with named columns.
        
        Produces a 67-dimension feature vector including:
        - Demographics (age, gender)
        - Hospital ward (IP/OP/ER one-hot)
        - ADI score
        - Procedures within 6 months
        - Vitals (25 features)
        - Prior antibiotics and classes
        - Prior organism infections
        
        Args:
            include_vitals: Whether to include vital sign features.
            include_antibiotics: Whether to include prior antibiotic features.
            include_prior_resistance: Whether to include prior organism/resistance features.
            vitals_lookback_hours: Hours to look back for vitals.
            abx_lookback_days: Days to look back for prior antibiotics.
            resistance_lookback_days: Days to look back for prior resistance.
            
        Returns:
            DataFrame with one row containing all features.
        """
        self._features = {}
        
        # Demographics (age, gender)
        self._features.update(self._get_demographics())
        
        # Hospital ward (IP/OP/ER one-hot encoded)
        self._features.update(self._get_hospital_ward())
        
        # ADI score (Area Deprivation Index - dummy value)
        self._features.update(self._get_adi_score())
        
        # Procedure-related features within 6 months
        self._features.update(self._get_procedures_within_6mo())
        
        # Vitals (25 features)
        if include_vitals:
            self._features.update(self._get_vitals(lookback_hours=vitals_lookback_hours))
        
        # Labs - COMMENTED OUT (not used by models)
        # if include_labs:
        #     self._features.update(self._get_labs(lookback_days=labs_lookback_days))
        
        # Prior antibiotics (medication names and classes)
        if include_antibiotics:
            self._features.update(self._get_prior_antibiotics(lookback_days=abx_lookback_days))
        
        # Prior organism infections
        if include_prior_resistance:
            self._features.update(
                self._get_prior_organism_resistance(lookback_days=resistance_lookback_days)
            )
        
        return pd.DataFrame([self._features])
    
    def _get_demographics(self) -> Dict[str, Any]:
        """
        Extract demographic features from patient data.
        
        Returns:
            Dict with demographic features (age, gender, etc.)
        """
        features = {}
        
        # Age calculation (in years, not binned - models expect continuous age)
        dob = self.patient_data.get('DOB')
        features['age'] = self._calculate_age(dob)
        
        # Gender (model expects: typically 0=female, 1=male)
        if 'gender' in self.patient_data:
            features['gender'] = self.patient_data['gender']
        elif 'Sex' in self.patient_data:
            # Map sex to binary gender encoding
            sex = self.patient_data['Sex'].lower() if isinstance(self.patient_data['Sex'], str) else self.patient_data['Sex']
            features['gender'] = 1 if sex in ['male', 'm', 1] else 0
        
        return features
    
    def _calculate_age(self, dob: Optional[str]) -> Optional[float]:
        """
        Calculate age in years from date of birth.
        
        Args:
            dob: Date of birth string (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ format)
            
        Returns:
            Age in years (float) or None if cannot be calculated
        """
        if not dob:
            return None
        
        try:
            pacific_tz = pytz.timezone("America/Los_Angeles")
            now = datetime.now(pacific_tz)
            
            # Parse DOB
            dob_str = dob.split("T")[0]
            dob_date = datetime.strptime(dob_str, "%Y-%m-%d")
            dob_date = pacific_tz.localize(dob_date)
            
            # Calculate age in years
            age = (now - dob_date).days / 365.25
            return round(age, 1)
                
        except Exception as e:
            logger.warning(f"Error calculating age: {e}")
            return None
    
    def _get_hospital_ward(self) -> Dict[str, int]:
        """
        Get hospital ward type features.
        
        NOTE: This pipeline is designed for inpatient data only.
        All patients processed through this pipeline are assumed to be inpatients.
        
        Returns one-hot encoded ward features:
        - hosp_ward_IP: Always 1 (inpatient pipeline)
        - hosp_ward_OP: Always 0 (inpatient pipeline)
        - hosp_ward_ER: Always 0 (TODO: Find FHIR endpoint to determine ER status)
        """
        # Pipeline only processes inpatient data
        features = {
            'hosp_ward_IP': 1,  # Always inpatient
            'hosp_ward_OP': 0,  # Not outpatient
            'hosp_ward_ER': 0,  # TODO: Need to find FHIR endpoint to get ER admission status
        }
        
        return features
    
    def _get_adi_score(self) -> Dict[str, float]:
        """
        Get Area Deprivation Index score.
        
        Returns dummy value as ADI requires external data source.
        """
        return {'adi_score': 0.0}
    
    # TODO: feature engineer for procedures
    def _get_procedures_within_6mo(self) -> Dict[str, int]:
        """
        Extract procedure-related features from the last 6 months.
        
        Identifies specific procedure types from pre-fetched procedure data.
        Returns binary flags for each procedure type.
        
        NOTE: No access to procedure endpoint response - The authenticated client's search request 
        applies to a sub-resource that the client is not authorized for. 
        Tried both category "order" (103693007) and "surgical" (387713003), neither has access to.
        API Documentation: order: https://fhir.epic.com/Specifications?api=976
                          surgical: https://fhir.epic.com/specifications?api=10042
        """
        features = {
            'nursing_visits_within_6mo': 0,  # TODO - requires separate Encounter endpoint as the current only works for Neitherland
            'urethral_catheter_within_6mo': 0,
            'surgical_procedure_within_6mo': 0,
            'cvc_within_6mo': 0,
            'parenteral_nutrition_within_6mo': 0,
            'mechvent_within_6mo': 0,
        }
        
        # Get pre-fetched procedures from patient_data
        procedures = self.patient_data.get('procedures', [])
        

        # Skip for now as no access to procedure endpoint response's sub-resource
        # for procedure in procedures:
        #     # Get procedure code text and coding
        #     code = procedure.get('code', {})
        #     code_text = code.get('text', '').lower()
            
        #     # Also check coding array for additional keywords
        #     coding_texts = []
        #     for coding in code.get('coding', []):
        #         coding_texts.append(coding.get('display', '').lower())
            
        #     all_text = code_text + ' ' + ' '.join(coding_texts)
            
        #     # Check category for surgical procedures
        #     category = procedure.get('category', {})
        #     category_code = ''
        #     for cat_coding in category.get('coding', []):
        #         category_code = cat_coding.get('code', '')
            
        #     # Surgical procedure detection
        #     if category_code == '387713003':
        #         features['surgical_procedure_within_6mo'] = 1
        #     elif any(term in all_text for term in ['surgery', 'surgical', 'ectomy', 'otomy', 'plasty']):
        #         features['surgical_procedure_within_6mo'] = 1
            
        #     # Urethral catheter detection
        #     if any(term in all_text for term in ['catheter', 'foley', 'urinary', 'urethral']):
        #         features['urethral_catheter_within_6mo'] = 1
            
        #     # CVC (central venous catheter) detection
        #     if any(term in all_text for term in ['central line', 'picc', 'central venous', 'cvc', 'port-a-cath', 'hickman']):
        #         features['cvc_within_6mo'] = 1
            
        #     # Mechanical ventilation detection
        #     if any(term in all_text for term in ['ventilat', 'intubat', 'mechanical vent', 'endotracheal']):
        #         features['mechvent_within_6mo'] = 1
            
        #     # Parenteral nutrition detection
        #     if any(term in all_text for term in ['tpn', 'parenteral nutrition', 'total parenteral']):
        #         features['parenteral_nutrition_within_6mo'] = 1
        
        return features
    
    def _get_vitals(self, lookback_hours: int = 48) -> Dict[str, Any]:
        """
        Extract vital sign features from FHIR observations.
        
        Generates aggregated statistics (mean, median, min, max, Q25, Q75, first, last)
        for each vital sign type within the lookback window.
        
        Args:
            lookback_hours: Number of hours to look back for vitals.
            
        Returns:
            Dict with vital sign features.
        """
        # Initialize ALL expected vital features to 0
        features = {feat: 0.0 for feat in self.VITAL_FEATURES}
        
        if not self.credentials or not self.api_prefix:
            logger.warning("No credentials/API configured, returning default vitals")
            return features
        
        try:
            # Calculate cutoff timestamp
            cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
            cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%MZ")
            print(f'cutoff_str: ${cutoff_str}')
            # Fetch vital observations
            params = {
                "patient": self.patient_data.get("FHIR"),
                "category": "vital-signs",
                "date": f"ge{cutoff_str}",
                "_format": "json",
            }
            
            response = requests.get(
                f"{self.api_prefix}api/FHIR/R4/Observation",
                params=params,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Epic-Client-ID": self.client_id,
                },
                auth=HTTPBasicAuth(
                    self.credentials.get("username", ""),
                    self.credentials.get("password", ""),
                ),
            )

            vital_data = response.json()
            print(f'vital_data: ${vital_data}')
            vital_values = self._parse_vital_observations(vital_data)
            print(f'vital_values: ${vital_values}')
            # Generate aggregated features for each vital
            for vital_name, values in vital_values.items():
                if vital_name not in self.VITAL_SIGN_MAP.values():
                    continue
                if not values:
                    continue
                
                features[f"mean_{vital_name}"] = np.mean(values)
                features[f"median_{vital_name}"] = np.median(values)
                features[f"max_{vital_name}"] = np.max(values)
                features[f"min_{vital_name}"] = np.min(values)
                features[f"Q25_{vital_name}"] = np.percentile(values, 25)
                features[f"Q75_{vital_name}"] = np.percentile(values, 75)
                features[f"first_{vital_name}"] = values[0]
                features[f"last_{vital_name}"] = values[-1]
                
        except Exception as e:
            logger.error(f"Error fetching vitals: {e}")
        
        return features
    
    def _parse_vital_observations(self, vital_data: Dict) -> Dict[str, List[float]]:
        """Parse FHIR vital observation bundle into values by type."""
        vital_values: Dict[str, List[float]] = {}
        
        for entry in vital_data.get("entry", []):
            resource = entry.get("resource", {})
            if "effectiveDateTime" not in resource:
                continue
            
            try:
                # Handle component-based vitals (like BP)
                if "component" in resource:
                    for comp in resource["component"]:
                        self._extract_vital_value(comp, vital_values)
                else:
                    self._extract_vital_value(resource, vital_values)
            except Exception:
                continue
        
        return vital_values
    
    def _extract_vital_value(
        self, 
        component: Dict, 
        vital_values: Dict[str, List[float]]
    ) -> None:
        """Extract a single vital value from a FHIR component."""
        if "valueQuantity" not in component:
            return
        
        value = component["valueQuantity"].get("value")
        name = component.get("code", {}).get("text", "")
        
        # Map to standardized name
        name = self.VITAL_SIGN_MAP.get(name, name)
        
        if name and value is not None:
            if name not in vital_values:
                vital_values[name] = []
            vital_values[name].append(float(value))
    
    def _get_labs(self, lookback_days: int = 14) -> Dict[str, Any]:
        """
        Extract lab value features from Epic API.
        
        Generates aggregated statistics for each lab type.
        
        Args:
            lookback_days: Number of days to look back for labs.
            
        Returns:
            Dict with lab value features.
        """
        features = {}
        
        if not self.credentials or not self.api_prefix:
            logger.warning("No credentials/API configured, skipping labs")
            return features
        
        for base_name, display_name in self.LAB_MAP.items():
            try:
                lab_values = self._fetch_lab_values(base_name, lookback_days)
                
                if lab_values:
                    features[f"first_{display_name}"] = lab_values[0]
                    features[f"last_{display_name}"] = lab_values[-1]
                    features[f"mean_{display_name}"] = np.mean(lab_values)
                    features[f"median_{display_name}"] = np.median(lab_values)
                    features[f"max_{display_name}"] = np.max(lab_values)
                    features[f"min_{display_name}"] = np.min(lab_values)
                    features[f"Q25_{display_name}"] = np.percentile(lab_values, 25)
                    features[f"Q75_{display_name}"] = np.percentile(lab_values, 75)
                    
            except Exception as e:
                logger.warning(f"Error fetching lab {base_name}: {e}")
        
        return features
    
    def _fetch_lab_values(self, base_name: str, lookback_days: int) -> List[float]:
        """Fetch lab values from Epic API for a specific lab type."""
        lab_packet = {
            "PatientID": self.patient_data.get("FHIR STU3"),
            "PatientIDType": "FHIR STU3",
            "UserID": self.credentials.get("username", "")[4:],
            "UserIDType": "External",
            "NumberDaysToLookBack": lookback_days,
            "MaxNumberOfResults": 200,
            "FromInstant": "",
            "ComponentTypes": [{"Value": base_name, "Type": "base-name"}],
        }
        
        response = requests.post(
            f"{self.api_prefix}api/epic/2014/Results/Utility/"
            "GETPATIENTRESULTCOMPONENTS/ResultComponents",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Epic-Client-ID": self.client_id,
            },
            auth=HTTPBasicAuth(
                self.credentials.get("username", ""),
                self.credentials.get("password", ""),
            ),
            json=lab_packet,
        )
        
        lab_response = response.json()
        values = []
        
        for component in lab_response.get("ResultComponents", []):
            raw_value = component.get("Value")
            if raw_value:
                # Extract numeric value
                numeric_chars = "0123456789-."
                num_str = "".join(c for c in raw_value[0] if c in numeric_chars)
                if num_str:
                    try:
                        values.append(float(num_str))
                    except ValueError:
                        continue
        
        return values
    
    def _get_prior_antibiotics(self, lookback_days: int = 180) -> Dict[str, Any]:
        """
        Extract prior antibiotic usage features.
        
        Creates binary flags for antibiotic names, classes, and subtypes.
        
        Args:
            lookback_days: Number of days to look back for prior antibiotics.
            
        Returns:
            Dict with antibiotic usage features.
        """
        # Initialize ALL expected antibiotic features to 0
        features = {}
        for feat in self.PRIOR_ABX_CLASS_FEATURES:
            features[feat] = 0
        for feat in self.PRIOR_MED_FEATURES:
            features[feat] = 0
        
        if not self.credentials or not self.api_prefix:
            logger.warning("No credentials/API configured, returning default antibiotics")
            return features
        
        try:
            max_delta = timedelta(days=lookback_days)
            now = datetime.now()
            
            # Fetch medication requests
            params = {"patient": self.patient_data.get("FHIR")}
            response = requests.get(
                f"{self.api_prefix}api/FHIR/R4/MedicationRequest",
                params=params,
                headers={"Epic-Client-ID": self.client_id},
                auth=HTTPBasicAuth(
                    self.credentials.get("username", ""),
                    self.credentials.get("password", ""),
                ),
            )
            
            med_dict = xmltodict.parse(response.text)
            # print(f'med_dict: ${med_dict}')
            if "Bundle" not in med_dict:
                return features
            
            entries = med_dict["Bundle"].get("entry", [])
            if isinstance(entries, collections.OrderedDict):
                entries = [entries]
            
            for entry in entries:
                # print(f'entry: ${entry}')
                self._process_medication_entry(entry, now, max_delta, features)
                
        except Exception as e:
            logger.error(f"Error fetching prior antibiotics: {e}")
        
        return features
    
    def _process_medication_entry(
        self,
        entry: Dict,
        now: datetime,
        max_delta: timedelta,
        features: Dict[str, Any],
    ) -> None:
        """Process a single medication entry and update features."""
        try:
            resource = entry.get("resource", {}).get("MedicationRequest", {})
            if not resource:
                return
            
            # Get medication name
            med_ref = resource.get("medicationReference", {})
            med_name = med_ref.get("display", {}).get("@value", "") # e.g. 'cephalexin (Keflex) 500 mg capsule'
            
            # Get order time
            order_time = resource.get("authoredOn", {}).get("@value", "")
            try:
                order_dt = datetime.strptime(order_time, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                try:
                    order_dt = datetime.strptime(order_time, "%Y-%m-%d")
                except ValueError:
                    return
            
            # Check if within lookback window
            if now - order_dt > max_delta:
                return
            
            # Clean medication name and get class/subtype
            cleaned_name, abx_class, abx_subtype = self._clean_medication_name(med_name)
            # print(cleaned_name, abx_class, abx_subtype)
            if cleaned_name:
                # Use model-expected feature names with prefixes
                # prior_med_{MedName} for specific medications
                med_key = f"prior_med_{cleaned_name}"
                features[med_key] = features.get(med_key, 0) + 1
                
                # prior_abx_class_{ClassName} for antibiotic classes
                if abx_class:
                    # Replace spaces with underscores for feature name
                    class_key = f"prior_abx_class_{abx_class.replace(' ', '_')}"
                    features[class_key] = features.get(class_key, 0) + 1
                    
        except Exception as e:
            logger.debug(f"Error processing medication entry: {e}")
    
    def _clean_medication_name(
        self, 
        name: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Clean medication name and look up antibiotic class/subtype.
        
        Args:
            name: Raw medication name from FHIR
            
        Returns:
            Tuple of (cleaned_name, antibiotic_class, antibiotic_subtype)
        """
        if not isinstance(name, str) or not name:
            return None, None, None
        
        cleaned = name.lower()
        
        # Remove dosage/concentration patterns
        cleaned = re.sub(r'\s*\d+(\.\d+)?\s*(mg|mcg|gram|ml|%)', '', cleaned)
        
        # Remove parenthetical content
        cleaned = re.sub(r'\(.*?\)', '', cleaned)
        
        # Remove common filler words
        filler_pattern = (
            r'in.*$|tablet|capsule|intravenous|piggyback|solution|suspension|oral|'
            r'sodium|chloride|injection|citrate|soln|dextrose|iv|macrocrystals|'
            r'macrocrystal|axetil|potassium|packet|monohydrate|ethylsuccinate|'
            r'powder|mandelate|hyclate|hcl|hippurate|tromethamine|million|unit|'
            r'syrup|chewable|delayed|mphase|release|benzathine|syringe|dispersible|'
            r'sulfate|procaine|blue|hyos|sod*phos|susp|and|fosamil|extended|'
            r'succinate|granules|delay|pot|ext|rel|cyam|salicylate|salicyl|'
            r'sodphos|methylene|stearate|synergy'
        )
        cleaned = re.sub(filler_pattern, '', cleaned)
        
        # Remove extra dosage references
        cleaned = re.sub(r'\d|for\s*|er\s*|hr\s*|/ml\s*|ml\s*|v\s*|g\s*|im\s*', '', cleaned)
        
        # Clean up whitespace and special chars
        cleaned = re.sub(r'[\s/.\-]+$', '', cleaned).strip()
        
        # Convert to title case
        cleaned = string.capwords(cleaned)
        
        # Look up antibiotic class and subtype
        abx_class, abx_subtype = self.ANTIBIOTIC_LOOKUP.get(cleaned, (None, None))
        
        return cleaned, abx_class, abx_subtype
    
    def _get_prior_organism_resistance(
        self, 
        lookback_days: int = 180
    ) -> Dict[str, Any]:
        """
        Extract prior organism and resistance features from culture results.
        
        Creates features for:
        - prior_infected_{ORGANISM}: Binary flag for prior positive cultures
        - {ORGANISM}_{antibiotic}_S: Count of susceptible results
        - {ORGANISM}_{antibiotic}_R: Count of resistant results
        
        Args:
            lookback_days: Number of days to look back for prior cultures.
            
        Returns:
            Dict with organism and resistance features.
        """
        # Initialize ALL expected prior infected features to 0
        features = {feat: 0 for feat in self.PRIOR_INFECTED_FEATURES}
        
        if not self.credentials or not self.api_prefix:
            logger.warning("No credentials/API configured, returning default prior resistance")
            return features
        
        try:
            max_time_delta = timedelta(days=lookback_days)
            
            # Culture LOINC codes for diagnostic reports
            culture_loinc_codes = ['90423-5', '45665', '6463-4', '79381-0', '13317-3']
            
            params = {
                'patient': self.patient_data.get("FHIR"),
                'code': f'http://loinc.org|{",".join(culture_loinc_codes)}'
            }
            
            resp = requests.get(
                f"{self.api_prefix}api/FHIR/R4/DiagnosticReport",
                params=params,
                headers={
                    'Content-Type': 'application/json; charset=utf-8',
                    'Accept': 'application/json',
                    'Epic-Client-ID': self.client_id,
                },
                auth=HTTPBasicAuth(
                    self.credentials.get("username", ""),
                    self.credentials.get("password", ""),
                ),
                timeout=900,
            )
            
            data = resp.json()
            observation_ids = []
            
            for entry in data.get('entry', []):
                resource = entry.get('resource', {})
                order_time = resource.get('effectiveDateTime', None)
                if order_time is None:
                    continue
                
                try:
                    order_date_time = datetime.strptime(order_time, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    try:
                        order_date_time = datetime.strptime(order_time, "%Y-%m-%d")
                    except ValueError:
                        continue
                
                if datetime.now() - order_date_time > max_time_delta:
                    continue
                
                for result in resource.get('result', []):
                    ref = result.get('reference', '')
                    if 'Observation/' in ref:
                        observation_ids.append(ref.split('Observation/')[1])
            
            if len(observation_ids) == 0:
                # print(f'No observation IDs found')
                return features
            
            # Get culture results from observations
            historical_microbiality = self._get_culture_order_results(observation_ids)
            
            for idx, row in historical_microbiality.iterrows():
                if row['Organism'] is None:
                    continue
                
                # Map organism to feature name using ORGANISM_TO_FEATURE mapping
                organism_full = row['Organism'].upper()
                organism_feature_name = None
                
                # Find matching organism pattern
                for pattern, feature_name in self.ORGANISM_TO_FEATURE.items():
                    if pattern in organism_full:
                        organism_feature_name = feature_name
                        break
                
                if organism_feature_name:
                    # Create prior_infected_* feature (matches model expected features)
                    key = f"prior_infected_{organism_feature_name}"
                    features[key] = 1
                
                # Process susceptibility results
                if 'Susceptibility' in row and isinstance(row['Susceptibility'], list):
                    for abx in row['Susceptibility']:
                        abx_clean, _, _ = self._clean_medication_name(abx)
                        if abx_clean and organism_feature_name:
                            key = f"{organism_feature_name}_{abx_clean}_S"
                            features[key] = features.get(key, 0) + 1
                
                # Process resistance results
                if 'Resistant' in row and isinstance(row['Resistant'], list):
                    for abx in row['Resistant']:
                        abx_clean, _, _ = self._clean_medication_name(abx)
                        if abx_clean and organism_feature_name:
                            key = f"{organism_feature_name}_{abx_clean}_R"
                            features[key] = features.get(key, 0) + 1
                            
        except Exception as e:
            logger.error(f"Error fetching prior organism resistance: {e}")
        
        return features
    
    def _get_culture_order_results(
        self, 
        observation_ids: List[str], 
        debug: bool = False
    ) -> pd.DataFrame:
        """
        Fetch and parse culture order results from FHIR Observation resources.
        
        Args:
            observation_ids: List of Observation FHIR IDs to fetch
            debug: Whether to print debug messages
            
        Returns:
            DataFrame with culture results including organism and susceptibility info
        """
        df = pd.DataFrame(columns=[
            'FHIR', 'MRN', 'CultureeffectiveDateTime', 'cultureresults',
            'specimenID', 'Organism', 'Susceptibility', 'Resistant'
        ])
        
        queue = list(observation_ids)
        seen = set()
        
        while queue:
            obs_id = queue.pop()
            if obs_id in seen:
                continue
            seen.add(obs_id)
            
            try:
                res = requests.get(
                    f"{self.api_prefix}api/FHIR/R4/Observation",
                    params={'_id': obs_id, '_format': 'json'},
                    headers={
                        "Content-Type": "application/json; charset=utf-8",
                        "Epic-Client-ID": self.client_id,
                    },
                    auth=HTTPBasicAuth(
                        self.credentials.get("username", ""),
                        self.credentials.get("password", ""),
                    ),
                )
                
                if res.status_code != 200:
                    if debug:
                        logger.debug(f"HTTP {res.status_code} for observation {obs_id}")
                    continue
                
                data = res.json()
                entry = data.get('entry', [{}])[0].get('resource', {})
                # print(f'entry: ${entry}')
                # Recursive members - add to queue
                for member in entry.get('hasMember', []):
                    ref_id = member.get('reference', '').split('Observation/')[-1]
                    if ref_id and ref_id not in seen:
                        queue.append(ref_id)
                
                # Extract susceptibility info from notes
                note_text = entry.get('note', [{}])[0].get('text', '') if entry.get('note') else ''
                susceptible, resistant = self._extract_abx_info(note_text) if note_text else ([], [])
                
                # Check interpretation field
                interpretation = str(entry.get('interpretation', '')).lower()
                abx_name = entry.get('code', {}).get('text', '')
                
                if 'susceptible' in interpretation:
                    susceptible.append(abx_name)
                elif 'resistant' in interpretation:
                    resistant.append(abx_name)
                
                # Find organism from derivedFrom
                organism = None
                for deriv in entry.get('derivedFrom', []):
                    display = deriv.get('display', '')
                    organism = self._find_organism(display)
                    if organism:
                        break
                
                # Map value string to result status
                result_status = self._map_culture_value(entry.get('valueString', ''))
                
                # Check for organism in valueString
                if not organism and 'bottle:' in str(entry.get('valueString', '')):
                    organism = entry['valueString'].split('bottle:')[1]
                
                df = pd.concat([df, pd.DataFrame([{
                    'FHIR': self.patient_data.get('FHIR'),
                    'MRN': self.patient_data.get('MRN'),
                    'CultureeffectiveDateTime': entry.get('effectiveDateTime'),
                    'cultureresults': result_status,
                    'specimenID': entry.get('specimen', {}).get('reference', '').split('Specimen/')[-1],
                    'Organism': organism,
                    'Susceptibility': susceptible,
                    'Resistant': resistant
                }])], ignore_index=True)
                
            except Exception as e:
                if debug:
                    logger.debug(f"Exception for observation {obs_id}: {e}")
                continue

        # Filter to positive cultures only
        df = df[df['cultureresults'] == 'Positive']
        df.drop_duplicates(
            subset=['FHIR', 'MRN', 'CultureeffectiveDateTime', 'cultureresults'], 
            inplace=True
        )
        df.reset_index(drop=True, inplace=True)
        return df
    
    # Note: Current culture value mapping is not robust - it only checks for specific terms regidly
    # TODO: Have a more robust mapping function for culture results
    def _map_culture_value(self, value: str) -> str:
        """Map culture value string to standardized result."""
        if not value:
            return ''
        value = value.lower()
        if 'no' in value or 'negative' in value:
            return 'Negative'
        elif any(term in value for term in ['bottle', 'positive', 'growth', 'organisms']):
            return 'Positive'
        return value
    
    def _find_organism(self, value: str) -> Optional[str]:
        """Find organism name in a text string."""
        if not value:
            return None
        for org in self.ORGANISMS:
            if org.lower() in value.lower():
                return org
        return None
    
    def _extract_abx_info(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Extract antibiotic susceptibility and resistance info from text.
        
        Args:
            text: Text containing susceptibility information
            
        Returns:
            Tuple of (susceptible_antibiotics, resistant_antibiotics)
        """
        # Common antibiotics to look for
        antibiotics = [
            'amikacin', 'amoxicillin', 'ampicillin', 'azithromycin', 'aztreonam',
            'cefazolin', 'cefepime', 'cefoxitin', 'ceftazidime', 'ceftriaxone',
            'cefuroxime', 'ciprofloxacin', 'clindamycin', 'daptomycin', 'doxycycline',
            'ertapenem', 'erythromycin', 'gentamicin', 'imipenem', 'levofloxacin',
            'linezolid', 'meropenem', 'metronidazole', 'minocycline', 'moxifloxacin',
            'nitrofurantoin', 'oxacillin', 'penicillin', 'piperacillin', 'rifampin',
            'tetracycline', 'tobramycin', 'trimethoprim', 'vancomycin'
        ]
        
        text = text.replace('\r\n', ' ').lower()
        susceptible, resistant = [], []
        
        for abx in antibiotics:
            if re.search(rf"\b{abx}\b.*(susceptible|active|sensitive)", text):
                susceptible.append(abx)
            if re.search(rf"\b{abx}\b.*(resistant|not active)", text):
                resistant.append(abx)
        
        # Pattern matching for S/R designations
        s_patterns = re.findall(r'(\w+)[:\-\s]+(susceptible|sensitive|\bs\b)', text)
        r_patterns = re.findall(r'(\w+)[:\-\s]+(resistant|\br\b)', text)
        
        for drug, _ in s_patterns:
            if drug not in susceptible and len(drug) > 2:
                susceptible.append(drug)
        
        for drug, _ in r_patterns:
            if drug not in resistant and len(drug) > 2:
                resistant.append(drug)
        
        return susceptible, resistant
    
    def get_feature_names(self) -> List[str]:
        """
        Get list of all feature names that were generated.
        
        Returns:
            List of feature column names.
        """
        return list(self._features.keys())
    
    def __repr__(self) -> str:
        return (
            f"FeatureEngineer("
            f"patient_fhir='{self.patient_data.get('FHIR', 'N/A')}', "
            f"num_features={len(self._features)})"
        )
