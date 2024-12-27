"""
Definition of DeploymentContainer
"""
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
from datetime import date, datetime, timedelta
from dateutil.parser import parse
import xml.etree.ElementTree as ET
from tqdm import tqdm
import pickle

import pdb

RACE_MAPPING = {
    'White': 'White',
    'Asian': 'Asian',
    'Other': 'Other',
    'Black or African American': 'Black',
    'Declines to State': 'Unknown',
    'Unknown': 'Unknown',
    'Native Hawaiian or Other Pacific Islander': 'Pacific Islander',
    'American Indian or Alaska Native': 'Native American',
    '': 'missing',
}


class DeploymentContainer(object):
    """
    A class that holds attributes and methods necessary to construct a feature
    vector using EPIC and FHIR APIs that plugs into a binary classification
    model trained using retrospective clarity data.
    """

    def __init__(self, filepath, credentials, csn,
                 env, cid, fhir_stu3=None, from_fhir=False):
        """
        Args:
            filepath: path to deploy config file saved by model trainer.
                includes: 'model', 'feature_order', 'bin_map', 'feature_config'
            credentials: stores user and password and client id for API calls
            csn: to identify the patient for whom we wish to do inference
            env: prefix to all the EPIC and FHIR apis which also specifies
                the env (ie SUPW, SUPM, POC etc)
            cid: client id for api calls
            fhir_stu3: the fhir_stu3 id of the patient
            from_fhir: if true, must provide fhir_stu3, and inference performed
                using this id instead of csn [debugging]
        """
        self.credentials = credentials
        self.filepath = filepath
        self.csn = csn
        self.client_id = cid
        with open(filepath, 'rb') as f:
            self.deploy = pickle.load(f)
        self.clf = self.deploy['model']
        self.feature_types = self.deploy['feature_config']
        self.feature_order = self.deploy['feature_order']
        self.bin_lup = self.deploy['bin_map']
        self.lab_base_names = self.deploy['lab_base_names']
        self.vital_base_names = self.deploy['vital_base_names']
        self.api_prefix = env
        self.patient_dict = {'FHIR STU3': fhir_stu3}
        self.from_fhir = from_fhir
        if self.from_fhir:
            assert fhir_stu3 is not None

    def __call__(self, feature_vector=None):
        """
        Get's all necessary features, inputs feature vector into model, returns
        a score.
        """
        if feature_vector is None:
            self.get_patient_identifiers()
            self.feature_vector = self.populated_features()
            self.feature_vector = np.array(self.feature_vector).reshape(1, -1)
            if 'transform' in self.deploy:
                self.feature_vector = self.deploy['transform'].transform(
                    self.feature_vector).toarray()
        else:
            self.feature_vector = feature_vector
        score = self.clf.predict_proba(self.feature_vector)[:, 1][0]
        self.patient_dict['score'] = score
        self.patient_dict = self.get_patient_dict()
        return score

    def get_patient_dict(self):
        """
        Returns dictionary containing score, EPI, and feature_vector
        """
        p_dict = {
            'score': self.patient_dict['score'],
            'model': self.filepath,
            'FHIR STU3': self.patient_dict['FHIR STU3'],
            'feature_vector': [float(p) for p in self.feature_vector[0]]
        }
        for key in self.patient_dict:
            if '_error_' in key:
                p_dict[key] = self.patient_dict[key]
        return p_dict

    def get_patient_identifiers(self):
        """
        Populates patient_identifier attribute with EPIC and FHIR identifiers.
        The Rest APIs we'll be using to pull in patient features will require
        different forms of identification for a particular patient.  Here we
        ensure we have all of them.

        Args:
            patient_csn: CSN at index time for patient in question
        """
        if self.from_fhir:
            id_ = self.patient_dict['FHIR STU3']
            id_type = 'FHIR STU3'
        else:
            id_ = self.csn
            id_type = "CSN"
        ReqPatientIDs = requests.get(
            (f"{self.api_prefix}api/epic/2010/Common/Patient/"
             "GETPATIENTIDENTIFIERS/Patient/Identifiers"),
            params={'PatientID': id_, 'PatientIDType': id_type},
            headers={'Content-Type': 'application/json; charset=utf-8',
                     'Epic-Client-ID': self.client_id},
            auth=HTTPBasicAuth(self.credentials["username"],
                               self.credentials["password"])
        )
        patient_json = json.loads(ReqPatientIDs.text)
        for id_load in patient_json["Identifiers"]:
            self.patient_dict[id_load["IDType"]] = id_load["ID"]

    def populated_features(self):
        """
        Extracts a feature vector for the observation ordered according to
        model specifications.
        Returns:
            feature_vector
        """
        if 'Diagnoses' in self.feature_types['Categorical']:
            # print("Featurizing diagnoses")
            self._get_diagnosis_codes()
        if 'Medications' in self.feature_types['Categorical']:
            # print("Featurizing medications")
            self._get_medications()
        if 'LabResults' in self.feature_types['Numerical']:
            # print("Featurizing lab results")
            self._get_lab_results()
        if 'Vitals' in self.feature_types['Numerical']:
            # print("Featurizing vital signs")
            self._get_vital_signs()

        # Handle individual demographic attribute config in helper
        if 'Age' in self.feature_types['Numerical']:
            # print('Featurizing demographics')
            self._get_demographics()

        # Create feature vector from patient dictionary
        feature_vector = []
        for feature in self.feature_order:
            if feature in self.patient_dict:
                feature_vector.append(self.patient_dict[feature])
            else:
                feature_vector.append(0)

        return feature_vector

    def _get_diagnosis_codes(self):
        """
        Pulls diagnosis codes (ICD10) that were recorded in a patients problem
        list. using EPIC `Condition` API. This is distinct from pulling all
        ICD codes assigned to the patient.

        TODO: figure out overlap between what this returns and what is in our
        clarity extract
        """
        patient_problem_request = requests.get(
            f"{self.api_prefix}api/FHIR/STU3/Condition",
            params={'patient': self.patient_dict['FHIR STU3'],
                    'clinical-status': 'active,inactive,resolved'},
            headers={'Content-Type': 'application/json; charset=utf-8',
                     'Epic-Client-ID': self.client_id},
            auth=HTTPBasicAuth(self.credentials["username"],
                               self.credentials["password"])
        )

        patient_problem_dict = xmltodict.parse(patient_problem_request.text)
        if 'Bundle' not in patient_problem_dict:  # Some patients restricted
            print('no entries')
            return
        # only one item
        if type(patient_problem_dict['Bundle']['entry']) == \
                collections.OrderedDict:  # otherwise no result
            print("just one entry")
            if "Condition" in patient_problem_dict['Bundle']['entry'][
                'resource']:
                code = patient_problem_dict['Bundle']['entry']['resource'][
                    'Condition']['code']['coding'][0]['code']['@value']
                self.patient_dict[code] = 1
        else:
            print("many entries")
            for key in tqdm(patient_problem_dict['Bundle']['entry']):
                code = key['resource'][
                    'Condition']['code']['coding'][0]['code']['@value']
                if code not in self.patient_dict:
                    self.patient_dict[code] = 1
                else:
                    self.patient_dict[code] += 1

    def _get_medications(self):
        """
        Pulls patient medications (current and discontinued) from their medical
        history with using look back window from deploy config file. Populates
        the patient dictionary with the medication names.

        TODO: this is seemingly only letting me return 1000 entries. They are
        not ordered by time, worried I'm only getting a sample of all existing
        orders during my look back window.  Can I control max entries?
        """
        params = {
            'patient': self.patient_dict['FHIR'],
        }
        request_results = requests.get(
            f"{self.api_prefix}api/FHIR/R4/MedicationRequest",
            params=params,
            headers={'Epic-Client-ID': self.client_id},
            auth=HTTPBasicAuth(self.credentials["username"],
                               self.credentials["password"])
        )
        med_dict = xmltodict.parse(request_results.text)

        # No result
        if "Bundle" not in med_dict:
            return

        # One or no results
        if type(med_dict['Bundle']['entry']) == collections.OrderedDict:
            if "MedicationRequest" in med_dict['Bundle']['entry']['resource']:
                med_name = med_dict['Bundle']['entry']['resource'][
                    'MedicationRequest']['medicationReference']['display'][
                    '@value']
                order_time = med_dict['Bundle']['entry']['resource'][
                    'MedicationRequest']['authoredOn']['@value']
                try:
                    order_date_time = datetime.strptime(
                        order_time, '%Y-%m-%dT%H:%M:%SZ')
                except:
                    order_date_time = datetime.strptime(order_time, '%Y-%m-%d')

                look_back = self.feature_types['Categorical']['Medications'][0
                ]['look_back']
                max_time_delta = timedelta(days=look_back)
                if datetime.now() - order_date_time <= max_time_delta:
                    self.patient_dict[med_name] = 1
            return

        # Multiple results
        for entry in tqdm(med_dict['Bundle']['entry']):
            med_name = entry['resource'][
                'MedicationRequest']['medicationReference']['display']['@value']
            order_time = entry['resource'][
                'MedicationRequest']['authoredOn']['@value']
            try:
                order_date_time = datetime.strptime(
                    order_time, '%Y-%m-%dT%H:%M:%SZ')
            except:
                order_date_time = datetime.strptime(order_time, '%Y-%m-%d')

            look_back = self.feature_types['Categorical']['Medications'][0][
                'look_back']
            max_time_delta = timedelta(days=look_back)
            if datetime.now() - order_date_time <= max_time_delta:
                if med_name in self.patient_dict:
                    self.patient_dict[med_name] += 1
                else:
                    self.patient_dict[med_name] = 1

    def _get_demographics(self):
        """
        Calls `GETPATIENTDEMOGRAPHICS` EPIC API and populates patient_dict
        attribute with demographic information (age, sex, race).
        """

        def calculate_age(born):
            today = date.today()
            return today.year - born.year - ((today.month, today.day)
                                             < (born.month, born.day))

        request_results = requests.get(
            (f'{self.api_prefix}api/epic/2010/Common/Patient/'
             'GETPATIENTDEMOGRAPHICS/Patient/Demographics'),
            params={'PatientID': self.patient_dict['FHIR STU3'],
                    'PatientIDType': 'FHIR STU3'},
            headers={'Content-Type': 'application/json; charset=utf-8',
                     'Epic-Client-ID': self.client_id},
            auth=HTTPBasicAuth(self.credentials["username"],
                               self.credentials["password"])
        )

        demographic_json = json.loads(request_results.text)

        # Get binned age
        if 'Age' in self.feature_types['Numerical']:
            self.patient_dict["DOB"] = parse(demographic_json["DateOfBirth"])
            self.patient_dict["Age"] = calculate_age(self.patient_dict["DOB"])
            bin = self._get_bin('Age', self.patient_dict['Age'])
            self.patient_dict[bin] = 1

        # Sex features: note EPICs naming convention (gender) is inappropriate.
        if 'Sex' in self.feature_types['Categorical']:
            self.patient_dict[f"sex_{demographic_json['Gender']}"] = 1

        # Race features
        if 'Race' in self.feature_types['Categorical']:
            race_mapped = RACE_MAPPING[demographic_json['Race'].split('^')[0]]
            self.patient_dict[f"race_{race_mapped}"] = 1

    def _get_lab_results(self):
        """
        Pulls lab results data for desired base_name component using
        `GETPATIENTRESULTCOMPONENTS` API. Finds the bins it should be associated
        with and populates the patient_dict attribute in bag of words fashion.

        Ex: if base_name is HCT, and we pull one value of 23.6 corresponding to
        the 0th bin then self.patient_dict[HCT_0] will be populated with 1.
        """
        look_back = self.feature_types['Numerical']['LabResults'][0
        ]['look_back']
        for base_name in tqdm(self.lab_base_names):
            lab_result_packet = {
                "PatientID": self.patient_dict['FHIR STU3'],
                "PatientIDType": "FHIR STU3",
                "UserID": self.credentials["username"].split('$')[-1],
                "UserIDType": "External",
                "NumberDaysToLookBack": look_back,
                "MaxNumberOfResults": 200,
                "FromInstant": "",
                "ComponentTypes":
                    [{"Value": base_name, "Type": "base-name"}]
            }
            lab_component_packet = json.dumps(lab_result_packet)
            lab_component_response = requests.post(
                (f'{self.api_prefix}api/epic/2014/Results/Utility/'
                 'GETPATIENTRESULTCOMPONENTS/ResultComponents'),
                headers={
                    'Content-Type': 'application/json; charset=utf-8',
                    'Epic-Client-ID': self.client_id
                },
                auth=HTTPBasicAuth(self.credentials["username"],
                                   self.credentials["password"]),
                data=lab_component_packet
            )
            numeric = '0123456789-.'
            lab_response = json.loads(lab_component_response.text)
            if lab_response["ResultComponents"]:  # not none
                for i in range(len(lab_response["ResultComponents"])):
                    if lab_response["ResultComponents"][i]["Value"] is None:
                        continue
                    value = lab_response["ResultComponents"][i]["Value"][0]
                    # Convert to numeric
                    num_value = ''
                    for i, c in enumerate(value):
                        if c in numeric:
                            num_value += c
                    try:
                        value = float(num_value)
                        binned_lab_val = self._get_bin(base_name, value)
                        if binned_lab_val not in self.patient_dict:
                            self.patient_dict[binned_lab_val] = 1
                        else:
                            self.patient_dict[binned_lab_val] += 1
                    except:
                        # Log parsing error in patient dictionary
                        self.patient_dict[f"{base_name}_error_{i}"] = value

    def _get_vital_signs(self, api_prefix, look_back=72):
        """
        TODO : Finish implementing this (need it working in SUPD to be able
        to test it)
        ID 5 : BLOOD PRESSURE
        ID 6 : TEMPERATURE
        ID 8 : PULSE
        ID 9 : RESPIRATIONS
        ID 10 : SPO2 (PULSE OXIMETRY)

        Gets binned vitals sign features and appends to patient_dict attribute
        in bag of words fashion. Calls the `GETFLOWSHEETROWS` API

        Args:
            api_prefix : prefix of the API we're going to call
            look_back : max for `GETFLOWSHEETROWS` is 72 hours
        """

        flowsheet_packet = {
            "PatientID": self.patient_identifiers['EPI'],
            "PatientIDType": "EPI",
            "ContactID": self.patient_identifiers['CSN'],
            "ContactIDType": "CSN",
            "LookbackHours": "72",
            "UserID": "",
            "UserIDType": "",
            "FlowsheetRowIDs": [
                {
                    "ID": "5",
                    "Type": "EXTERNAL"
                }
            ]
        }
        flowsheet_packet = json.dumps(flowsheet_packet)
        flowsheet_response = requests.post(
            (f'{api_prefix}api/epic/2014/Clinical/Patient/'
             'GETFLOWSHEETROWS/FlowsheetRows'),
            headers={'Content-Type': 'application/json; charset=utf-8',
                     'Epic-Client-ID': self.client_id},
            auth=HTTPBasicAuth(self.credentials["username"],
                               self.credentials["password"]),
            data=flowsheet_packet
        )
        flowsheet_data = json.loads(flowsheet_response.text)
        
    def _get_bin(self, feature_name, value):
        """
        Given the numerical value for a feature, consults the feature_bin_map
        attribute to find the appropriate bin for said feature and the bag
        of words style name ie `{feature}_{binNumber}`

        Args:
            feature_name : name of the numerical feature
            value : floating point associated with value of feature

        Returns:
            feature : `{feature}_{binNumber}`
                ex: if hematocrit in the 5th bin then HCT_4
        """
        min_list = self.bin_lup[self.bin_lup['feature'] == feature_name].values[0]
        min_list = min_list[1:]  # pop first element which is feature name

        for i, m in enumerate(min_list):
            if value < m:
                return f"{feature_name}_{i}"

        return f"{feature_name}_{len(min_list)}"
