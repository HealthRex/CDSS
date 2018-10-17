
import LocalEnv
LocalEnv.LOCAL_TEST_DB_PARAM["DSN"] = 'UMich_test.db'
LocalEnv.LOCAL_TEST_DB_PARAM["DATAPATH"] = LocalEnv.PATH_TO_CDSS + '/scripts/LabTestAnalysis/test/'
import medinfo.db.Env # TODO: comment
medinfo.db.Env.SQL_PLACEHOLDER = "?"
medinfo.db.Env.DATABASE_CONNECTOR_NAME = "sqlite3"

from medinfo.db.test.Util import DBTestCase
from scripts.LabTestAnalysis.machine_learning.extraction.LabNormalityMatrix import LabNormalityMatrix

import unittest
# from Const import RUNNER_VERBOSITY
import sqlite3
import pandas as pd
import os
from medinfo.db import DBUtil
from medinfo.dataconversion.FeatureMatrixFactory import FeatureMatrixFactory

import medinfo.dataconversion.test.UMichFeatureMatrixTestData as FMTU

class TestLabNormalityMatrix(DBTestCase):
    def setUp(self):
        DBTestCase.setUp(self)
        self.connection = DBUtil.connection();
        self._insertUMichTestRecords()
        self.matrix = LabNormalityMatrix('WBC', 10, random_state=1234, isLabPanel=False)

    def tearDown(self):
        self.matrix._factory.cleanTempFiles()
        os.remove(self.matrix._factory.getMatrixFileName())
        self.connection.close()
        DBTestCase.tearDown(self)

    def test_empty(self):
        print self.matrix._get_components_in_lab_panel()
        print self.matrix._get_average_orders_per_patient()
        print self.matrix._get_random_patient_list()
        # print 'self.matrix._num_patients:', self.matrix._num_patients

        pass

    def _insertUMichTestRecords(self):
        db_name = medinfo.db.Env.DB_PARAM['DSN']
        db_path = medinfo.db.Env.DB_PARAM['DATAPATH']
        conn = sqlite3.connect(db_path + '/' + db_name)

        table_names = ['labs', 'pt_info', 'demographics', 'encounters', 'diagnoses']

        for table_name in table_names:
            columns = FMTU.FM_TEST_INPUT_TABLES["%s_columns"%table_name]
            column_types = FMTU.FM_TEST_INPUT_TABLES["%s_column_types"%table_name]

            df = pd.DataFrame()
            for one_line in FMTU.FM_TEST_INPUT_TABLES['%s_data'%table_name]:
                df = df.append(dict(zip(columns, one_line)), ignore_index=True)

            df.to_sql(table_name, conn, if_exists="append", index=False)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLabNormalityMatrix()))
    return suite

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())