import collections
from xml.sax.handler import feature_validation
import pandas as pd
import numpy as np
import os
import xmltodict
import json
import uuid
import requests
from requests.auth import HTTPBasicAuth
from datetime import date, datetime, timedelta, timezone
from dateutil.parser import parse
import xml.etree.ElementTree as ET
from tqdm import tqdm
import pickle
from . import cosmos
import pytz
import re
import string
import pandas 


class feature_engineering (object):

    def __init__(
        self,
        credentials,
        env,
        client_id,
        patient_dict,
        #modelpath=None,
        #databricks_endpoint=None,
        ):
        self.credentials = credentials
        self.fhir_r4 = patient_dict.get("FHIR", None)
        self.client_id = client_id
        # Load the model here 
        """ 
        with open(modelpath, "rb") as f:
            self.infernecemodel = pickle.load(f)
        if databricks_endpoint is None:
            self.clf = self.deploy["model"]
        else:
            self.clf = None
        """
        #self.databricks_endpoint = databricks_endpoint
        self.api_prefix = env
        self.patient_dict = patient_dict
        
    def __call__(self, feature_vector=None):
        """
        Get's all necessary features
        retrunrs feature vector
        """
        age_bin = self._get_Age_bin("Age", self.patient_dict["DOB"])
        #self._get_vitals() # add labs
        #self._get_labs() # add vitals
        #self._get_prior_abx() # add prior antibiotics and class and subtype
        self._get_conditions() # add comorbidities
        """
        ***** this feature extraction is not completed *************
        """
        prior_microbial_resitance_organism=self._get_prior_organism_microbial_resistance() # add prior microbial resistance

        # vetorzie feature 
        Feature_data = pd.DataFrame([self.patient_dict])
        Feature_data['Age_bin'] = age_bin
        return Feature_data
        
    

    def _get_Age_bin(self, feature_name, DOB):
        """
        Get's age bin from DOB
        """
        if DOB is None or DOB == "":
            return "Unknown"
        try:
            pacific_timezone = pytz.timezone("America/Los_Angeles")
            date = datetime.now(pacific_timezone)
            dob_date = datetime.strptime(DOB.split("T")[0], "%Y-%m-%d")
            dob_date = pacific_timezone.localize(dob_date)
            age = (date - dob_date).days / 365.25
            if age < 18 :
                return "<18"
            elif age < 25:
                return 1
            elif age < 35:
                return 2
            elif age <45:
                return 3
            elif age < 55:
                return 4
            elif age < 65:
                return 5
            elif age < 75:
                return 6
            elif age < 85:
                return 7
            elif age < 90:
                return 8
            else:
                return 9
        except Exception as e:
            logging.error(f"Error in calculating age bin: {e}")
            return "Unknown"


   
    def _get_vitals(self,look_back=48):
        """
            Get's vital signs from FHIR R4
        Args:
            look_back: how many hours to look back for vital signs
        Returns:
            Updates self.patient_dict with vital sign features
        """
        VITALSIGN_dict = {
                            "Systolic blood pressure": "BP_High_Systolic",
                            "Diastolic blood pressure": "BP_Low_Diastolic",
                            "Temp": "Temp",
                            "Pulse": "Pulse",
                            "Resp Rate": "Resp",
                            "SpO2": "SpO2",
                            "Heart Rate": "Heart Rate",
                        }

        def get_timestamp_hours_ago(look_back):
                now = datetime.now()
                delta = timedelta(hours=look_back)
                result = now - delta
                formatted_result = result.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
                return formatted_result

        cutoff_timestamp = get_timestamp_hours_ago(look_back)

        params = {
            "patient": self.patient_dict["FHIR"],
            "category": "vital-signs",
            "date": f"ge{cutoff_timestamp}",
            "_format": "json",
        }
        
        vitals_observation = requests.get(
            f"{self.api_prefix}api/FHIR/R4/Observation",
            params=params,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Epic-Client-ID": self.client_id,
            },
            auth=HTTPBasicAuth(
                self.credentials["username"], self.credentials["password"]
            ),
        )
        vital_dict = json.loads(vitals_observation.text)
        vital_signs = {}

        def process_vital_dict(vital_dict):
            for entry in vital_dict.get("entry", []):
                if ('resource' not in entry) or ("effectiveDateTime" not in entry["resource"]):
                    continue
                timestamp = entry["resource"]["effectiveDateTime"]

                try:
                    order_date_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                except:
                    order_date_time = datetime.strptime(timestamp, "%Y-%m-%d")

                codes = []
                try:
                    if "component" in entry["resource"]:  # Multiple values included
                        for comp in entry["resource"]["component"]: 
                            numerical_value = comp["valueQuantity"]["value"]
                            unit = comp["valueQuantity"]["unit"]
                            measurement_name = comp["code"]["text"]
                            if measurement_name in VITALSIGN_dict:
                                measurement_name = VITALSIGN_dict[measurement_name]
                            if measurement_name in vital_signs:
                                vital_signs[measurement_name].append(numerical_value)
                            else:
                                vital_signs[measurement_name] = [numerical_value]
                    else:
                        comp = entry["resource"]
                        numerical_value = comp["valueQuantity"]["value"]
                        measurement_name = comp["code"]["text"]
                        if measurement_name in VITALSIGN_dict:
                            measurement_name = VITALSIGN_dict[measurement_name]
                        if measurement_name in vital_signs:
                            vital_signs[measurement_name].append(numerical_value)
                        else:
                            vital_signs[measurement_name] = [numerical_value]
                except:
                    print('Error in processing vital_dict')
                    pass

        process_vital_dict(vital_dict)
        for vital in vital_signs.keys():
            if vital not in list(VITALSIGN_dict.values()):
                continue
            for vital_value in vital_signs[vital]:
                mean_vital=np.mean(vital_signs[vital])
                median_vital=np.median(vital_signs[vital])
                Q25_vital=np.percentile(vital_signs[vital],25)
                Q75_vital=np.percentile(vital_signs[vital],75)
                max_vital=np.max(vital_signs[vital])
                min_vital=np.min(vital_signs[vital])
                self.pateint_dict[f"mean_{vital}"] = mean_vital
                self.patient_dict[f"median_{vital}"] = median_vital
                self.patient_dict[f"max_{vital}"] = max_vital
                self.patient_dict[f"min_{vital}"] = min_vital
                self.patient_dict[f"Q25_{vital}"] = Q25_vital
                self.patient_dict[f"Q75_{vital}"] = Q75_vital
                self.pateint_dict[f"first_{vital}"] = vital_signs[vital][0]
                self.patient_dict[f"last_{vital}"] = vital_signs[vital][-1]
                

    def _get_labs(self,look_back=14):
       
        
        labs_dict = {
        "wbc": "WBC",
        "neut": "Neutrophils", # neutrophils is not recognized in Epic,
        "lymph": "Lymphocytes",   # lymphocytes is not recognized in Epic,
        "hgb": "HGB",
        "plt": "PLT",
        "hco3": "Bicarbonate", # hco3 is not recognized in Epic,
        "na": "Sodium",
        "lac": "Lactate", # lactate is not recognized in Epic,
        "cr": "Creatinine",
        "bun": "BUN",
        "pct": "Procalcitonin" # procalcitonin is not recognized in Epic,
        } # 'wbc', 'hgb', 'plt', 'na', 'k', 'cr', 'ca', 'mg', 'phos' lab base names has been coofirmed their name in Epic

        for base_name in tqdm(labs_dict.keys()):
            lab_result_packet = {
                "PatientID": self.patient_dict["FHIR STU3"],
                "PatientIDType": "FHIR STU3",
                "UserID": self.credentials["username"][4:],
                "UserIDType": "External",
                "NumberDaysToLookBack": look_back,
                "MaxNumberOfResults": 200, # Get most recent and this is the max number of results
                "FromInstant": "",
                "ComponentTypes": [{"Value": base_name, "Type": "base-name"}],
            }
            lab_component_packet = json.dumps(lab_result_packet)
            lab_component_response = requests.post(
                (
                    f"{self.api_prefix}api/epic/2014/Results/Utility/"
                    "GETPATIENTRESULTCOMPONENTS/ResultComponents"
                ),
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Epic-Client-ID": self.client_id,
                },
                auth=HTTPBasicAuth(
                    self.credentials["username"], self.credentials["password"]
                ),
                data=lab_component_packet,
            )
            numeric = "0123456789-."
            all_lab_vals=[]
            lab_response = json.loads(lab_component_response.text)
            if lab_response["ResultComponents"]: 
                for i in range(len(lab_response["ResultComponents"])):
                    if lab_response["ResultComponents"][i]["Value"] is None:
                        continue
                    value = lab_response["ResultComponents"][i]["Value"][0]
                    num_value = ""
                    for i, c in enumerate(value):
                        if c in numeric:
                            num_value += c
                    
                    value = float(num_value)
                    all_lab_vals.append(value)
            if len(all_lab_vals)>0:
                self.patient_dict[f'first_{labs_dict[base_name]}'] = all_lab_vals[0]
                self.patient_dict[f'last_{labs_dict[base_name]}'] = all_lab_vals[-1]
                self.patient_dict[f'mean_{labs_dict[base_name]}'] = np.mean(all_lab_vals)
                self.patient_dict[f'median_{labs_dict[base_name]}'] = np.median(all_lab_vals)
                self.patient_dict[f'max_{labs_dict[base_name]}'] = np.max(all_lab_vals)
                self.patient_dict[f'min_{labs_dict[base_name]}'] = np.min(all_lab_vals)
                self.patient_dict[f'Q25_{labs_dict[base_name]}'] = np.percentile(all_lab_vals,25)
                self.patient_dict[f'Q75_{labs_dict[base_name]}'] = np.percentile(all_lab_vals,75)

    def _get_prior_abx(self,look_back=180):
        max_time_delta = timedelta(days=look_back)    
        # only check for prior antibiotics in the last 6 months    
        with open("HttpTriggerInference/abx_list.pkl", "rb") as f:
            prior_antibiotics_names = pickle.load(f)

        def clean_medication_name(name: str) -> str:
            antibiotic_lookup = {'Nitrofurantoin': ('Nitrofuran', 'Nitrofuran'),
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
                'Hiprex': ('Urinary Antiseptic', 'Urinary Antiseptic'),
                'Ceftazidime': ('Beta Lactam', 'Cephalosporin Gen3'),
                'Zyvox': ('Oxazolidinone', 'Oxazolidinone'),
                'Methenamine Mandelate': ('Urinary Antiseptic', 'Urinary Antiseptic'),
                'Rifabutin': ('Ansamycin', 'Ansamycin'),
                'Tedizolid': ('Oxazolidinone', 'Oxazolidinone'),
                }
            if not isinstance(name, str):
                return ""

            name = name.lower()  # Convert to lowercase

            # Remove dosage or concentration (e.g., '1 mg', '0.5%', '2.5 mcg')
            name = re.sub(r'\s*\d+(\.\d+)?\s*(mg|mcg|gram|ml|%)', '', name)

            # Remove text in parentheses
            name = re.sub(r'\(.*?\)', '', name)

            # Remove common filler words and descriptors
            filler_words = (
                r'in.*$|tablet|capsule|intravenous|piggyback|solution|suspension|oral|sodium|chloride|'
                r'injection|citrate|soln|dextrose|iv|macrocrystals|macrocrystal|axetil|potassium|packet|'
                r'monohydrate|ethylsuccinate|powder|mandelate|hyclate|hcl|hippurate|tromethamine|'
                r'million|unit|syrup|chewable|delayed|mphase|release|benzathine|syringe|dispersible|'
                r'sulfate|procaine|blue|hyos|sod*phos|susp|and|fosamil|extended|succinate|granules|'
                r'delay|pot|ext|rel|cyam|salicylate|salicyl|sodphos|methylene|stearate|synergy'
            )
            name = re.sub(filler_words, '', name)

            # Remove extra dosage/unit references
            name = re.sub(r'\d|for\s*|er\s*|hr\s*|/ml\s*|ml\s*|v\s*|g\s*|im\s*', '', name)

            # Remove trailing characters, extra whitespace, slashes, dots, dashes
            name = re.sub(r'[\s/.\-]+$', '', name)
            name = name.strip()

            # Convert to title case for readability
            cleaned_name = string.capwords(name)
            # Map to antibiotic class and subtype
            antibiotic_class, antibiotic_subtype = antibiotic_lookup.get(cleaned_name, (None, None))
            return name, antibiotic_class, antibiotic_subtype
            


        params = {"patient": self.patient_dict["FHIR"]}

        request_results = requests.get(
            f"{self.api_prefix}api/FHIR/R4/MedicationRequest",
            params=params,
            headers={"Epic-Client-ID": self.client_id},
            auth=HTTPBasicAuth(
                self.credentials["username"], self.credentials["password"]
            ),
        )
        med_dict = xmltodict.parse(request_results.text)
        
        if "Bundle" not in med_dict:
            return

        # One or no results
        if type(med_dict["Bundle"]["entry"]) == collections.OrderedDict:
            if "MedicationRequest" in med_dict["Bundle"]["entry"]["resource"]:
                antibiotic_name,antibiotic_class, antibiotic_subtype =clean_medication_name(med_dict["Bundle"]["entry"]["resource"]["MedicationRequest"][
                    "medicationReference"
                ]["display"]["@value"])
                order_time = med_dict["Bundle"]["entry"]["resource"][
                    "MedicationRequest"
                ]["authoredOn"]["@value"]
                try:
                    order_date_time = datetime.strptime(
                        order_time, "%Y-%m-%dT%H:%M:%SZ"
                    )
                except:
                    order_date_time = datetime.strptime(order_time, "%Y-%m-%d")

                #if not antibiotic_name in prior_antibiotics_names:
                #    return
                if datetime.now() - order_date_time <= max_time_delta:
                    self.patient_dict[antibiotic_name] = 1
                    self.patient_dict[antibiotic_class] = 1
                    self.patient_dict[antibiotic_subtype] = 1
            return

        # Multiple results
        for entry in tqdm(med_dict["Bundle"]["entry"]):
            antibiotic_name,antibiotic_class, antibiotic_subtype = clean_medication_name(entry["resource"]["MedicationRequest"]["medicationReference"][
                "display"
            ]["@value"])
            order_time = entry["resource"]["MedicationRequest"]["authoredOn"]["@value"]
            try:
                order_date_time = datetime.strptime(order_time, "%Y-%m-%dT%H:%M:%SZ")
            except:
                order_date_time = datetime.strptime(order_time, "%Y-%m-%d")
            #if not antibiotic_name in prior_antibiotics_names:
            #    continue
            if datetime.now() - order_date_time <= max_time_delta:
                if antibiotic_name in self.patient_dict:
                    self.patient_dict[antibiotic_name] += 1
                    self.patient_dict[antibiotic_class] += 1
                    self.patient_dict[antibiotic_subtype] += 1
                else:
                    self.patient_dict[antibiotic_name] = 1
                    self.patient_dict[antibiotic_class] = 1
                    self.patient_dict[antibiotic_subtype] = 1
    
    def _get_conditions(self):
        patient_diagnosis_codes = {}
        patient_problem_request = requests.get(
            f"{self.api_prefix}api/FHIR/STU3/Condition", 
            params={
                "patient": self.patient_dict["FHIR STU3"],
                "clinical-status": "active,inactive,resolved",
            },
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Epic-Client-ID": self.client_id,
            },
            auth=HTTPBasicAuth(
                self.credentials["username"], self.credentials["password"]
            ),
        )
        patient_problem_dict = xmltodict.parse(patient_problem_request.text)

        if "Bundle" not in patient_problem_dict: 
            print("no entries")
            return
        # only one item
        if (
            type(patient_problem_dict["Bundle"]["entry"]) == collections.OrderedDict
        ): 
            if "Condition" in patient_problem_dict["Bundle"]["entry"]["resource"]:
                code = patient_problem_dict["Bundle"]["entry"]["resource"]["Condition"][
                    "code"
                ]["coding"][0]["code"]["@value"]
                patient_diagnosis_codes[code] = 1
        else:
            for key in tqdm(patient_problem_dict["Bundle"]["entry"]):
                code = key["resource"]["Condition"]["code"]["coding"][0]["code"][
                    "@value"
                ]
                if code not in patient_diagnosis_codes:
                    patient_diagnosis_codes[code] = 1
                else:
                    patient_diagnosis_codes[code] += 1
        # find the comorbidities
        with open("HttpTriggerInference/comorbidites.pkl", "rb") as f:
            comorbidities = pickle.load(f)
        for comorbidity, codes in comorbidities.items():
            for code in codes:
                if code in patient_diagnosis_codes:
                    self.patient_dict[comorbidity] = 1
                    break

    def _get_prior_organism_microbial_resistance(self,look_back=180):
        max_time_delta = timedelta(days=look_back)   
        culture_loinc_codes = ['90423-5','45665', '6463-4', '79381-0', '13317-3'] 
        params = {
        'patient': self.patient_dict["FHIR"],
        'code': f'http://loinc.org|{culture_loinc_codes}'
        }
        

        resp = requests.get(
        f"{os.environ['EPIC_ENV']}api/FHIR/R4/DiagnosticReport",
        params=params,
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
            'Epic-Client-ID': os.environ['EPIC_CLIENT_ID'],
        },
        auth=HTTPBasicAuth(os.environ['secretID'], os.environ['secretpass']),
        timeout=900,
        )
        data = resp.json()
        observation_ids = []
        for entry in data.get('entry', []):
            resource = entry.get('resource', {})
            order_time = resource.get('effectiveDateTime', None)
            if order_time is None:
                continue
            
            order_date_time = datetime.strptime(order_time, "%Y-%m-%dT%H:%M:%SZ")
            if datetime.now() - order_date_time > max_time_delta:
                continue

            for result in resource.get('result', []):
                ref = result.get('reference', '')
                if 'Observation/' in ref:
                    observation_ids.append(ref.split('Observation/')[1])
        if len(observation_ids) == 0:
            return
        historical_microbiality = get_cultureorderresults(observation_ids)
        for idx, row in historical_microbiality.iterrows():
            if row['Organism'] is None:
                continue
            organism = row['Organism'].upper()
            key = f"prior_{organism}"
            self.patient_dict[key] = 1
            if 'Susceptibility' in row and isinstance(row['Susceptibility'], list):
                for abx in row['Susceptibility']:
                    abx_clean, abx_class, abx_subtype = clean_medication_name(abx)
                    if abx_clean:
                        key = f"{organism}_{abx_clean}_S"
                        if key in self.patient_dict:
                            self.patient_dict[key] += 1
                        else:
                            self.patient_dict[key] = 1
            if 'Resistant' in row and isinstance(row['Resistant'], list):
                for abx in row['Resistant']:
                    abx_clean, abx_class, abx_subtype = clean_medication_name(abx)
                    if abx_clean:
                        key = f"{organism}_{abx_clean}_R"
                        if key in self.patient_dict:
                            self.patient_dict[key] += 1
                        else:
                            self.patient_dict[key] = 1

    def get_cultureorderresults(patient, obsfhirids, debug=False):
        def map_value_string(value):
            value = value.lower()
            if 'no' in value or 'negative' in value:
                return 'Negative'
            elif any(term in value for term in ['bottle', 'positive', 'growth', 'organisms']):
                return 'Positive'
            return value

        def find_organism(value):
            organisms = ['ESCHERICHIA COLI', 'KLEBSIELLA PNEUMONIAE', 'PSEUDOMONAS AERUGINOSA',
                        'STAPHYLOCOCCUS AUREUS', 'ENTEROCOCCUS SPECIES', 'PROTEUS MIRABILIS',
                        'ENTEROBACTER CLOACAE COMPLEX', 'COAG NEGATIVE STAPHYLOCOCCUS',
                        'SERRATIA MARCESCENS', 'KLEBSIELLA OXYTOCA']
            return next((org for org in organisms if org.lower() in value.lower()), None)

        def extract_abx_info(text, debug=False):
            with open("HttpTriggerInference/abx_list.pkl", "rb") as f:
                antibiotics = pickle.load(f)
            text = text.replace('\r\n', ' ').lower()
            susceptible, resistant = [], []

            for abx in antibiotics:
                if re.search(rf"\b{abx}\b.*(susceptible|active|sensitive)", text):
                    susceptible.append(abx)
                    if debug:
                        print(f"[MATCH] Susceptible: {abx}")
                if re.search(rf"\b{abx}\b.*(resistant|not active)", text):
                    resistant.append(abx)
                    if debug:
                        print(f"[MATCH] Resistant: {abx}")

            s_patterns = re.findall(r'(\w+)[:\-\s]+(susceptible|sensitive|\bs\b)', text)
            r_patterns = re.findall(r'(\w+)[:\-\s]+(resistant|\br\b)', text)

            for drug, _ in s_patterns:
                if drug not in susceptible and len(drug) > 2:
                    susceptible.append(drug)
                    if debug:
                        print(f"[PATTERN] Susceptible: {drug}")

            for drug, _ in r_patterns:
                if drug not in resistant and len(drug) > 2:
                    resistant.append(drug)
                    if debug:
                        print(f"[PATTERN] Resistant: {drug}")

            return susceptible, resistant

        df = pd.DataFrame(columns=[
            'FHIR', 'MRN', 'CultureeffectiveDateTime', 'cultureresults',
            'specimenID', 'Organism', 'Susceptibility', 'Resistant'
        ])

        queue = list(obsfhirids)
        seen = set()

        while queue:
            obs_id = queue.pop()
            if obs_id in seen:
                continue
            seen.add(obs_id)

            try:
                res = requests.get(
                    f"{os.environ['EPIC_ENV']}api/FHIR/R4/Observation",
                    params={'_id': obs_id, '_format': 'json'},
                    headers={
                        "Content-Type": "application/json; charset=utf-8",
                        "Epic-Client-ID": os.environ["EPIC_CLIENT_ID"],
                    },
                    auth=HTTPBasicAuth(os.environ["secretID"], os.environ["secretpass"]),
                )

                if res.status_code != 200:
                    if debug:
                        print(f"[ERROR] HTTP {res.status_code} for observation {obs_id}")
                    continue

                data = res.json()
                entry = data.get('entry', [{}])[0].get('resource', {})

                # Recursive members
                for member in entry.get('hasMember', []):
                    ref_id = member.get('reference', '').split('Observation/')[-1]
                    if ref_id and ref_id not in seen:
                        queue.append(ref_id)

                note_text = entry.get('note', [{}])[0].get('text', '')
                susceptible, resistant = extract_abx_info(note_text, debug=debug) if note_text else ([], [])

                interpretation = entry.get('interpretation', '').lower()
                abx_name = entry.get('code', {}).get('text', '')

                if 'susceptible' in interpretation:
                    susceptible.append(abx_name)
                elif 'resistant' in interpretation:
                    resistant.append(abx_name)

                organism = None
                for deriv in entry.get('derivedFrom', []):
                    display = deriv.get('display', '')
                    organism = find_organism(display)
                    if organism:
                        break

                result_status = map_value_string(entry.get('valueString', ''))
                if not organism and 'bottle:' in entry.get('valueString', ''):
                    organism = entry['valueString'].split('bottle:')[1]

                df = pd.concat([df, pd.DataFrame([{
                    'FHIR': patient['FHIR'],
                    'MRN': patient['MRN'],
                    'CultureeffectiveDateTime': entry.get('effectiveDateTime'),
                    'cultureresults': result_status,
                    'specimenID': entry.get('specimen', {}).get('reference', '').split('Specimen/')[-1],
                    'Organism': organism,
                    'Susceptibility': susceptible,
                    'Resistant': resistant
                }])], ignore_index=True)

            except Exception as e:
                if debug:
                    print(f"[EXCEPTION] Observation {obs_id}: {e}")
                continue

        df = df[df['cultureresults'] == 'Positive']
        df.drop_duplicates(subset=['FHIR', 'MRN', 'CultureeffectiveDateTime', 'cultureresults'], inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

