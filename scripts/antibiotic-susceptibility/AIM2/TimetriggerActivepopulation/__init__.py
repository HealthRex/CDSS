import datetime
import logging
import os
import requests
import pytz
import random
import threading
import traceback
import azure.functions as func 
import pdb
import sys
import subprocess
from utils import utils, cosmos

LOCAL_DEV = True

deployed_unit_ids=['2000233', '2000327', '2000252','2000263','2000262','2000258','2000261','2000250','2000273',
'2000241','2000251','2000253','2000224','2000231','2000237','2000211','120201004','120201003','120201002','120201001',
'110100003','110100004','110100005','110100007','110100008','110100009','110100011','110100012','110100013','110100015',
'110100016','110100017']
deployed_unit_names=[ "H1","G1","EGR","E3", "E2-ICU","E2-AAU","E1","DGR","D3","D2","D1","C3","C2","B3","B2","B1","3 WEST PLEASANTON",
"2 WEST PLEASANTON","2 NORTH PLEASANTON","1 WEST PLEASANTON","J5","J6","J7","K5","K6","K7","L5","L6","L7","M5","M6","M7"] 


model_path = "Aim1_b_5abxmodel"  # Adjust the model path for local development

"""
This module contains the main function for the Azure Function Timer Trigger.
It retrieves a list of patients in specified units, processes each patient to retrieve their identifiers,   
and makes HTTP requests to a specified function URL to get inference data.
It also includes error handling and logging for API requests.
"""
def main(timerevent: func.TimerRequest) -> None:
    pacific_timezone = pytz.timezone("America/Los_Angeles")
    timestamp = datetime.datetime.now(pacific_timezone).strftime("%Y-%m-%dT%H:%M:%Z")

    if timerevent.past_due:
        logging.info("The timer is past due!")
    
    patient_list = utils.get_patients_in_unit(unit_ids=deployed_unit_ids, unit_names=deployed_unit_names)
    def process_patient_list(patient_id_list):
        if LOCAL_DEV:
            function_url = "http://localhost:7071/api/HttpTriggerInference" # the defult of function URL locally
        else: 
            function_url = "" # replace with real URL once you have deployed it, SHC team will help you with this
            
        for patient in patient_id_list:
            patient_identifiers = utils.get_patient_identifiers(patient["CSN"],"CSN")
            patient.update(patient_identifiers)

            #patient_identifiers = utils.get_patients_EPIs(patient["MRN"],"MRN")
            #patient.update(patient_identifiers)

            
            for retry in range(6):
                try:
                    headers = {"Content-Type": "application/json; charset=utf-8"}
                    params = {
                            "FHIR": patient["FHIR"],
                            "FHIR STU3": patient["FHIR STU3"],
                            "CSN": patient["CSN"], 
                            "BeddingUnit": patient["BeddingUnit"], # ward information
                            "MRN": patient["MRN"],
                            "SHCMRN": patient["SHCMRN"],
                            "DOB": patient["DOB"],
                            "Gender": patient["Gender"],
                            "RoomAndBedName": patient["RoomAndBedName"]
                        }
                    response = requests.get(function_url, headers=headers, params=params, timeout=900) # 15 minutes timeout
                    
                    if response.status_code == 200: #If succeed, just break
                        break
                    else:
                        if retry==5:
                            error=patient['SHCMRN']
                            Patient_Inference_Error_dict = {
                                    "API": function_url,
                                    "Error": error,
                                    "Time": timestamp,
                                    "model": "partition_key",
                                }
                            cosmos.cosmoswrite(
                                    patient=Patient_Inference_Error_dict,
                                    container_id='Model_APIErrors', # update the container name if needed
                                    partition_key="PartitionKey" # update the partition key if needed
                                )
                except:
                    error=patient['SHCMRN']
                    Patient_Inference_Error_dict = {
                            "API": function_url,
                            "Error": error,
                            "Time": timestamp,
                            "model": "partition_key",
                        }
                    cosmos.cosmoswrite(
                            patient=Patient_Inference_Error_dict,
                            container_id='Model_APIErrors', # update the container name if needed
                            partition_key="PartitionKey" # update the partition key if needed
                        )
           
        
    num_threads =20 if not LOCAL_DEV else 1
    # Shuffle and split the patient list into chunks for each thread
    def shuffle_split(id_list, num_chunks):
        random.shuffle(id_list)
        chunks = []
        len_per_chunk = 1+len(id_list)//num_chunks
        for i in range(num_chunks):
            chunks.append(id_list[len_per_chunk*i:min(len(id_list), len_per_chunk*(i+1))])
        return chunks
    
    patient_chunks = shuffle_split(patient_list, num_threads)
    
    if LOCAL_DEV:
        process_patient_list(patient_chunks[0])  # Process the first chunk directly for local testing
    else:
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=process_patient_list, args=(patient_chunks[i],), name=f"Thread-{i+1}")
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    logging.info("Python timer trigger function ran at %s", timestamp)
