"""
Houses utility functions to read and write to Azure Cosmos
"""
import datetime
import logging
import os
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import pandas as pd
import uuid

"""
Functions to read and write to Azure Cosmos DB
"""
def getcosmoscores(date1, date2, container_id, partition_key, final_info_only=False):
    
    client = cosmos_client.CosmosClient(
        os.environ["COSMOS_HOST"], os.environ["COSMOS_KEY"]
    )
    
    # setup database for this sample
    try:
        db = client.create_database(id=os.environ["COSMOS_DB_ID"])
        print("Database with id '{0}' created".format(os.environ["COSMOS_DB_ID"]))
    except exceptions.CosmosResourceExistsError:
        db = client.get_database_client(os.environ["COSMOS_DB_ID"])
        print("Database with id '{0}' was found".format(os.environ["COSMOS_DB_ID"]))
    try:
        container = db.create_container(
            id=container_id, partition_key=PartitionKey(path="/ComponentInferenceHttpTrigger_20240229_combinedpkl")
        )#
        print("Container with id '{0}' created".format(container_id))

    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(container_id)
        print("Container with id '{0}' was found".format(container_id))    
    return get_inference_packet(container, date1, date2, partition_key, final_info_only)


def get_epic_order(patient, partition_key,container_id):
    order1 = {
        "id": datetime.datetime.now().strftime("%c") + (str(uuid.uuid4()).replace('-', '')),
        "partitionKey": partition_key,
        "orderid": "None",
        "order_date": datetime.datetime.now().strftime("%c"),
        "patient": patient,
        "container_id":container_id,
    }
    logging.info(f"order1: {order1} End order1")
    return order1


def create_item(container, patient, partition_key):
    epic_patient = get_epic_order(patient, partition_key)
    container.create_item(body=epic_patient)

def cosmoswrite(patient, container_id, partition_key):
    def write_to_file(file_path, content):
        import json
        with open(file_path, 'a') as file:
            file.write(json.dumps(content) + '\n')

    client = cosmos_client.CosmosClient(
        os.environ["COSMOS_HOST"], os.environ["COSMOS_KEY"]
    )
    try:
        db = client.create_database(id=os.environ["COSMOS_DB_ID"])
        print("Database with id '{0}' created".format(os.environ["COSMOS_DB_ID"]))
    except exceptions.CosmosResourceExistsError:
        db = client.get_database_client(os.environ["COSMOS_DB_ID"])
        print("Database with id '{0}' was found".format(os.environ["COSMOS_DB_ID"]))

    # setup container for this sample
    try:
        container = db.create_container(
            id=container_id, partition_key=PartitionKey(path="/ComponentInferenceHttpTrigger_20240229_combinedpkl")
        )
        print("Container with id '{0}' created".format(container_id))
    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(container_id)
        print("Container with id '{0}' was found".format(container_id))
    create_item(container, patient, partition_key)
    