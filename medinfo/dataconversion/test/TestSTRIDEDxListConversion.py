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
from medinfo.db.Model import SQLQuery, RowItemModel;

from medinfo.dataconversion.STRIDEDxListConversion import STRIDEDxListConversion;

TEST_SOURCE_TABLE = "stride_dx_list";
TEMP_SOURCE_TABLE = "PreTest_dx_list";
TEST_START_DATE = datetime(2100,1,1);   # Date in far future to start checking for test records to avoid including existing data in database

class TestSTRIDEDxListConversion(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        
        log.info("Populate the database with test data")
        
        # Relabel any existing data to not interfere with the new test data that will be produced
        DBUtil.execute("update clinical_item_category set source_table = '%s' where source_table = '%s';" % (TEMP_SOURCE_TABLE,TEST_SOURCE_TABLE) );
    
        self.patientIdStrList = list();
        headers = ["pat_id","pat_enc_csn_id","noted_date","resolved_date","dx_icd9_code","data_source"];
        dataModels = \
            [  
                RowItemModel( ["-126500", -131017780655, "2111-10-14", None, "-431.00", "PROBLEM_LIST"], headers ),

                RowItemModel( ["-126268", -131015534571, "2111-05-04", None, "-0285", "PROBLEM_LIST"], headers ),
                RowItemModel( ["-126268", -131015534571, None, None, "-272.4", "PROBLEM_LIST"], headers ),
                RowItemModel( ["-126268", -131015534571, None, None, "-309.9", "ENC_Dx"], headers ),
                RowItemModel( ["-126268", -131015534571, "2111-05-18", None, "-785", "ADMIT_DX"], headers ),
                RowItemModel( ["-126472", -131015404439, None, None, "-719.46", "ENC_Dx"], headers ),

                # Repeat, but under different encounter, should be ignored, just base on noted date
                RowItemModel( ["-126500", -131000000000, "2111-10-14", None, "-431.00", "PROBLEM_LIST"], headers ),

                RowItemModel( ["-126798", -131014753610, None, None, "-482.9", "ENC_Dx"], headers ),
                RowItemModel( ["-126798", -131014753610, "2111-03-08", None, "-780", "ADMIT_DX"], headers ),
                RowItemModel( ["-126798", -131016557370, "2111-07-26", None, "-780.97", "ADMIT_DX"], headers ),    # No matching diagnosis code, will just make up a label then

            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("stride_dx_list", dataModel, retrieveCol="pat_id" );
            self.patientIdStrList.append( str(dataItemId) );

        
        self.icd9CUIdStrList = list();
        headers = ["cui","ispref","aui","tty","code","str","suppress"];
        dataModels = \
            [  
                RowItemModel( ["-C1", "Y", "-A1", "PT", "-0285", "Diagnosis 1","N"], headers ),
                RowItemModel( ["-C2b","Y", "-A2b","PT", "-431.0", "Diagnosis 2b","N"], headers ),    # Parent diagnoses
                RowItemModel( ["-C2", "Y", "-A2", "PT", "-431.00", "Diagnosis 2","N"], headers ),
                RowItemModel( ["-C3", "N", "-A3", "AB", "-431.00", "Diagnosis 3","N"], headers ),    # Repeat, but not preferred
                RowItemModel( ["-C4", "N", "-A4", "HT", "-785", "Diagnosis 4","N"], headers ),
                RowItemModel( ["-C5", "Y", "-A5", "HT", "-780", "Diagnosis 5","N"], headers ),
                RowItemModel( ["-C6a","Y", "-A6a","PT", "-780.9", "Diagnosis 6a","N"], headers ),
                RowItemModel( ["-C6", "Y", "-A6", "PT", "-780.97", "Diagnosis 6","N"], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("stride_icd9_cm", dataModel, retrieveCol="cui" );
            self.icd9CUIdStrList.append( str(dataItemId) );

        self.converter = STRIDEDxListConversion();  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBUtil.execute \
        (   """delete from patient_item 
            where clinical_item_id in 
            (   select clinical_item_id
                from clinical_item as ci, clinical_item_category as cic
                where ci.clinical_item_category_id = cic.clinical_item_category_id
                and cic.source_table = '%s'
            );
            """ % TEST_SOURCE_TABLE
        );
        DBUtil.execute \
        (   """delete from clinical_item 
            where clinical_item_category_id in 
            (   select clinical_item_category_id 
                from clinical_item_category 
                where source_table = '%s'
            );
            """ % TEST_SOURCE_TABLE
        );
        DBUtil.execute("delete from clinical_item_category where source_table = '%s';" % TEST_SOURCE_TABLE);
        DBUtil.execute("update clinical_item_category set source_table = '%s' where source_table = '%s';" % (TEST_SOURCE_TABLE,TEMP_SOURCE_TABLE) ); # Reset labels of any prior data

        query = SQLQuery();
        query.delete = True;
        query.addFrom("stride_dx_list");
        query.addWhereIn("pat_id", self.patientIdStrList );
        DBUtil.execute( query );

        query = SQLQuery();
        query.delete = True;
        query.addFrom("stride_icd9_cm");
        query.addWhereIn("cui", self.icd9CUIdStrList );
        DBUtil.execute( query );

        DBTestCase.tearDown(self);

    def test_dataConversion(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the conversion process...");
        self.converter.convertSourceItems(TEST_START_DATE);

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
                cic.source_table = '%s'
            order by
                pi.patient_id desc, ci.name, pi.item_date
            """ % TEST_SOURCE_TABLE;
        expectedData = \
            [   # Expected data should be updated once we have ICD9 - Name conversion tables
                [None, -126268, -131015534571, "Diagnosis (PROBLEM_LIST)", None, "ICD9.-0285", "Diagnosis 1", datetime(2111,5,4)],
                [None, -126268, -131015534571, "Diagnosis (ADMIT_DX)", None, "ICD9.-785", "Diagnosis 4", datetime(2111,5,18)],

                [None, -126500, -131017780655, "Diagnosis (PROBLEM_LIST)", None, "ICD9.-431.0", "Diagnosis 2b", datetime(2111,10,14)],
                [None, -126500, -131017780655, "Diagnosis (PROBLEM_LIST)", None, "ICD9.-431.00", "Diagnosis 2", datetime(2111,10,14)],
                
                [None, -126798, -131014753610, "Diagnosis (ADMIT_DX)", None, "ICD9.-780", "Diagnosis 5", datetime(2111,3,8)],
                [None, -126798, -131016557370, "Diagnosis (ADMIT_DX)", None, "ICD9.-780", "Diagnosis 5", datetime(2111,7,26)],
                [None, -126798, -131016557370, "Diagnosis (ADMIT_DX)", None, "ICD9.-780.9", "Diagnosis 6a", datetime(2111,7,26)],
                [None, -126798, -131016557370, "Diagnosis (ADMIT_DX)", None, "ICD9.-780.97", "Diagnosis 6", datetime(2111,7,26)],
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestSTRIDEDxListConversion("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestSTRIDEDxListConversion("test_insertFile_skipErrors"));
    #suite.addTest(TestSTRIDEDxListConversion('test_executeIterator'));
    #suite.addTest(TestSTRIDEDxListConversion('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestSTRIDEDxListConversion));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
