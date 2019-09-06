import os

from medinfo.db import DBUtil
from medinfo.dataconversion.Util import log
from medinfo.db.bigquery import bigQueryUtil
from google.cloud import bigquery


class StarrCommonUtils:

    def __init__(self, bqClient=None, pgConn=None):
        self.bqClient = bqClient
        self.pgConn = pgConn

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
