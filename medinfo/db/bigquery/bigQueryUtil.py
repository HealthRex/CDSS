'''
create a BigQuery connection object
    need to set PATH_TO_GCP_TOKEN in LocalEnv

client object methods
    connect to BQ using json token
    create new dataset
    create new table
    create new table by uploading CSV
    create schema/table-type from postgres /d <db> output
    get row count of table
    get query result
'''

from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.cloud.bigquery import dbapi

from medinfo.dataconversion.Util import log
import LocalEnv

import re
import time
import os
import csv

PATH_TO_GCP_TOKEN = LocalEnv.PATH_TO_GCP_TOKEN
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = PATH_TO_GCP_TOKEN

def connection( client=None ):
    '''
    use this to create a BQ connection object
             to use functions from DBUtil

    in BQ, close() and commit() are no-op

    client does not need to be specified
    '''
    conn = dbapi.connect(client)
    return conn

def headerChecker(csv_path, header_list):
    with open(csv_path) as f:
        reader = csv.reader(f)
        csv_header = next(reader)

    if csv_header != header_list:
        raise NonMatchingHeadersException('headers from %r do not match' % csv_path)

class NonMatchingHeadersException(Exception):
    pass

class BigQueryClient:
    '''
    methods to perform using client object
    '''

    def __init__(self):
        self.client = bigquery.Client()
        log.info('Did not connect to BQ, check credentials env(GOOGLE_APPLICATION_CREDENTIALS)')
        assert self.client is not None, 'Did not connect to BQ, check credentials env(GOOGLE_APPLICATION_CREDENTIALS)'

    def reconnect_client(self):
        self.client = bigquery.Client()

    def create_new_dataset(self, dataset_id):
        '''
        https://cloud.google.com/bigquery/docs/datasets#create-dataset

        :param dataset_id: dataset name
        :return: None
        '''

        dataset_ref = self.client.dataset(dataset_id)

        try:
            # Check if the dataset with specified ID already exists
            self.client.get_dataset(dataset_ref)
            log.info('Dataset {} already exists! Skipping create operation.'.format(dataset_id))
            #print(f'Dataset {dataset_id} already exists! Skipping create operation.')
        except NotFound:
            # Construct a full Dataset object to send to the API.
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = 'US'
            dataset = self.client.create_dataset(dataset)  # API request
            log.info('Dataset {} created successfully project: {}.'.format(dataset.dataset_id, self.client.project))
            #print(f'Dataset {dataset.dataset_id} created successfully project: {self.client.project}.')

    def create_new_table_from_schema(self, dataset_id, table_id,
                                     schema):
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
            #print(f'Table {table_id} in dataset {dataset_id} already exists! Skipping create operation.')
        except NotFound:
            # Construct a full Table object to send to the API.
            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)  # API request
            log.info('''
                    Table {} in dataset {}
                    created successfully project: {}.
                    '''.format(table.table_id, dataset_id, self.client.project))
            '''
            print(
                f'Table {table.table_id} in dataset {dataset_id}'
                f'created successfully project: {self.client.project}.'
            )
            '''

    def _stream_csv_to_table(self, dataset_id, table_id, csv_path, batch_size = 1000):
        '''
        FYI: Streaming is NOT free :)
        https://cloud.google.com/bigquery/pricing#streaming_pricing
        TODO: 06/03/2019 NOT TESTED, DO NOT USE THIS FUNCTION

        :param dataset_id: dataset name
        :param table_id: table name
        :param csv_path: path to CSV from SQL
        :param batch_size: rows per insert (default 1000)
        :return: None
        '''

        table_ref = self.client.dataset(dataset_id).table(table_id)
        table = self.client.get_table(table_ref)  # API request

        with open(csv_path, 'w') as infile, open(csv_path + '_errors', 'w') as outfile:
            for line in infile:
                rows_to_insert = []
                row = line.split(',')
                # TODO validate row
                rows_to_insert.append(row)

                if len(rows_to_insert) == batch_size:
                    errors = self.client.insert_rows(table, rows_to_insert)  # API request
                    assert errors == []
                    rows_to_insert = []

            if rows_to_insert:
                errors = self.client.insert_rows(table, rows_to_insert)  # API request
                assert errors == []

    def load_csv_to_table(self, dataset_id, table_id, csv_path, auto_detect_schema = True,
                          schema = [], skip_rows = 0, append_to_table=False):
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
        # https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-csv#overwriting_a_table_with_csv_data
        #job_config.write_disposition = bigquery.WriteDisposition.WRITE_EMPTY
        job_config.skip_leading_rows = skip_rows
        job_config.quote_character = '\"'


        if not append_to_table:
            job_config.write_disposition = bigquery.WriteDisposition.WRITE_EMPTY

            if auto_detect_schema:
                assert schema == [], 'Auto-detect is False, but schema is specified'
                job_config.autodetect = True
            else:
                job_config.autodetect = False
                assert schema != [], 'Auto-detect is False, but no schema specified'
                job_config.schema = schema


        with open(csv_path, 'rb') as csv_file:
            load_table_job = self.client.load_table_from_file(
                csv_file,
                table_ref,
                location=location,
                job_config=job_config,
            )  # API request

        log.info('Uploading table... ')
        #print('Uploading table... ')
        try:
            load_table_job.result() # Wait for load to complete
        except:
            errors = load_table_job.errors
            log.error(errors)
            return errors
        #print(load_table_job.error_result)
        table = self.client.get_table(table_ref)
        log.info('''
                {} rows loaded into 
                table {} in dataset {}
                in project: {}.
                '''.format(load_table_job.output_rows, table.table_id, dataset_id, self.client.project))
        '''
        print(
            f'{load_table_job.output_rows} rows loaded into '
            f'table {table.table_id} in dataset {dataset_id} '
            f'in project: {self.client.project}.'
        )
        '''

    def read_table_types(self, table_types_path):
        '''
        reads in lines, deliminited by "|", e.g.:
        <column name> | <data type> | <collation> | <nullable> | <default>

        :param table_types_path:
        :return: list of bigquery.SchemaField
        '''

        type_mapping = {
            'TINYINT'   : 'INT64',
            'SMALLINT'  : 'INT64',
            'MEDIUMINT' : 'INT64',
            'INT'       : 'INT64',
            'INTEGER'   : 'INT64',
            'BIGINT'    : 'INT64',
            'DECIMAL'   : 'NUMERIC',
            'NUMERIC'   : 'NUMERIC',
            'REAL'      : 'FLOAT64',
            'DOUBLE PRECISION': 'FLOAT64',
            'BOOLEAN'   : 'BOOL',
            'CHAR'      : 'STRING',
            'CHARACTER': 'STRING',
            'CHARACTER VARYING': 'STRING',
            'VARCHAR'   : 'STRING',
            'BYTEA'     : 'BYTES',
            'TINYTEXT'  : 'STRING',
            'TEXT'      : 'STRING',
            'MEDIUMTEXT': 'STRING',
            'LONGTEXT'  : 'STRING',
            'DATE'      : 'DATE',
            'TIME'      : 'TIME',
            'TIMESTAMP' : 'TIMESTAMP',
            'TIMESTAMP WITHOUT TIME ZONE': 'TIMESTAMP'
        }

        schema_fields = []

        with open(table_types_path, 'r') as type_table_f:
            for line in type_table_f:
                column, pg_type, collation, nullable, default = [item.strip() for item in line.split('|')]
                pg_type_ = re.sub(r'\(.*\)', '', pg_type).upper()
                bq_type = type_mapping[pg_type_]
                mode = 'REQUIRED' if nullable == 'not null' else 'NULLABLE'
                schema_fields.append(bigquery.SchemaField(column, bq_type, mode=mode))

        return schema_fields

    def get_row_count(self, full_table_name):

        query_job = self.client.query('SELECT COUNT(*) FROM ' + full_table_name, location='US')
        results = query_job.result()
        results_list = [row for row in results]

        return results_list[0][0]

    def queryBQ(self, query_str, query_params=None, location ='US', batch_mode = False, dry_run = False,
                verbose = False):

        job_config = bigquery.QueryJobConfig()
        job_config.dry_run = dry_run

        if batch_mode:
            # Run at batch priority, which won't count toward concurrent rate limit.
            job_config.priority = bigquery.QueryPriority.BATCH

        if query_params:
            job_config.query_parameters = query_params

        query_job = self.client.query(query_str, location=location, job_config=job_config)

        if batch_mode: # wait until job is done
            while query_job.state != 'DONE':
                query_job = self.client.get_job(query_job.job_id, location=location)
                log.info('Job {} is currently in state {}'.format(query_job.job_id, query_job.state))
                #print('Job {} is currently in state {}'.format(query_job.job_id, query_job.state))
                time.sleep(5)

        if verbose:
            log.info('This query will process {} bytes.'.format(query_job.total_bytes_processed))
            #print('This query will process {} bytes.'.format(query_job.total_bytes_processed))

        return query_job
