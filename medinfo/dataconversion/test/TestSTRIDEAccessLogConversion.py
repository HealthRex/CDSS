#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime;
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel, generatePlaceholders;

from medinfo.dataconversion.STRIDEAccessLogConversion import STRIDEAccessLogConversion;

TEST_SOURCE_TABLE = "test_accesslog_script";

class TestSTRIDEAccessLogConversion(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);

        log.info("Populate the database with test data (Assumes MySQL data structure)")
        DBUtil.execute \
        ("""create table %s
            (
                USER_ID varchar(255),
                USER_NAME varchar(255),
                DE_PAT_ID bigint,
                ACCESS_DATETIME datetime,
                METRIC_ID integer,
                METRIC_NAME text,
                LINE_COUNT integer,
                DESCRIPTION text,
                METRIC_GROUP_NUM integer,
                METRIC_GROUP_NAME text
            );
         """ % TEST_SOURCE_TABLE
        );

        self.testUserIDs = list();
        headers = ["user_id","user_name","de_pat_id","access_datetime","metric_id","metric_name","line_count","description","metric_group_num","metric_group_name"];
        dataModels = \
            [
                RowItemModel( ['S-7', 'CJ', None, '2013-10-14 08:44:47', '33006', 'ME_IBGLANCE', '1', 'IN BASKET GLANCE PLUGIN ACCESSED IN RADAR', '33000', 'Radar'], headers ),
                RowItemModel( ['S-7', 'CJ', '3289034', '2014-03-20 00:40:18', '34127', 'IP_ORDERSSECTION', '1', 'Inpatient Orders section opened ', '17001', 'PATIENT CLINICAL INFO'], headers ),
                RowItemModel( ['S-7', 'CJ', None, '2014-01-01 10:10:56', '20008', 'AC_IB_CREATEMSG', '1', 'In Basket message of any type created.', '20000', 'In Basket Report'], headers ),
                RowItemModel( ['S-7', 'CJ', None, '2014-01-01 10:10:56', '20008', 'AC_IB_CREATEMSG', '2', '(Created messages counted.) ', '20000', 'In Basket Report'], headers ),
                RowItemModel( ['S-7', 'CJ', '1853397', '2013-06-29 11:25:02', '20075', 'AC_DOCUMENTLIST_SUBC', '1', 'Prelude Documents list accessed for patient.', None, None], headers ),
                RowItemModel( ['S-4', 'AB', '3133593', '2013-10-22 06:46:29', '17008', 'MR_REPORTS', '1', 'A report with patient data accessed.', '17001', 'PATIENT CLINICAL INFO'], headers ),
                RowItemModel( ['S-4', 'AB', '3047429', '2014-03-16 20:56:54', '17016', 'MR_RESULTS_REVIEW', '1', 'Results Review activity accessed.', '17002', 'Patient Chart Review'], headers ),
                RowItemModel( ['S-4', 'AB', '3408732', '2014-04-08 08:47:38', '17016', 'MR_RESULTS_REVIEW', '1', 'Results Review activity accessed.', '17002', 'Patient Chart Review'], headers ),
                RowItemModel( ['S-4', 'AB', None, '2014-02-26 19:27:48', '34140', 'IP_SYSTEM_LIST', '1', 'Inpatient system list accessed.', '20001', 'PATIENT DEMOGRAPHICS'], headers ),
                RowItemModel( ['S-4', 'AB', '2487184', '2013-10-11 08:45:46', '17008', 'MR_REPORTS', '1', 'A report with patient data accessed.', '17001', 'PATIENT CLINICAL INFO'], headers ),

            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem(TEST_SOURCE_TABLE, dataModel, retrieveCol="user_id" );
            userID = int(dataItemId[1:]);   # Trim leading S and parse remainder as an integer
            self.testUserIDs.append(userID);

        self.converter = STRIDEAccessLogConversion();  # Instance to test on
        self.converter.sourceTableName = TEST_SOURCE_TABLE;

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")
        query = SQLQuery();
        query.delete = True;
        query.addFrom("access_log");
        query.addWhereIn("user_id", self.testUserIDs );
        DBUtil.execute( query );

        query = SQLQuery();
        query.delete = True;
        query.addFrom("user");
        query.addWhereIn("user_id", self.testUserIDs );
        DBUtil.execute( query );

        DBUtil.execute("drop table %s;" % TEST_SOURCE_TABLE);
        DBTestCase.tearDown(self);

    # def test_dataConversion(self):
    #     # Run the data conversion on the same data and look for expected records
    #     log.debug("Run the conversion process...");
    #     self.converter.convertSourceItems();
    #
    #     # Just query back for the same data, de-normalizing the data back to a general table
    #     testQuery = \
    #         """
    #         select
    #             u.name,
    #             al.de_pat_id,
    #             al.access_datetime,
    #             m.name,
    #             m.description,
    #             mg.name
    #         from
    #             access_log as al,
    #             user as u,
    #             metric as m,
    #             metric_group as mg
    #         where
    #             al.user_id = u.user_id and
    #             al.metric_id = m.metric_id and
    #             m.metric_group_id = mg.metric_group_id and
    #             al.user_id in (%s)
    #         order by
    #             al.access_datetime
    #         """ % generatePlaceholders(len(self.testUserIDs));
    #
    #     expectedData = \
    #         [
    #             ['CJ', 1853397, datetime(2013, 6, 29, 11, 25, 2), 'AC_DOCUMENTLIST_SUBC', 'Prelude Documents list accessed for patient.', 'Null Group'],  # Put placeholder for null group to avoid having to do outer join
    #             ['AB', 2487184, datetime(2013, 10, 11, 8, 45, 46), 'MR_REPORTS', 'A report with patient data accessed.', 'PATIENT CLINICAL INFO'],
    #             ['CJ', None, datetime(2013, 10, 14, 8, 44, 47), 'ME_IBGLANCE', 'IN BASKET GLANCE PLUGIN ACCESSED IN RADAR', 'Radar'],
    #             ['AB', 3133593, datetime(2013, 10, 22, 6, 46, 29), 'MR_REPORTS', 'A report with patient data accessed.', 'PATIENT CLINICAL INFO'],
    #             ['CJ', None, datetime(2014, 1, 1, 10, 10, 56), 'AC_IB_CREATEMSG', 'In Basket message of any type created. (Created messages counted.) ', 'In Basket Report'],
    #             ['AB', None, datetime(2014, 2, 26, 19, 27, 48), 'IP_SYSTEM_LIST', 'Inpatient system list accessed.', 'PATIENT DEMOGRAPHICS'],
    #             ['AB', 3047429, datetime(2014, 3, 16, 20, 56, 54), 'MR_RESULTS_REVIEW', 'Results Review activity accessed.', 'Patient Chart Review'],
    #             ['CJ', 3289034, datetime(2014, 3, 20, 0, 40, 18), 'IP_ORDERSSECTION', 'Inpatient Orders section opened ', 'PATIENT CLINICAL INFO'],
    #             ['AB', 3408732, datetime(2014, 4, 8, 8, 47, 38), 'MR_RESULTS_REVIEW', 'Results Review activity accessed.', 'Patient Chart Review'],
    #         ];
    #     actualData = DBUtil.execute(testQuery, self.testUserIDs);
    #     self.assertEqualTable( expectedData, actualData );


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestSTRIDEAccessLogConversion("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestSTRIDEAccessLogConversion("test_insertFile_skipErrors"));
    #suite.addTest(TestSTRIDEAccessLogConversion('test_executeIterator'));
    #suite.addTest(TestSTRIDEAccessLogConversion('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestSTRIDEAccessLogConversion));

    return suite;

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
