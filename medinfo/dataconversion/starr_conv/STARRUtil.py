import csv
import os
import pytz
import random
import time

from medinfo.db import DBUtil
from medinfo.dataconversion.Util import log
from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery


class StarrCommonUtils:

    def __init__(self, bqClient=None, pgConn=None):
        self.bqClient = bqClient
        self.pgConn = pgConn

    @staticmethod
    def convertPatIdToSTRIDE(starr_pat_id):
        return int(starr_pat_id[2:], 16)

    '''
    BigQuery SQL conversion e.g.
    https://stackoverflow.com/questions/46664776
    
    CREATE TEMP FUNCTION HexToInt(hex_string STRING) AS (
      IFNULL(SAFE_CAST(CONCAT('0x', REPLACE(hex_string, ' ', '')) AS INT64), 0)
    );
    
    SELECT HexToInt(SUBSTR('JCcdf815', 3));
    '''

    @staticmethod
    def convertPatIdToSTARR(stride_pat_id):
        return 'JC' + hex(stride_pat_id)

    '''
    BigQuery SQL conversion e.g.
    https://stackoverflow.com/questions/51600209
    
    CREATE TEMP FUNCTION IntToHex(x INT64) AS (
      LTRIM(
      (SELECT STRING_AGG(FORMAT('%02x', x >> (byte * 8) & 0xff), 
                         '' ORDER BY byte DESC)
       FROM UNNEST(GENERATE_ARRAY(0, 7)) AS byte),
      '0'
      )
    );
    
    SELECT CONCAT('JC', IntToHex(13498389));
    '''

    @staticmethod
    def random_period():
        start_date = random.randint(1, int(time.time()))
        end_date = random.randint(start_date, int(time.time()))
        return start_date, end_date

    @staticmethod
    def dump_test_data_to_csv(header, test_data, csv_file):
        with open(csv_file, 'wb') as test_data_file:
            csv_writer = csv.writer(test_data_file)
            csv_writer.writerow(header)
            csv_writer.writerows(test_data)

    '''
    Retrieves schema for given table from the given BQ client.
    It is possible to filter out only required fields.
    The resulting schema, in this case, will be sorted according to the filter order.
    '''
    def get_schema_filtered(self, dataset, table, fields_to_keep_in_schema):
        schema = self.bqClient.client.get_table(
            self.bqClient.client.dataset(dataset, 'mining-clinical-decisions').table(table)
        ).schema

        if fields_to_keep_in_schema:
            # filter out only fields we need
            schema = list(filter(lambda field: field.name in fields_to_keep_in_schema, schema))
            # sort schema fields according to the header
            schema.sort(key=lambda field: fields_to_keep_in_schema.index(field.name))

        return schema

    def upload_csv_to_bigquery(self, schema_dataset, schema_table, dest_dataset, dest_table, csv_file,
                               schema_fields=None):
        schema = self.get_schema_filtered(schema_dataset, schema_table, schema_fields)

        self.bqClient.load_csv_to_table(
            dest_dataset,
            dest_table,
            csv_file,
            False,
            schema,
            1
        )

    def dumpPatientItemToCsv(self, tempDir, batchCounter=999):
        log.info('Dumping patient_item for batch %s to CSV' % batchCounter)

        DBUtil.execute \
                (
                '''
                COPY patient_item TO '%s/%s_patient_item.csv' DELIMITER ',' CSV HEADER;
                ''' % (tempDir, batchCounter), conn=self.pgConn
            )

    def dumpClinicalTablesToCsv(self, tempDir):
        log.info('Dumping clinical_item and clinical_item_category to CSV')

        DBUtil.execute \
                (
                '''
                COPY clinical_item TO '%s/clinical_item.csv' DELIMITER ',' CSV HEADER;
                ''' % tempDir, conn=self.pgConn
            )

        DBUtil.execute \
                (
                '''
                COPY clinical_item_category TO '%s/clinical_item_category.csv' DELIMITER ',' CSV HEADER;
                ''' % tempDir, conn=self.pgConn
            )

    def uploadPatientItemCsvToBQ(self, tempDir, datasetId, batchCounter=999):
        log.info('Uploading patient_item CSV to BQ dataset %s for batch %s' % (datasetId, batchCounter))
        patient_item_schema = [bigquery.SchemaField('patient_item_id', 'INT64', 'REQUIRED', None, ()),
                               bigquery.SchemaField('external_id', 'INT64', 'NULLABLE', None, ()),
                               bigquery.SchemaField('patient_id', 'INT64', 'REQUIRED', None, ()),
                               bigquery.SchemaField('clinical_item_id', 'INT64', 'REQUIRED', None, ()),
                               bigquery.SchemaField('item_date', 'TIMESTAMP', 'REQUIRED', None, ()),
                               bigquery.SchemaField('analyze_date', 'TIMESTAMP', 'NULLABLE', None, ()),
                               bigquery.SchemaField('encounter_id', 'INT64', 'NULLABLE', None, ()),
                               bigquery.SchemaField('text_value', 'STRING', 'NULLABLE', None, ()),
                               bigquery.SchemaField('num_value', 'FLOAT64', 'NULLABLE', None, ()),
                               bigquery.SchemaField('source_id', 'INT64', 'NULLABLE', None, ())]

        csv_path = tempDir + '/' + str(batchCounter) + '_patient_item.csv'

        bigQueryUtil.headerChecker(csv_path, [sf.name for sf in patient_item_schema])

        self.bqClient.load_csv_to_table(datasetId, 'patient_item', csv_path, skip_rows=1, append_to_table=True)
        # auto_detect_schema=False, schema=patient_item_schema)

    def uploadClinicalTablesCsvToBQ(self, tempDir, datasetId):
        log.info('Uploading clinical_item_category CSV to BQ dataset %s' % datasetId)
        clinical_item_category_schema = [
            bigquery.SchemaField('clinical_item_category_id', 'INT64', 'REQUIRED', None, ()),
            bigquery.SchemaField('source_table', 'STRING', 'REQUIRED', None, ()),
            bigquery.SchemaField('description', 'STRING', 'NULLABLE', None, ()),
            bigquery.SchemaField('default_recommend', 'INT64', 'NULLABLE', None, ())]

        clinical_item_category_csv_path = tempDir + '/clinical_item_category.csv'

        bigQueryUtil.headerChecker(clinical_item_category_csv_path, [sf.name for sf in clinical_item_category_schema])

        self.bqClient.load_csv_to_table(datasetId, 'clinical_item_category', clinical_item_category_csv_path,
                                        skip_rows=1, append_to_table=True)
        # auto_detect_schema=False, schema=clinical_item_category_schema)

        log.info('Uploading clinical_item CSV to BQ dataset %s' % datasetId)
        clinical_item_schema = [bigquery.SchemaField('clinical_item_id', 'INT64', 'REQUIRED', None, ()),
                                bigquery.SchemaField('clinical_item_category_id', 'INT64', 'REQUIRED', None, ()),
                                bigquery.SchemaField('external_id', 'INT64', 'NULLABLE', None, ()),
                                bigquery.SchemaField('name', 'STRING', 'REQUIRED', None, ()),
                                bigquery.SchemaField('description', 'STRING', 'NULLABLE', None, ()),
                                bigquery.SchemaField('default_recommend', 'INT64', 'NULLABLE', None, ()),
                                bigquery.SchemaField('item_count', 'FLOAT64', 'NULLABLE', None, ()),
                                bigquery.SchemaField('patient_count', 'FLOAT64', 'NULLABLE', None, ()),
                                bigquery.SchemaField('encounter_count', 'FLOAT64', 'NULLABLE', None, ()),
                                bigquery.SchemaField('analysis_status', 'INT64', 'NULLABLE', None, ()),
                                bigquery.SchemaField('outcome_interest', 'INT64', 'NULLABLE', None, ())]

        clinical_item_csv_path = tempDir + '/clinical_item.csv'

        bigQueryUtil.headerChecker(clinical_item_csv_path, [sf.name for sf in clinical_item_schema])

        self.bqClient.load_csv_to_table(datasetId, 'clinical_item', clinical_item_csv_path,
                                        skip_rows=1, append_to_table=True)
        # auto_detect_schema=False, schema=clinical_item_schema)

    def removePatientItemCsv(self, tempDir, batchCounter=999):
        log.info('Removing patient_item CSV for batch %s' % batchCounter)
        if os.path.exists(tempDir + '/' + str(batchCounter) + '_patient_item.csv'):
            os.remove(tempDir + '/' + str(batchCounter) + '_patient_item.csv')
        else:
            print(tempDir + '/' + str(batchCounter) + '_patient_item.csv does not exist')

    def removeClinicalTablesCsv(self, tempDir):
        log.info('Removing clinical_item and clinical_item_category CSVs')
        if os.path.exists(tempDir + '/clinical_item.csv'):
            os.remove(tempDir + '/clinical_item.csv')
        else:
            print(tempDir + '/clinical_item.csv does not exist')

        if os.path.exists(tempDir + '/clinical_item_category.csv'):
            os.remove(tempDir + '/clinical_item_category.csv')
        else:
            print(tempDir + '/clinical_item_category.csv does not exist')

    def removePatientItemAddedLines(self, source_table):
        """delete added records"""
        log.info('Removing patient_item added lines in PSQL DB')

        DBUtil.execute \
            ("""delete from patient_item 
                    where clinical_item_id in 
                    (   select clinical_item_id
                        from clinical_item as ci, clinical_item_category as cic
                        where ci.clinical_item_category_id = cic.clinical_item_category_id
                        and cic.source_table = '%s'
                    );
                    """ % source_table, conn=self.pgConn
             )

    def removeClinicalTablesAddedLines(self, source_table):
        """delete added records"""
        log.info('Removing clinical_item and clinical_item_category added lines in PSQL DB')

        DBUtil.execute \
            ("""delete from clinical_item 
                    where clinical_item_category_id in 
                    (   select clinical_item_category_id 
                        from clinical_item_category 
                        where source_table = '%s'
                    );
                    """ % source_table, conn=self.pgConn
             )
        DBUtil.execute("delete from clinical_item_category where source_table = '%s';" % source_table, conn=self.pgConn)
