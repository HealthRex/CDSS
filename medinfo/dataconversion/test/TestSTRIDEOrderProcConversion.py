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

from medinfo.dataconversion.STRIDEOrderProcConversion import STRIDEOrderProcConversion;

TEST_START_DATE = datetime(2100,1,1);   # Date in far future to start checking for test records to avoid including existing data in database

class TestSTRIDEOrderProcConversion(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        
        log.info("Populate the database with test data")
        
        # Relabel any existing data to not interfere with the new test data that will be produced
        DBUtil.execute("update clinical_item_category set source_table = 'PreTest_order_proc' where source_table = 'stride_order_proc';");
    
        self.orderProcIdStrList = list();
        headers = ["order_proc_id", "pat_id", "pat_enc_csn_id", "order_type", "proc_id", "proc_code", "description", "order_time", "instantiated_time","stand_interval"];
        dataModels = \
            [   # Deliberately design dates in far future to facilitate isolated testing
                RowItemModel( [ -417974686, "380873", 111, "Nursing", 1453, "NUR1043", "NURSING PULSE OXIMETRY", "2111-12-10", None, "CONTINUOUS"], headers ),
                RowItemModel( [ -419697343, "3042640", 222, "Point of Care Testing", 1001, "LABPOCGLU", "GLUCOSE BY METER", "2112-01-13", None, "Q6H"], headers ),
                RowItemModel( [ -418928388, "-1612899", 333, "Point of Care Testing", 1001, "LABPOCGLU", "GLUCOSE BY METER", "2111-12-28", None, "ONCE"], headers ),
                RowItemModel( [ -418928399, "-1612899", 333, "Point of Care Testing", 1001, "LABPOCGLU", "GLUCOSE BY METER", "2111-12-28", None, "DAILY"], headers ), # Ignore repeast when consider unique by patient, item, date
                RowItemModel( [ -418928378, "-1612899", 333, "Point of Care Testing", 1001, "LABPOCGLU", "GLUCOSE BY METER", "2111-12-18", None, "PRN"], headers ),    # PRN orders should be ignored
                RowItemModel( [ -418045499, "2087083", 444, "Nursing", 1428, "NUR1018", "MONITOR INTAKE AND OUTPUT", "2111-12-11", None, None], headers ),
                RowItemModel( [ -417843774, "2648748", 555, "Nursing", 1508, "NUR1068", "WEIGHT", "2111-12-08", None, "ONCE"], headers ),
                RowItemModel( [ -419268931, "3039254", 666, "Lab", 1721, "LABPTT", "PTT PARTIAL THROMBOPLASTIN TIME", "2112-01-04", None, "DAILY"], headers ),
                RowItemModel( [ -419268231, "3039254", 666, "Lab", 1721, "LABPTT", "PTT PARTIAL THROMBOPLASTIN TIME", "2112-01-04", "2112-01-06", "Q6H PRN"], headers ),  # Ignore instantiated / spawned child orders
                RowItemModel( [ -419268937, "3039254", 666, "Lab", 9991721, "LABPTT", "PTT (PARTIAL THROMBOPLASTIN TIME)", "2112-01-05", None, "DAILY"], headers ), # Different proc_id, but same proc_Code. Treat like the same
                RowItemModel( [ -419268935, "3039254", 777, "Lab", 1721, "LABPTT", "PTT PARTIAL THROMBOPLASTIN TIME", "2112-01-04", "2112-01-07", "ONCE"], headers ),  #   Primarily only interested in the decision point with the original order
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("stride_order_proc", dataModel, retrieveCol="order_proc_id" );
            self.orderProcIdStrList.append( str(dataItemId) );

        # Certain items drawn from order sets
        headers = ["order_proc_id", "protocol_id","protocol_name","section_name","smart_group"];
        dataModels = \
            [   
                RowItemModel( [ -418928388, -222, "ER General", "Testing", "PoC",], headers ),
                RowItemModel( [ -418928378, -222, "ER General", "Testing", "PoC",], headers ),
                RowItemModel( [ -418045499, -111, "General Admit", "Nursing", "Monitoring",], headers ),
                RowItemModel( [ -419268931, -111, "General Admit", "Lab", "Coag",], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("stride_orderset_order_proc", dataModel, retrieveCol="order_proc_id" );

        self.converter = STRIDEOrderProcConversion();  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBUtil.execute \
        (   """delete from patient_item_collection_link
            where item_collection_item_id in 
            (   select item_collection_item_id
                from item_collection_item as ici, item_collection as ic
                where ici.item_collection_id = ic.item_collection_id
                and ic.external_id < 0
            );
            """
        );
        DBUtil.execute \
        (   """delete from item_collection_item
            where item_collection_id in 
            (   select item_collection_id
                from item_collection as ic
                where ic.external_id < 0
            );
            """
        );
        DBUtil.execute("delete from item_collection where external_id < 0;");


        DBUtil.execute \
        (   """delete from patient_item 
            where clinical_item_id in 
            (   select clinical_item_id
                from clinical_item as ci, clinical_item_category as cic
                where ci.clinical_item_category_id = cic.clinical_item_category_id
                and cic.source_table = 'stride_order_proc'
            );
            """
        );
        DBUtil.execute \
        (   """delete from clinical_item 
            where clinical_item_category_id in 
            (   select clinical_item_category_id 
                from clinical_item_category 
                where source_table = 'stride_order_proc'
            );
            """
        );
        DBUtil.execute("delete from clinical_item_category where source_table = 'stride_order_proc';");
        DBUtil.execute("update clinical_item_category set source_table = 'stride_order_proc' where source_table = 'PreTest_order_proc';"); # Reset labels of any prior data

        DBUtil.execute("delete from stride_orderset_order_proc where order_proc_id in (%s)" % str.join(",", self.orderProcIdStrList) );
        DBUtil.execute("delete from stride_order_proc where order_proc_id in (%s)" % str.join(",", self.orderProcIdStrList) );

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
                cic.source_table = 'stride_order_proc'
            order by
                pi.external_id
            """;
        expectedData = \
            [
                [ -419697343, 3042640, 222, "Point of Care Testing", 1001, "LABPOCGLU", "GLUCOSE BY METER", datetime(2112,01,13) ],
                [ -419268937, 3039254, 666, "Lab", 1721, "LABPTT", "PTT PARTIAL THROMBOPLASTIN TIME", datetime(2112,01,05) ],
                [ -419268931, 3039254, 666, "Lab", 1721, "LABPTT", "PTT PARTIAL THROMBOPLASTIN TIME", datetime(2112,01,04) ],
                [ -418928388, -1612899, 333, "Point of Care Testing", 1001, "LABPOCGLU", "GLUCOSE BY METER", datetime(2111,12,28) ],
                [ -418045499, 2087083, 444, "Nursing", 1428, "NUR1018", "MONITOR INTAKE AND OUTPUT", datetime(2111,12,11) ],
                [ -417974686, 380873, 111, "Nursing", 1453, "NUR1043", "NURSING PULSE OXIMETRY", datetime(2111,12,10) ],
                [ -417843774, 2648748, 555, "Nursing", 1508, "NUR1068", "WEIGHT", datetime(2111,12,8) ],
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );


        # Query for order set links
        testQuery = \
            """
            select 
                pi.external_id,
                ci.description,
                ic.external_id,
                ic.name,
                ic.section,
                ic.subgroup
            from
                patient_item as pi,
                clinical_item as ci,
                clinical_item_category as cic,
                patient_item_collection_link as picl,
                item_collection_item as ici,
                item_collection as ic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = 'stride_order_proc' and
                pi.patient_item_id = picl.patient_item_id and
                picl.item_collection_item_id = ici.item_collection_item_id and
                ici.item_collection_id = ic.item_collection_id
            order by
                pi.external_id
            """;
        expectedData = \
            [
                [ -419268931, "PTT PARTIAL THROMBOPLASTIN TIME", -111,"General Admit","Lab","Coag"],
                [ -418928388, "GLUCOSE BY METER", -222,"ER General","Testing","PoC" ],
                [ -418045499, "MONITOR INTAKE AND OUTPUT", -111,"General Admit","Nursing","Monitoring" ],
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestSTRIDEOrderProcConversion("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestSTRIDEOrderProcConversion("test_insertFile_skipErrors"));
    #suite.addTest(TestSTRIDEOrderProcConversion('test_executeIterator'));
    #suite.addTest(TestSTRIDEOrderProcConversion('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestSTRIDEOrderProcConversion));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
