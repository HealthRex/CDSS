import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime
import logging
import os

# import config
HOST = os.environ["COSMOS_HOST"]
MASTER_KEY = os.environ["COSMOS_KEY"]
DATABASE_ID = os.environ["DATABASE_ID"]
CONTAINER_ID = os.environ["CONTAINER_ID"]


def query_items(container, partition_key):
    print('\nQuerying for an  Item by Partition Key\n')

    items = list(container.query_items(
        query=f"SELECT * FROM c WHERE c.partitionKey = '{partition_key}'",
    ))
    return items

def query_items_bydate(container, qdate, partition_key):
    print('\nQuerying for an  Item by Partition Key\n')

    query = f"""
    SELECT * FROM c WHERE c.partitionKey = '{partition_key}'
    AND TimestampToDateTime(c._ts*1000) > '{qdate}'
    """
    items = list(container.query_items(
        query=query,
    ))
    return items


def query_items_between_dates(container, date1, date2, partition_key):
    print('\nQuerying for an  Item by Partition Key\n')

    query = f"""
    SELECT * FROM c WHERE c.partitionKey = '{partition_key}' AND 
    TimestampToDateTime(c._ts*1000) >= '{date1}' AND 
    TimestampToDateTime(c._ts*1000) <= '{date2}'"
    """
    items = list(container.query_items(
        query=query
    ))
    return items


def get_epic_order(patient, partition_key):
    """
    Formats the item to save (appends partition key)
    """
    patient['DOB'] = ''
    order1 = {
        'id': datetime.datetime.now().strftime('%c'),
        'partitionKey': partition_key,
        'orderid': 'None',
        'order_date': datetime.datetime.now().strftime('%c'),
        'patient': patient
    }
    logging.info(f"order1: {order1} End order1")
    return order1


def create_item(container, patient, partition_key):
    """
    Given a container, a patient dictionary, and a partion key, creates the
    item
    Args:
        container: instantiated from cosmoswrite
        patient: dictionary of data to save
        partition_key: string to identify the model that this inference relates
            to
    """
    epic_patient = get_epic_order(patient, partition_key)
    container.create_item(body=epic_patient)


def getcosmosbetweendate(date1, date2):
    client = cosmos_client.CosmosClient(
        HOST, {'masterKey': MASTER_KEY},
        user_agent="CosmosDBPythonQuickstart",
        user_agent_overwrite=True)
    # setup database for this sample
    try:
        db = client.create_database(id=DATABASE_ID)
        print('Database with id \'{0}\' created'.format(DATABASE_ID))

    except exceptions.CosmosResourceExistsError:
        db = client.get_database_client(DATABASE_ID)
        print('Database with id \'{0}\' was found'.format(DATABASE_ID))

    # setup container for this sample
    try:
        container = db.create_container(id=CONTAINER_ID,
                                        partition_key=PartitionKey(path='/partitionKey'))
        print('Container with id \'{0}\' created'.format(CONTAINER_ID))

    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(CONTAINER_ID)
        print('Container with id \'{0}\' was found'.format(CONTAINER_ID))

    return query_items_between_dates(container, date1, date2)


def getcosmosbydate(qdate):
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY},
                                        user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    # setup database for this sample
    try:
        db = client.create_database(id=DATABASE_ID)
        print('Database with id \'{0}\' created'.format(DATABASE_ID))

    except exceptions.CosmosResourceExistsError:
        db = client.get_database_client(DATABASE_ID)
        print('Database with id \'{0}\' was found'.format(DATABASE_ID))

    # setup container for this sample
    try:
        container = db.create_container(id=CONTAINER_ID,
                                        partition_key=PartitionKey(path='/partitionKey'))
        print('Container with id \'{0}\' created'.format(CONTAINER_ID))

    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(CONTAINER_ID)
        print('Container with id \'{0}\' was found'.format(CONTAINER_ID))

    return query_items_bydate(container, qdate)


def getcosmos():
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY},
                                        user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    # setup database for this sample
    try:
        db = client.create_database(id=DATABASE_ID)
        print('Database with id \'{0}\' created'.format(DATABASE_ID))

    except exceptions.CosmosResourceExistsError:
        db = client.get_database_client(DATABASE_ID)
        print('Database with id \'{0}\' was found'.format(DATABASE_ID))

    # setup container for this sample
    try:
        container = db.create_container(id=CONTAINER_ID,
                                        partition_key=PartitionKey(path='/partitionKey'))
        print('Container with id \'{0}\' created'.format(CONTAINER_ID))

    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(CONTAINER_ID)
        print('Container with id \'{0}\' was found'.format(CONTAINER_ID))

    return query_items(container)


def cosmoswrite(patient, partition_key):
    """
    Base funtion to call that enables us to write an inference packet
    to cosmos.
    Args:
        patient: a dictionary of items to write to cosmos
        partition_key: a string indicating partition to write to. General
            rule of thumb is that each new instantation of a model should
            get its own partition key. ex: 20220705_label_hct.
    """
    client = cosmos_client.CosmosClient(
        HOST, {'masterKey': MASTER_KEY},
        user_agent="CosmosDBPythonQuickstart",
        user_agent_overwrite=True)

    # setup database for this sample
    try:
        db = client.create_database(id=DATABASE_ID)
        print('Database with id \'{0}\' created'.format(DATABASE_ID))

    except exceptions.CosmosResourceExistsError:
        db = client.get_database_client(DATABASE_ID)
        print('Database with id \'{0}\' was found'.format(DATABASE_ID))

    # setup container for this sample
    try:
        container = db.create_container(id=CONTAINER_ID,
                                        partition_key=PartitionKey(path='/partitionKey'))
        print('Container with id \'{0}\' created'.format(CONTAINER_ID))

    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(CONTAINER_ID)
        print('Container with id \'{0}\' was found'.format(CONTAINER_ID))

    create_item(container, patient, partition_key)
