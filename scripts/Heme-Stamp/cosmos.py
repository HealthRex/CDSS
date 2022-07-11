import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime
import logging

# import config
settings = {
    'host': 'https://machinelearningoutput.documents.azure.com:443/',
    'master_key': 'LufjB7LUP4aRaDGIRs3NTTdIU440Gv1hlhVV7453HcL1UeJs3oXoj55lPsNmckzZMNEFXSu3oFTe2K3DsxLpZg==',
    'database_id': 'machinelearningdb',
    'container_id': 'machinelearningcontainer'
}
HOST = settings['host']
MASTER_KEY = settings['master_key']
DATABASE_ID = settings['database_id']
CONTAINER_ID = settings['container_id']


def query_items(container):
    print('\nQuerying for an  Item by Partition Key\n')

    # Including the partition key value of account_number in the WHERE filter results in a more efficient query
    items = list(container.query_items(
        query="SELECT * FROM c WHERE c.partitionKey = 'HemeStamp'",
    ))
    return items
    # for item in items:
    #    print(f"Item: {item}")


def query_items_bydate(container, qdate):
    print('\nQuerying for an  Item by Partition Key\n')

    # Including the partition key value of account_number in the WHERE filter results in a more efficient query
    items = list(container.query_items(
        query=f"SELECT * FROM c WHERE c.partitionKey = 'HemeStamp' AND TimestampToDateTime(c._ts*1000) > '{qdate}'",
    ))
    return items


def query_items_between_dates(container, date1, date2):
    print('\nQuerying for an  Item by Partition Key\n')

    # Including the partition key value of account_number in the WHERE filter results in a more efficient query
    items = list(container.query_items(
        query=f"SELECT * FROM c WHERE c.partitionKey = 'HemeStamp' AND TimestampToDateTime(c._ts*1000) >= '{date1}' AND TimestampToDateTime(c._ts*1000) <= '{date2}' ",
    ))
    return items

    # for item in items:
    #    print(f"Item: {item}")


def get_epic_order(patient):
    patient['DOB'] = ''
    order1 = {
        'id': datetime.datetime.now().strftime('%c'),
        'partitionKey': 'HemeStamp',
        'orderid': 'None',
        'order_date': datetime.datetime.now().strftime('%c'),
        'patient': patient
    }
    logging.info(f"order1: {order1} End order1")
    return order1


def create_item(container, patient):
    # farts

    epic_patient = get_epic_order(patient)
    logging.info(epic_patient)

    container.create_item(body=epic_patient)


def getcosmosbetweendate(date1, date2):
    client = cosmos_client.CosmosClient(
        HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    # setup database for this sample
    try:
        db = client.create_database(id=DATABASE_ID)
        print('Database with id \'{0}\' created'.format(DATABASE_ID))

    except exceptions.CosmosResourceExistsError:
        db = client.get_database_client(DATABASE_ID)
        print('Database with id \'{0}\' was found'.format(DATABASE_ID))

    # setup container for this sample
    try:
        container = db.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
        print('Container with id \'{0}\' created'.format(CONTAINER_ID))

    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(CONTAINER_ID)
        print('Container with id \'{0}\' was found'.format(CONTAINER_ID))

    return query_items_between_dates(container, date1, date2)


def getcosmosbydate(qdate):
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart",
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
        container = db.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
        print('Container with id \'{0}\' created'.format(CONTAINER_ID))

    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(CONTAINER_ID)
        print('Container with id \'{0}\' was found'.format(CONTAINER_ID))

    return query_items_bydate(container, qdate)


def getcosmos():
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart",
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
        container = db.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
        print('Container with id \'{0}\' created'.format(CONTAINER_ID))

    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(CONTAINER_ID)
        print('Container with id \'{0}\' was found'.format(CONTAINER_ID))

    return query_items(container)


def cosmoswrite(patient):
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart",
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
        container = db.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
        print('Container with id \'{0}\' created'.format(CONTAINER_ID))


    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(CONTAINER_ID)
        print('Container with id \'{0}\' was found'.format(CONTAINER_ID))

    create_item(container, patient)