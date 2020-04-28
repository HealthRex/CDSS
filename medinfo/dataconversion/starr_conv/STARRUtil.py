import csv
import os
import pytz
import random
import subprocess
import sys
import time

from medinfo.common.Util import stdOpen
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
        with open(csv_file, 'w', newline='') as test_data_file:
            csv_writer = csv.writer(test_data_file)
            csv_writer.writerow(header)
            csv_writer.writerows(test_data)

    '''
    Retrieves schema for given table from the given BQ client.
    It is possible to filter out only required fields.
    The resulting schema, in this case, will be sorted according to the filter order.
    '''
    def get_schema_filtered(self, dataset, table, fields_to_keep_in_schema=None):
        schema = self.bqClient.client.get_table('mining-clinical-decisions.{}.{}'.format(dataset, table)).schema

        if fields_to_keep_in_schema:
            # filter out only fields we need
            schema = list([field for field in schema if field.name in fields_to_keep_in_schema])
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

    def dumpPatientItemCollectionLinkToCsv(self, tempDir, batchCounter=999):
        log.info('Dumping patient_item_collection_link for batch {} to CSV'.format(batchCounter))

        DBUtil.dumpTableToCsv('patient_item_collection_link',
                              '{}/{}_patient_item_collection_link.csv'.format(tempDir, batchCounter))

    def dumpItemCollectionTablesToCsv(self, tempDir):
        log.info('Dumping item_collection_item and item_collection to CSV')

        DBUtil.dumpTableToCsv('item_collection_item', '{}/item_collection_item.csv'.format(tempDir))
        DBUtil.dumpTableToCsv('item_collection', '{}/item_collection.csv'.format(tempDir))

    def uploadPatientItemCollectionLinkCsvToBQ(self, tempDir, datasetId, batchCounter=999):
        log.info('Uploading patient_item CSV to BQ dataset {} for batch {}'.format(datasetId, batchCounter))
        patient_item_collection_link_schema = self.get_schema_filtered('clinical_item2018',
                                                                       'patient_item_collection_link')

        csv_path = tempDir + os.path.sep + str(batchCounter) + '_patient_item_collection_link.csv'

        bigQueryUtil.headerChecker(csv_path, [sf.name for sf in patient_item_collection_link_schema])

        self.bqClient.load_csv_to_table(datasetId, 'patient_item_collection_link', csv_path, skip_rows=1,
                                        append_to_table=True, auto_detect_schema=False,
                                        schema=patient_item_collection_link_schema)

    def uploadItemCollectionTablesCsvToBQ(self, tempDir, datasetId):
        log.info('Uploading item_collection CSV to BQ dataset {}'.format(datasetId))
        item_collection_schema = self.get_schema_filtered('clinical_item2018', 'item_collection')

        item_collection_csv_path = tempDir + '/item_collection.csv'

        bigQueryUtil.headerChecker(item_collection_csv_path, [sf.name for sf in item_collection_schema])

        self.bqClient.load_csv_to_table(datasetId, 'item_collection', item_collection_csv_path, skip_rows=1,
                                        append_to_table=True, auto_detect_schema=False, schema=item_collection_schema)

        log.info('Uploading item_collection_item CSV to BQ dataset {}'.format(datasetId))
        item_collection_item_schema = self.get_schema_filtered('clinical_item2018', 'item_collection_item')

        item_collection_item_csv_path = tempDir + '/item_collection_item.csv'

        bigQueryUtil.headerChecker(item_collection_item_csv_path, [sf.name for sf in item_collection_item_schema])

        self.bqClient.load_csv_to_table(datasetId, 'item_collection_item', item_collection_item_csv_path, skip_rows=1,
                                        append_to_table=True, auto_detect_schema=False,
                                        schema=item_collection_item_schema)

    def removePatientItemCollectionLinkCsv(self, temp_dir, batchCounter=999):
        log.info('Removing patient_item_collection_link CSV for batch {}'.format(batchCounter))
        self.remove_file(temp_dir + os.path.sep + str(batchCounter) + '_patient_item_collection_link.csv')

    def removeItemCollectionTablesCsv(self, temp_dir):
        log.info('Removing item_collection and item_collection_item CSVs')
        self.remove_file(temp_dir + '/item_collection.csv')
        self.remove_file(temp_dir + '/item_collection_item.csv')

    def removePatientItemCollectionLinkAddedLines(self, source_table):
        """delete added records"""
        log.info('Removing patient_item_collection_link added lines in PSQL DB')

        DBUtil.execute(
            """delete from patient_item_collection_link pi
               using item_collection_item ici, clinical_item ci, clinical_item_category cic
               where pi.item_collection_item_id = ici.item_collection_item_id
                 and ici.clinical_item_id = ci.clinical_item_id
                 and ci.clinical_item_category_id = cic.clinical_item_category_id
                 and cic.source_table = '{}';
                 """.format(source_table), conn=self.pgConn
        )

    def removeItemCollectionTablesAddedLines(self, source_table):
        """delete added records"""
        log.info('Removing item_collection_item and item_collection added lines in PSQL DB')

        DBUtil.execute(
            """delete from item_collection_item ici
               using clinical_item ci, clinical_item_category cic
               where ici.clinical_item_id = ci.clinical_item_id
                 and ci.clinical_item_category_id = cic.clinical_item_category_id
                 and cic.source_table = '{}';
                 """.format(source_table), conn=self.pgConn
         )

        # TODO should be using source_table also
        DBUtil.execute("delete from item_collection where true;", conn=self.pgConn)

    def dumpPatientItemToCsv(self, tempDir, batchCounter=999):
        log.info('Dumping patient_item for batch {} to CSV'.format(batchCounter))

        DBUtil.dumpTableToCsv('patient_item', '{}/{}_patient_item.csv'.format(tempDir, batchCounter))

    def dumpClinicalTablesToCsv(self, tempDir):
        log.info('Dumping clinical_item and clinical_item_category to CSV')

        DBUtil.dumpTableToCsv('clinical_item', '{}/clinical_item.csv'.format(tempDir))
        DBUtil.dumpTableToCsv('clinical_item_category', '{}/clinical_item_category.csv'.format(tempDir))

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
                               bigquery.SchemaField('source_id', 'INT64', 'NULLABLE', None, ()),
                               bigquery.SchemaField('item_date_utc', 'TIMESTAMP', 'NULLABLE', None, ())]

        csv_path = tempDir + os.path.sep + str(batchCounter) + '_patient_item.csv'

        bigQueryUtil.headerChecker(csv_path, [sf.name for sf in patient_item_schema])

        self.bqClient.load_csv_to_table(datasetId, 'patient_item', csv_path, schema=patient_item_schema, skip_rows=1,
                                        append_to_table=True)
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
                                        schema=clinical_item_category_schema, skip_rows=1, append_to_table=True)
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
                                        schema=clinical_item_schema, skip_rows=1, append_to_table=True)
        # auto_detect_schema=False, schema=clinical_item_schema)

    def removePatientItemCsv(self, temp_dir, batchCounter=999):
        log.info('Removing patient_item CSV for batch {}'.format(batchCounter))
        self.remove_file(temp_dir + os.path.sep + str(batchCounter) + '_patient_item.csv')

    def removeClinicalTablesCsv(self, temp_dir):
        log.info('Removing clinical_item and clinical_item_category CSVs')
        self.remove_file(temp_dir + '/clinical_item.csv')
        self.remove_file(temp_dir + '/clinical_item_category.csv')

    @staticmethod
    def remove_file(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            log.warning('{} does not exist'.format(file_path))

    def removePatientItemAddedLines(self, source_table):
        """delete added records"""
        log.info('Removing patient_item added lines in PSQL DB')

        DBUtil.execute(
            """delete from patient_item 
                where clinical_item_id in 
                (   select clinical_item_id
                    from clinical_item as ci, clinical_item_category as cic
                    where ci.clinical_item_category_id = cic.clinical_item_category_id
                    and cic.source_table = '{}'
                );
                """.format(source_table), conn=self.pgConn
        )

    def removeClinicalTablesAddedLines(self, source_table):
        """delete added records"""
        log.info('Removing clinical_item and clinical_item_category added lines in PSQL DB')

        DBUtil.execute(
            """delete from clinical_item 
                where clinical_item_category_id in 
                (   select clinical_item_category_id 
                    from clinical_item_category 
                    where source_table = '{}'
                );
                """.format(source_table), conn=self.pgConn
        )
        DBUtil.execute("delete from clinical_item_category where source_table = '{}';".format(source_table),
                       conn=self.pgConn)
