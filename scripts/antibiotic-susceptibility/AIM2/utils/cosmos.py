import datetime
import logging
import os

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import pandas as pd
import uuid

def get_epic_order(patient, partition_key,container_id):
    """
    Given a patient dictionary, a partition key, and a container id, creates
    an epic order dictionary to write to cosmos.
    Args:
        patient: dictionary of patient data
        partition_key: string to identify the model that this inference relates  to
        container_id: string to identify the cosmos container to write to
    Returns:
        epic_order: dictionary of data to write to cosmos
    """
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
    """
    Given a container, a patient dictionary, and a partion key, creates the
    item
    Args:
        container: cosmos container object
        patient: dictionary of patient data
        partition_key: string to identify the model that this inference relates  to
    Returns:
        None
    """
    epic_patient = get_epic_order(patient, partition_key,container)
    container.create_item(body=epic_patient)


def cosmoswrite(patient, container_id, partition_key):
    """
    Base funtion to call that enables us to write an inference packet
    to cosmos.
    Args:
        patient: a dictionary of items to write to cosmos
        container_id: cosmos container, typically unique to a cohort
        partition_key: a string indicating partition to write to. Partition key
        is unique to a task (perhaps multiple tasks per cohort)
    """
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

    # setup container for this sample
    try:
        container = db.create_container(
            id=container_id, partition_key=PartitionKey(path="/PartitionKey")
        )
        print("Container with id '{0}' created".format(container_id))

    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(container_id)
        print("Container with id '{0}' was found".format(container_id))

    create_item(container, patient, partition_key)
