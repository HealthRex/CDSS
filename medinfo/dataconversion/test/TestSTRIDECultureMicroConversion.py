#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime;
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.db.test.Util import DBTestCase;
from stride.core.StrideLoader import StrideLoader;
from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader; 

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.ResultsFormatter import TabDictReader;

from medinfo.dataconversion.STRIDECultureMicroConversion import STRIDECultureMicroConversion, ConversionOptions;

TEST_START_DATE = datetime(2100,1,1);   # Date in far future to start checking for test records to avoid including existing data in database

class TestSTRIDECultureMicroConversion(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        
        log.info("Populate the database with test data")
        StrideLoader.build_stride_psql_schemata()
        ClinicalItemDataLoader.build_clinical_item_psql_schemata();

        ###### PREPARE SOME FAKE INPUT DATA TO BE CONVERTED ##############
        ###### PREPARE SOME FAKE INPUT DATA TO BE CONVERTED ##############
        ###### PREPARE SOME FAKE INPUT DATA TO BE CONVERTED ##############
        ###### PREPARE SOME FAKE INPUT DATA TO BE CONVERTED ##############
        ###### PREPARE SOME FAKE INPUT DATA TO BE CONVERTED ##############
        dataTextStr = \
"""stride_treatment_team_id\tpat_id\tpat_enc_csn_id\ttrtmnt_tm_begin_date\ttrtmnt_tm_end_date\ttreatment_team\tprov_name
-100\t-2536\t-57\t\t\t\tAnonymous.
-200\t-117\t0\t10/5/2113 23:18\t10/6/2113 10:20\tAdditional Communicating Provider\tAnonymous.Additional Communicating Provider
-300\t-4845\t-60\t6/26/2113 8:11\t6/26/2113 8:13\tCare Coordinator\tAnonymous.Care Coordinator
-400\t-9194\t-26\t4/11/2109 8:39\t\tCase Manager\tAnonymous.Case Manager
-500\t-9519\t-69\t3/19/2113 12:10\t\tChief Resident\tAnonymous.Chief Resident
-600\t-8702\t-77\t4/10/2109 8:45\t\tClinical Dietician\tAnonymous.Clinical Dietician
-700\t-8307\t-92\t7/9/2113 0:21\t7/9/2113 2:16\tCo-Attending\tAnonymous.Co-Attending
-800\t-5474\t-78\t12/4/2113 9:47\t12/4/2113 12:55\tConsulting Attending\tAnonymous.Consulting Attending
-900\t-6015\t-47\t7/24/2113 2:29\t\tConsulting Fellow\tAnonymous.Consulting Fellow
"""
        # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "stride_culture_micro", delim="\t", dateColFormats={"trtmnt_tm_begin_date": None, "trtmnt_tm_end_date": None} );

        self.converter = STRIDECultureMicroConversion();  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        ######FIX THIS TO CLEANUP YOUR TEST DATA .... May be don't have to, since superclass will just drop the whole database anyway
        DBUtil.execute \
        (   """delete from patient_item 
            where clinical_item_id in 
            (   select clinical_item_id
                from clinical_item as ci, clinical_item_category as cic
                where ci.clinical_item_category_id = cic.clinical_item_category_id
                and cic.source_table = 'stride_treatment_team'
            );
            """
        );
        DBUtil.execute \
        (   """delete from clinical_item 
            where clinical_item_category_id in 
            (   select clinical_item_category_id 
                from clinical_item_category 
                where source_table = 'stride_treatment_team'
            );
            """
        );
        DBUtil.execute("delete from clinical_item_category where source_table = 'stride_treatment_team';");

        DBUtil.execute("delete from stride_treatment_team where stride_treatment_team_id < 0");

        DBTestCase.tearDown(self);

    def test_dataConversion(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the conversion process...");
        convOptions = ConversionOptions();
        convOptions.startDate = TEST_START_DATE;
        self.converter.convertSourceItems(convOptions);

        # Just query back for the same data, de-normalizing the data back to a general table
        testQuery = \
            """
            select 
                pi.external_id,
                pi.patient_id,
                pi.encounter_id,
                cic.description,
                ci.external_id,
                ci.name,
                ci.description,
                pi.item_date
            from
                patient_item as pi,
                clinical_item as ci,
                clinical_item_category as cic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = 'stride_culture_micro'
            order by
                pi.external_id desc, ci.external_id desc
            """;
        expectedData = \
            [   ##### CHANGE to the actual expected data
[-200, -117, 0, "Treatment Team", None, "ACP", "Additional Communicating Provider", DBUtil.parseDateValue("10/5/2113 23:18"),],
[-300, -4845, -60, "Treatment Team", None, "CC", "Care Coordinator", DBUtil.parseDateValue("6/26/2113 8:11"),],
[-400, -9194, -26, "Treatment Team", None, "CM", "Case Manager", DBUtil.parseDateValue("4/11/2109 8:39"),],
[-500, -9519, -69, "Treatment Team", None, "CR", "Chief Resident", DBUtil.parseDateValue("3/19/2113 12:10"),],
[-600, -8702, -77, "Treatment Team", None, "CD", "Clinical Dietician", DBUtil.parseDateValue("4/10/2109 8:45"),],
[-700, -8307, -92, "Treatment Team", None, "C", "Co-Attending", DBUtil.parseDateValue("7/9/2113 0:21"),],
[-800, -5474, -78, "Treatment Team", None, "CA", "Consulting Attending", DBUtil.parseDateValue("12/4/2113 9:47"),],
[-900, -6015, -47, "Treatment Team", None, "CF", "Consulting Fellow", DBUtil.parseDateValue("7/24/2113 2:29"),],
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestSTRIDECultureMicroConversion("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestSTRIDECultureMicroConversion("test_insertFile_skipErrors"));
    #suite.addTest(TestSTRIDECultureMicroConversion('test_executeIterator'));
    #suite.addTest(TestSTRIDECultureMicroConversion('test_dataConversion_aggregate'));
    suite.addTest(unittest.makeSuite(TestSTRIDECultureMicroConversion));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
