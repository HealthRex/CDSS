import logging
import json
import azure.functions as func
import pickle
import traceback
import requests
from requests.auth import HTTPBasicAuth
from . import cosmos
from . import deploy


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    CSN = req.params.get('CSN')
    if not CSN:
        return func.HttpResponse(
            'This function executed unsuccessfully. No Score was processed.',
            status_code=400
        )
    ENV = req.params.get('EPICENV')
    if not ENV:
        return func.HttpResponse(
            "Function unsuccessful. Epic Environment is missing.",
            status_code=400
        )

    CID = req.params.get('ClientID')
    if not CID:
        return func.HttpResponse(
            "Function unsuccessful. param: ClientID is missing.",
            status_code=400)

    with open('HemeStampModel/credentials.confg') as json_file:
        creds = json.load(json_file)
    logging.info('loaded creds from file')

    models = [
        '20220630_label_hemestamp_deploy.pkl',
    ]
    get_features = True
    for model in models:
        dp = deploy.DeploymentContainer(
            filepath=f'HemeStampModel/{model}',
            credentials=creds,
            csn=CSN,
            env=ENV,
            cid=CID
        )
        dp.get_patient_identifiers()
        FHIR_ID = dp.patient_dict['FHIR']
        try:
            if get_features:
                score = dp()
                feature_vector = dp.feature_vector
                get_features = False
                dp.patient_dict['FHIR ID'] = FHIR_ID
                cosmos.cosmoswrite(
                    patient=dp.patient_dict,
                    partition_key=model)
                score_success = True
            else:
                score = dp(feature_vector)
                dp.patient_dict['FHIR ID'] = FHIR_ID
                cosmos.cosmoswrite(
                    patient=dp.patient_dict,
                    partition_key=model)

        except Exception as e:
            dp.get_patient_identifiers()
            error_dict = {
                'FHIR ID' : dp.patient_dict['FHIR'],
                'FHIR STU3': dp.patient_dict['FHIR STU3'],
                'Error': traceback.format_exc(),
                'model': model
            }
            cosmos.cosmoswrite(patient=error_dict,
                               partition_key=model)
            score_success = False
    if score_success:
        return func.HttpResponse(
            f"Hello, {score}. This function executed successfully.")
    else:
        return func.HttpResponse(
            "This function executed successfully. No Score was processed.",
            status_code=200
        )
