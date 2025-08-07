import datetime
import logging
import os
import numpy
import requests
from . import cosmos
from requests.auth import HTTPBasicAuth
from urllib.error import HTTPError
import pytz
import azure.functions as func
import traceback
from .deployer import NgboostDeployer
from .feature_engineering import feature_engineering
from scipy.stats import norm
import pickle
import json

LOCAL_DEV = True

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    if LOCAL_DEV:
        model_path = "5_Most_CommonABX.pkl"
    else:
        model_path = "NA"   # add your model path here once you have deployed it 


    # Set pacific time zone
    pacific_timezone = pytz.timezone("America/Los_Angeles")
    date = datetime.datetime.now(pacific_timezone).strftime("%Y-%m-%dT%H:%M:%S")

    Feature_dict = feature_engineering(
            credentials={
                "username": os.environ["secretID"],
                "password": os.environ["secretpass"],
            },
            env=os.environ["EPIC_ENV"],
            client_id=os.environ["EPIC_CLIENT_ID"],
            patient_dict=dict(req.params)
        )

    Feature_vector = Feature_dict()
    """
    This part of code is not test yet as we still working on the feature engineering
    """
    # load model
    EmpricABX_model = EmpricABX(
        modelpath=model_path,
        credentials={
            "username": os.environ["secretID"],
            "password": os.environ["secretpass"],
        },
        env=os.environ["EPIC_ENV"],
        client_id=os.environ["EPIC_CLIENT_ID"],
        databricks_endpoint=None,
    )
    score_dict = EmpricABX_model(feature_vector=Feature_vector)
    logging.info(f"score_dict: {score_dict}")

    # write to cosmos
    try:
        patient_dict = dict(req.params)
        patient_dict.update(score_dict)
        patient_dict["inference_date"] = date
        partition_key = 'PartitionKey' # add your partition key here
        container_id = 'ModelInference' # add your container id here
        cosmos.cosmoswrite(patient=patient_dict, container_id=container_id, partition_key=partition_key)
    
    except Exception as e:
        return func.HttpResponse(
            f"Error writing to cosmos: {e}",
            status_code=500
        )