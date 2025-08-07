import os
from turtle import pd
import pandas as pdas
import requests
from requests.auth import HTTPBasicAuth
import json
"""
Utility functions to interact with Epic FHIR and REST APIs
"""
def get_patients_EPIs(patient_id, patient_id_type):
    params = {'identifier': patient_id,
              '_format': 'json'}
    fhir_id_request = requests.get(
        f"{os.environ['EPIC_ENV']}api/FHIR/R4/Patient",
        params=params,
         headers={
            "Content-Type": "application/json; charset=utf-8",
            "Epic-Client-ID": os.environ["EPIC_CLIENT_ID"],
        },
        auth=HTTPBasicAuth(os.environ["secretID"], os.environ["secretpass"]),
    )
    fhir_id_dict = json.loads(fhir_id_request.text)

    if len(fhir_id_dict['entry']) > 1:
        for value in fhir_id_dict['entry'][1:]:
            if 'id' in value['resource']:
                print(f"Unable to identify single FHIR ID for MRN {patient_id}")

    fhir_id = fhir_id_dict['entry'][0]['resource']['id']
    return fhir_id

def get_patient_identifiers(patient_id, patient_id_type):
    ReqPatientIDs = requests.get(
        (
            f"{os.environ['EPIC_ENV']}api/epic/2010/Common/Patient/"
            "GETPATIENTIDENTIFIERS/Patient/Identifiers"
        ),
        params={"PatientID": patient_id, "PatientIDType": patient_id_type},
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Epic-Client-ID": os.environ["EPIC_CLIENT_ID"],
        },
        auth=HTTPBasicAuth(os.environ["secretID"], os.environ["secretpass"]),
    )
    patient_json = json.loads(ReqPatientIDs.text)
    patient_dict = {}
    for id_load in patient_json["Identifiers"]:
        patient_dict[id_load["IDType"]] = id_load["ID"]
    return patient_dict


def get_patients_in_unit(unit_ids=[], unit_names=[]):
    """
    Returns a list of patient in certain units, all POC
    """
    if not isinstance(unit_ids, list):
        unit_ids = [unit_ids]
        unit_names = [unit_names]
    
    PatientList = []
    def get_patients_in_single_unit(unit_id, unit_name):
        UnitJSONresp = requests.get(
            f"{os.environ['EPIC_ENV']}api/epic/2012/Access/Patient/GETCENSUSBYUNIT/UnitCensus",
            params={"UnitID": unit_id},
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Epic-Client-ID": os.environ["EPIC_CLIENT_ID"],
            },
            auth=HTTPBasicAuth(os.environ["secretID"], os.environ["secretpass"]),
        )
        UnitJSON = json.loads(UnitJSONresp.text)
        for key in UnitJSON["BeddedPatients"]:
            Patient = {}
            Patient["BeddingUnit"] = unit_name
            Patient["FirstName"] = key["FirstName"]
            Patient["LastName"] = key["LastName"]
            Patient["MiddleName"] = key["MiddleName"]
            Patient["Gender"] = key["Sex"]
            Patient["DOB"] = key["DateOfBirth"]
            Patient["RoomAndBedName"] = key["RoomAndBedName"]
            for value in key["PatientIDs"]:
                Patient[value["Type"]] = value["ID"]
            
            for value in key['ContactIDs']:
                Patient[value["Type"]] = value["ID"]
            
            PatientList.append(Patient)

    for idx in range(len(unit_ids)):
        get_patients_in_single_unit(unit_ids[idx], unit_names[idx])
    print('**************PatientList*****************',len(PatientList))
    return PatientList
