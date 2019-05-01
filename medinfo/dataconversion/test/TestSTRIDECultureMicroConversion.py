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
"""order_proc_anon_id,pat_anon_id,pat_enc_csn_anon_id,proc_code,organism_name,antibiotic_name,suseptibility,shifted_result_time
-10,1,2,LABBLC,BACTEROIDES FRAGILIS,Clindamycin,Intermediate,9/10/2111 13:15
-11,2,3,LABBLC,COAG NEGATIVE STAPHYLOCOCCUS,Vancomycin,Susceptible,4/26/2109 9:49
-12,3,4,LABBLC,COAG NEGATIVE STAPHYLOCOCCUS,Oxacillin,Resistant,4/18/2109 4:48
-13,4,5,LABBLC,COAG NEGATIVE STAPHYLOCOCCUS,Vancomycin,Susceptible,3/28/2109 23:21
-14,5,6,LABBLC,ENTEROCOCCUS FAECALIS,Amoxicillin/Clavulanic Acid,Susceptible,6/3/2109 17:07
-14,5,6,LABBLC,ENTEROCOCCUS FAECALIS,Amoxicillin/Clavulanic Acid,Susceptible,6/3/2109 17:07
-20,10,11,LABBLC,ENTEROCOCCUS FAECALIS,Method,,6/10/2109 17:07
-15,6,7,LABBLC2,,,,6/4/2109 17:07
-16,7,8,LABBLC2,,,,
-17,10,10,LABBLC2,ENTEROCOCCUS FAECALIS,Penicillin,,6/8/2109 17:07
-17,10,10,LABBLC2,ENTEROCOCCUS FAECALIS,,Intermediate,6/11/2109 17:07
"""
        # Parse into DB insertion object
        # DBUtil.insertFile( StringIO(dataTextStr), "stride_culture_micro", delim="   ", dateColFormats={"trtmnt_tm_begin_date": None, "trtmnt_tm_end_date": None} );
        DBUtil.insertFile( StringIO(dataTextStr), "stride_culture_micro", delim=",", dateColFormats={"shifted_result_time": None} );


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
                and cic.source_table = 'stride_culture_micro'
            );
            """
        );
        DBUtil.execute \
        (   """delete from clinical_item 
            where clinical_item_category_id in 
            (   select clinical_item_category_id 
                from clinical_item_category 
                where source_table = 'strid_culture_micro'
            );
            """
        );
        DBUtil.execute("delete from clinical_item_category where source_table = 'stride_culture_micro ';");

        DBUtil.execute("delete from stride_culture_micro where order_proc_anon_id < 0");

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
                pi.external_id desc
            """;
        expectedData = \
            [   ##### CHANGE to the actual expected data
[-10, 1, 2, "Microculture Susceptibility General", "Clindamycin:Intermediate", "Intermediate TO Clindamycin", DBUtil.parseDateValue("9/10/2111 13:15"),],
[-11, 2, 3, "Microculture Susceptibility General", "Vancomycin:Susceptible", "Susceptible TO Vancomycin", DBUtil.parseDateValue("4/26/2109 9:49"),],
[-12, 3, 4, "Microculture Susceptibility General", "Oxacillin:Resistant", "Resistant TO Oxacillin", DBUtil.parseDateValue("4/18/2109 4:48"),],
[-13, 4, 5, "Microculture Susceptibility General", "Vancomycin:Susceptible", "Susceptible TO Vancomycin", DBUtil.parseDateValue("3/28/2109 23:21"),],
[-14, 5, 6, "Microculture Susceptibility General", "Amoxicillin-Clavulanic Acid:Susceptible", "Susceptible TO Amoxicillin-Clavulanic Acid", DBUtil.parseDateValue("6/3/2109 17:07")],
[-15, 6, 7, "Microculture Susceptibility General", "Negative Culture", "Microculture Grew No Bacteria", DBUtil.parseDateValue("6/4/2109 17:07")]
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
