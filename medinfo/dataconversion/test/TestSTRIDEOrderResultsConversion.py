#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from io import StringIO
from datetime import datetime;
import unittest

from .Const import RUNNER_VERBOSITY;
from .Util import log;

from medinfo.db.test.Util import DBTestCase;
from stride.core.StrideLoader import StrideLoader;
from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader; 

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;

from medinfo.dataconversion.STRIDEOrderResultsConversion import STRIDEOrderResultsConversion;

TEST_SOURCE_TABLE = "stride_order_results";
TEST_START_DATE = datetime(2100,1,1);   # Date in far future to start checking for test records to avoid including existing data in database

class TestSTRIDEOrderResultsConversion(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        
        log.info("Populate the database with test data")
        StrideLoader.build_stride_psql_schemata()
        ClinicalItemDataLoader.build_clinical_item_psql_schemata();

        dataTextStr = """order_proc_id\tpat_id\tpat_enc_csn_id\torder_type\tproc_id\tproc_code\tdescription
-30560253\t-7803\t-1772\tLab\t471521\tLABACETA\tACETAMINOPHEN, SERUM
-31300455\t-2168\t-261\tLab\t471521\tLABACETA\tACETAMINOPHEN, SERUM
-29501223\t-9860\t-1772\tLab\t471521\tLABACETA\tACETAMINOPHEN, SERUM
-31823670\t-2130\t-3897\tLab\t471521\tLABACETA\tACETAMINOPHEN, SERUM
-31237072\t-124\t-8391\tLab\t471521\tLABACETA\tACETAMINOPHEN, SERUM
-29966444\t-5690\t-1150\tLab\t471521\tLABACETA\tACETAMINOPHEN, SERUM
-33197720\t-9926\t-4898\tLab\t471521\tLABACETA\tACETAMINOPHEN, SERUM
-36668349\t-9815\t-3658\tLab\t471521\tLABACETA\tACETAMINOPHEN, SERUM
-33280031\t-3858\t-6463\tLab\t471521\tLABACETA\tACETAMINOPHEN, SERUM
-38543619\t-6562\t-4489\tLab\t898794\tLABCSMP\tCANCER SOMATIC MUTATION PANEL
-35954787\t-7074\t-6965\tLab\t898794\tLABCSMP\tCANCER SOMATIC MUTATION PANEL
-22793877\t-3261\t-4837\tLab\t471944\tLABCBCD\tCBC WITH DIFF
-40604146\t-7480\t-8730\tLab\t896082\t10355R\tHLA - MONITORING BY IGG
-33765278\t-4255\t-622\tLab\t896082\t10355R\tHLA - MONITORING BY IGG
-39004110\t-5750\t-4953\tLab\t472748\tLABYLEPTN\tLEPTIN
-22910018\t-1862\t-621\tLab\t472785\tLABMGN\tMAGNESIUM, SERUM/PLASMA
-22840955\t-9532\t-639\tLab\t472837\tLABTNI\tTROPONIN I
-21479311\t-9844\t-5135\tLab\t473684\tLABMETB\tMETABOLIC PANEL, BASIC
-19231504\t-1518\t-3744\tLab\t473684\tLABMETB\tMETABOLIC PANEL, BASIC
-19007449\t-9542\t-4105\tLab\t473684\tLABMETB\tMETABOLIC PANEL, BASIC
-1748206\t-1099\t-9890\tLab\t473766\tLABY25VD\tVITAMIN D, 25-HYDROXY
-2794591\t-4038\t-6687\tLab\t473766\tLABY25VD\tVITAMIN D, 25-HYDROXY
-3580354\t-2795\t-752\tLab\t473766\tLABY25VD\tVITAMIN D, 25-HYDROXY
-3347071\t-6139\t-7104\tLab\t473766\tLABY25VD\tVITAMIN D, 25-HYDROXY
-4464954\t-4591\t-1383\tLab\t473766\tLABY25VD\tVITAMIN D, 25-HYDROXY
-3393444\t-5157\t-5537\tLab\t473766\tLABY25VD\tVITAMIN D, 25-HYDROXY
-2658433\t-6894\t-211\tLab\t473766\tLABY25VD\tVITAMIN D, 25-HYDROXY
"""
        DBUtil.insertFile( StringIO(dataTextStr), "stride_order_proc", delim="\t");

        # Deliberately design dates in far future to facilitate isolated testing
        dataTextStr = \
            """order_proc_id\tline\tresult_time\tcommon_name\tbase_name\tord_num_value\tresult_flag\tresult_in_range_yn
-4464954\t2\t5/28/2113 23:28\t25-HYDROXY D3\t25OHD3\t55\tNone\tNone
-3580354\t2\t12/17/2113 0:40\t25-HYDROXY D3\t25OHD3\t49\tNone\tNone
-3393444\t2\t10/9/2113 5:03\t25-HYDROXY D3\t25OHD3\t65\tNone\tNone
-3347071\t2\t9/8/2113 22:10\t25-HYDROXY D3\t25OHD3\t2\tNone\tNone
-2794591\t2\t3/19/2113 19:26\t25-HYDROXY D3\t25OHD3\t70\tNone\tNone
-2658433\t2\t7/5/2111 0:28\t25-HYDROXY D3\t25OHD3\t45\tNone\tNone
-1748206\t2\t7/3/2111 14:21\t25-HYDROXY D3\t25OHD3\t50\tNone\tNone
-36668349\t1\t10/30/2111 7:23\tACETAMINOPHEN(ACETA)\tACETA\t7.7\tNone\tNone
-33280031\t1\t11/29/2111 7:41\tACETAMINOPHEN(ACETA)\tACETA\t9999999\tNone\tNone
-33197720\t1\t11/29/2111 15:22\tACETAMINOPHEN(ACETA)\tACETA\tNone\tNone\tNone
-31823670\t1\t11/29/2111 14:08\tACETAMINOPHEN(ACETA)\tACETA\t5.4\tNone\tNone
-31300455\t1\t11/29/2111 18:58\tACETAMINOPHEN(ACETA)\tACETA\t270.7\tNone\tNone
-31237072\t1\t11/29/2111 5:45\tACETAMINOPHEN(ACETA)\tACETA\t50.6\tNone\tNone
-30560253\t1\t11/29/2111 16:13\tACETAMINOPHEN(ACETA)\tACETA\t2.6\tNone\tNone
-29966444\t1\t11/29/2111 2:27\tACETAMINOPHEN(ACETA)\tACETA\t4.2\tNone\tNone
-29501223\t1\t11/29/2111 0:15\tACETAMINOPHEN(ACETA)\tACETA\t5.1\tNone\tNone
-22793877\t4\t11/29/2111 14:36\tHEMATOCRIT(HCT)\tHCT\t19.7\tLow Panic\tNone
-22793877\t3\t11/30/2111 7:36\tHEMOGLOBIN(HGB)\tHGB\t7\tLow Panic\tNone
-40604146\t15\t12/13/2111 18:12\tINTERPRETATION/ COMMENTS CLASS II 9374R\t9374R\tNone\tNone\tNone
-33765278\t10\t9/22/2112 20:26\tINTERPRETATION/ COMMENTS CLASS II 9374R\t9374R\t9999999\tNone\tNone
-39004110\t1\t8/26/2112 15:07\tLEPTIN\tYLEPT1\t20\tNone\tNone
-22910018\t1\t11/13/2112 8:18\tMAGNESIUM, SER/PLAS(MGN)\tMG\t2.1\tNone\tY
-22793877\t6\t10/17/2112 1:09\tMCH(MCH)\tMCH\t31.7\tNone\tY
-22793877\t7\t12/13/2112 2:54\tMCHC(MCHC)\tMCHC\t35.4\tNone\tY
-22793877\t5\t11/11/2112 2:54\tMCV(MCV)\tMCV\t89.7\tNone\tY
-22793877\t9\t1/30/2113 13:28\tPLATELET COUNT(PLT)\tPLT\t11\tLow\tNone
-22793877\t2\t7/11/2113 23:24\tRBC(RBC)\tRBC\t2.2\tLow\tNone
-22793877\t8\t1/27/2113 14:44\tRDW(RDW)\tRDW\t33.3\tHigh\tNone
-21479311\t1\t8/31/2109 15:42\tSODIUM, SER/PLAS\tNA\t142\tNone\tNone
-19231504\t1\t8/20/2109 12:22\tSODIUM, SER/PLAS\tNA\t134\tLow\tNone
-19007449\t1\t9/13/2109 11:55\tSODIUM, SER/PLAS\tNA\t157\tHigh\tNone
-38543619\t15\t10/23/2109 14:30\tTP53(GTP53)\tGTP53\t9999999\tNone\tNone
-35954787\t15\t8/19/2109 16:39\tTP53(GTP53)\tGTP53\t9999999\tNone\tNone
-22793877\t1\t9/25/2109 16:10\tWBC(WBC)\tWBC\t0.2\tLow Panic\tNone
"""
        DBUtil.insertFile( StringIO(dataTextStr), "stride_order_results", delim="\t", dateColFormats={"result_time": None} );

        self.converter = STRIDEOrderResultsConversion();  # Instance to test on

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

        DBUtil.execute("delete from order_result_stat where base_name not like 'PreTest_%%';");

        DBUtil.execute("delete from stride_order_results where order_proc_id < 0" );
        DBUtil.execute("delete from stride_order_proc where order_proc_id < 0" );

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
                pi.num_value,
                pi.text_value,
                pi.item_date
            from
                patient_item as pi,
                clinical_item as ci,
                clinical_item_category as cic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = 'stride_order_results'
            order by
                pi.external_id desc, ci.name
            """;
        expectedData = \
            [
                [-1748206, -1099, -9890, 'Lab Result', None, '25OHD3(InRange)', '25-HYDROXY D3 (InRange)', 50, None, DBUtil.parseDateValue('7/3/2111 14:21'),],
                [-2658433, -6894, -211, 'Lab Result', None, '25OHD3(InRange)', '25-HYDROXY D3 (InRange)', 45, None, DBUtil.parseDateValue('7/5/2111 0:28'),],
                [-2794591, -4038, -6687, 'Lab Result', None, '25OHD3(InRange)', '25-HYDROXY D3 (InRange)', 70, None, DBUtil.parseDateValue('3/19/2113 19:26'),],
                [-3347071, -6139, -7104, 'Lab Result', None, '25OHD3(Low)', '25-HYDROXY D3 (Low)', 2, None, DBUtil.parseDateValue('9/8/2113 22:10'),],
                [-3393444, -5157, -5537, 'Lab Result', None, '25OHD3(InRange)', '25-HYDROXY D3 (InRange)', 65, None, DBUtil.parseDateValue('10/9/2113 5:03'),],
                [-3580354, -2795, -752, 'Lab Result', None, '25OHD3(InRange)', '25-HYDROXY D3 (InRange)', 49, None, DBUtil.parseDateValue('12/17/2113 0:40'),],
                [-4464954, -4591, -1383, 'Lab Result', None, '25OHD3(InRange)', '25-HYDROXY D3 (InRange)', 55, None, DBUtil.parseDateValue('5/28/2113 23:28'),],
                [-19007449, -9542, -4105, 'Lab Result', None, 'NA(High)', 'SODIUM, SER/PLAS (High)', 157, None, DBUtil.parseDateValue('9/13/2109 11:55'),],
                [-19231504, -1518, -3744, 'Lab Result', None, 'NA(Low)', 'SODIUM, SER/PLAS (Low)', 134, None, DBUtil.parseDateValue('8/20/2109 12:22'),],
                [-21479311, -9844, -5135, 'Lab Result', None, 'NA(InRange)', 'SODIUM, SER/PLAS (InRange)', 142, None, DBUtil.parseDateValue('8/31/2109 15:42'),],
                [-22793877, -3261, -4837, 'Lab Result', None, 'HCT(LowPanic)', 'HEMATOCRIT(HCT) (Low Panic)', 19.7, None, DBUtil.parseDateValue('11/29/2111 14:36'),],
                [-22793877, -3261, -4837, 'Lab Result', None, 'HGB(LowPanic)', 'HEMOGLOBIN(HGB) (Low Panic)', 7, None, DBUtil.parseDateValue('11/30/2111 7:36'),],
                [-22793877, -3261, -4837, 'Lab Result', None, 'MCH(InRange)', 'MCH(MCH) (InRange)', 31.7, None, DBUtil.parseDateValue('10/17/2112 1:09'),],
                [-22793877, -3261, -4837, 'Lab Result', None, 'MCHC(InRange)', 'MCHC(MCHC) (InRange)', 35.4, None, DBUtil.parseDateValue('12/13/2112 2:54'),],
                [-22793877, -3261, -4837, 'Lab Result', None, 'MCV(InRange)', 'MCV(MCV) (InRange)', 89.7, None, DBUtil.parseDateValue('11/11/2112 2:54'),],
                [-22793877, -3261, -4837, 'Lab Result', None, 'PLT(Low)', 'PLATELET COUNT(PLT) (Low)', 11, None, DBUtil.parseDateValue('1/30/2113 13:28'),],
                [-22793877, -3261, -4837, 'Lab Result', None, 'RBC(Low)', 'RBC(RBC) (Low)', 2.2, None, DBUtil.parseDateValue('7/11/2113 23:24'),],
                [-22793877, -3261, -4837, 'Lab Result', None, 'RDW(High)', 'RDW(RDW) (High)', 33.3, None, DBUtil.parseDateValue('1/27/2113 14:44'),],
                [-22793877, -3261, -4837, 'Lab Result', None, 'WBC(LowPanic)', 'WBC(WBC) (Low Panic)', 0.2, None, DBUtil.parseDateValue('9/25/2109 16:10'),],
                [-22910018, -1862, -621, 'Lab Result', None, 'MG(InRange)', 'MAGNESIUM, SER/PLAS(MGN) (InRange)', 2.1, None, DBUtil.parseDateValue('11/13/2112 8:18'),],
                [-29501223, -9860, -1772, 'Lab Result', None, 'ACETA(InRange)', 'ACETAMINOPHEN(ACETA) (InRange)', 5.1, None, DBUtil.parseDateValue('11/29/2111 0:15'),],
                [-29966444, -5690, -1150, 'Lab Result', None, 'ACETA(InRange)', 'ACETAMINOPHEN(ACETA) (InRange)', 4.2, None, DBUtil.parseDateValue('11/29/2111 2:27'),],
                [-30560253, -7803, -1772, 'Lab Result', None, 'ACETA(InRange)', 'ACETAMINOPHEN(ACETA) (InRange)', 2.6, None, DBUtil.parseDateValue('11/29/2111 16:13'),],
                [-31237072, -124, -8391, 'Lab Result', None, 'ACETA(InRange)', 'ACETAMINOPHEN(ACETA) (InRange)', 50.6, None, DBUtil.parseDateValue('11/29/2111 5:45'),],
                [-31300455, -2168, -261, 'Lab Result', None, 'ACETA(High)', 'ACETAMINOPHEN(ACETA) (High)', 270.7, None, DBUtil.parseDateValue('11/29/2111 18:58'),],
                [-31823670, -2130, -3897, 'Lab Result', None, 'ACETA(InRange)', 'ACETAMINOPHEN(ACETA) (InRange)', 5.4, None, DBUtil.parseDateValue('11/29/2111 14:08'),],
                [-33197720, -9926, -4898, 'Lab Result', None, 'ACETA(Result)', 'ACETAMINOPHEN(ACETA) (Result)', None, None, DBUtil.parseDateValue('11/29/2111 15:22'),],
                [-33280031, -3858, -6463, 'Lab Result', None, 'ACETA(Result)', 'ACETAMINOPHEN(ACETA) (Result)', 9999999, None, DBUtil.parseDateValue('11/29/2111 7:41'),],
                [-33765278, -4255, -622, 'Lab Result', None, '9374R(Result)', 'INTERPRETATION/ COMMENTS CLASS II 9374R (Result)', 9999999, None, DBUtil.parseDateValue('9/22/2112 20:26'),],
                [-35954787, -7074, -6965, 'Lab Result', None, 'GTP53(Result)', 'TP53(GTP53) (Result)', 9999999, None, DBUtil.parseDateValue('8/19/2109 16:39'),],
                [-36668349, -9815, -3658, 'Lab Result', None, 'ACETA(InRange)', 'ACETAMINOPHEN(ACETA) (InRange)', 7.7, None, DBUtil.parseDateValue('10/30/2111 7:23'),],
                [-38543619, -6562, -4489, 'Lab Result', None, 'GTP53(Result)', 'TP53(GTP53) (Result)', 9999999, None, DBUtil.parseDateValue('10/23/2109 14:30'),],
                [-39004110, -5750, -4953, 'Lab Result', None, 'YLEPT1(InRange)', 'LEPTIN (InRange)', 20, None, DBUtil.parseDateValue('8/26/2112 15:07'),],
                [-40604146, -7480, -8730, 'Lab Result', None, '9374R(Result)', 'INTERPRETATION/ COMMENTS CLASS II 9374R (Result)', None, None, DBUtil.parseDateValue('12/13/2111 18:12'),],
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );


        # Query back for stat data
        testQuery = \
            """
            select 
                base_name,
                max_result_flag,
                max_result_in_range
            from
                order_result_stat
            where
                base_name not like 'PreTest_%%'
            order by
                base_name
            """;
        # Don't necessarily expect stats for all items if always get a usable result_flag, result_in_range_yn, or sentinel result value
        expectedData = \
            [
                ["25OHD3",None,None],
                #["9374R",None,None],
                ["ACETA",None,None],
                #["GTP53",None,None],
                #["HCT","Low Panic",None],
                #["HGB","Low Panic",None],
                #["MCH",None,"Y"],
                #["MCHC",None,"Y"],
                #["MCV",None,"Y"],
                #["MG",None,"Y"],
                ["NA","Low",None],
                #["PLT","Low",None],
                #["RBC","Low",None],
                #["RDW","High",None],
                #["WBC","Low Panic",None],
                ["YLEPT1",None,None],
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestSTRIDEOrderResultsConversion("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestSTRIDEOrderResultsConversion("test_insertFile_skipErrors"));
    #suite.addTest(TestSTRIDEOrderResultsConversion('test_executeIterator'));
    #suite.addTest(TestSTRIDEOrderResultsConversion('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestSTRIDEOrderResultsConversion));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
