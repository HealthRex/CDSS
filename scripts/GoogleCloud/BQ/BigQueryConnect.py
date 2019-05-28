'''
TODO: still work-in-progress

connect to BQ using json token
create new dataset
create new table
create new table by uploading CSV
'''

from google.cloud import bigquery
#from google.cloud import storage
from google.cloud.exceptions import NotFound

from typing import List
from pathlib import Path

class BigQueryConnect():
    '''
    setup credentials: export GOOGLE_APPLICATION_CREDENTIALS="<path to json>"
    '''

    def __init__(self):
        self.client = bigquery.Client()
        assert self.client is not None, 'Did not connect to BQ, check credentials env(GOOGLE_APPLICATION_CREDENTIALS)'

    def create_new_dataset(self, dataset_id: str) -> None:
        '''
        https://cloud.google.com/bigquery/docs/datasets#create-dataset

        :param dataset_id: dataset name
        :return: None
        '''

        dataset_ref = self.client.dataset(dataset_id)

        try:
            # Check if the dataset with specified ID already exists
            self.client.get_dataset(dataset_ref)
            print(f'Dataset {dataset_id} already exists! Skipping create operation.')
        except NotFound:
            # Construct a full Dataset object to send to the API.
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = 'US'
            dataset = self.client.create_dataset(dataset)  # API request
            print(f'Dataset {dataset.dataset_id} created successfully project: {self.client.project}.')

    def create_new_table_from_schema(self, dataset_id: str, table_id: str,
                                     schema: List[bigquery.SchemaField]) -> None:
        '''
        https://cloud.google.com/bigquery/docs/tables#create-table

        :param dataset_id: dataset name
        :param table_id: table name
        :param schema:
            schema = [
                bigquery.SchemaField('full_name', 'STRING', mode='REQUIRED', description='blah'),
                bigquery.SchemaField('age', 'INTEGER', mode='REQUIRED'),
            ]
        :return: None
        '''

        dataset_ref = self.client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)

        try:
            self.client.get_table(table_ref)
            print(f'Table {table_id} in dataset {dataset_id} already exists! Skipping create operation.')
        except NotFound:
            # Construct a full Table object to send to the API.
            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)  # API request
            print(
                f'Table {table.table_id} in dataset {dataset_id}'
                f'created successfully project: {self.client.project}.'
            )

    def load_csv_to_table(self, dataset_id: str, table_id: str, csv_path: str, auto_detect_schema: bool = True,
                          schema: List[bigquery.SchemaField] = [], skip_rows: int = 0) -> None:
        '''
        TODO: add functionality for optional schema input
        TODO: what happens if dataset does not exist?

        :param dataset_id: dataset name
        :param table_id: table name
        :param csv_path: path to exported csv file
        :param auto_detect_schema: auto detect schema types from CSV (default True)
        :param schema: (default None)
            schema = [
                bigquery.SchemaField('full_name', 'STRING', mode='REQUIRED', description='blah'),
                bigquery.SchemaField('age', 'INTEGER', mode='REQUIRED'),
            ]
        :param skip_rows: how many rows in CSV to skip (default 0)
        :return: None

        Details on loading local data
        https://cloud.google.com/bigquery/docs/loading-data-local
        '''

        location = 'US'

        dataset_ref = self.client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location

        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.CSV
        job_config.skip_leading_rows = skip_rows
        job_config.autodetect = auto_detect_schema

        with open(csv_path, "rb") as csv_file:
            load_table_job = self.client.load_table_from_file(
                csv_file,
                table_ref,
                location=location,
                job_config=job_config,
            )  # API request

        load_table_job.result() # Wait for load to complete
        table = self.client.get_table(table_ref)

        print(
            f'{load_table_job.output_rows} rows loaded into '
            f'table {table.table_id} in dataset {dataset_id} '
            f'created successfully project: {self.client.project}.'
        )
