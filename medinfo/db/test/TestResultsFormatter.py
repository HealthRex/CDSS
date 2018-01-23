#!/usr/bin/env python
"""Test case for respective module in medinfo.Common package"""

import sys, os
from cStringIO import StringIO
import unittest

from datetime import datetime;

from Const import LOGGER_LEVEL, RUNNER_VERBOSITY;
from Util import log;

from Util import DBTestCase;

from medinfo.common.test.Util import MedInfoTestCase;

from medinfo.db.ResultsFormatter import TabDictReader;

class TestResultsFormatter(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        DBTestCase.tearDown(self);

    def test_TabDictReader(self):
        """Verify expected results when reading from different delimited file examples,
        particularly cases of messed up quoting or internal delimiter characters."""
        
        inFileStr = \
            """# Test comment line
            order_proc_id,"pat_id",pat_enc_csn_id,ordering_date,"order_type",proc_id,"proc_code","description","display_name","cpt_code","proc_cat_name","order_class","authrzing_prov_id","abnormal_yn","lab_status","order_status",quantity,"future_or_stand",standing_exp_date,standing_occurs,stand_orig_occur,"radiology_status",proc_bgn_time,proc_end_time,order_inst,"stand_interval","discrete_interval",instantiated_time,order_time,result_time,proc_start_time,problem_list_id,proc_ending_time,chng_order_proc_id,last_stand_perf_dt,last_stand_perf_tm,parent_ce_order_id,"ordering_mode"
            3488535,"7229924684871",444976,10/12/2009 00:00,"Nursing",472897,"NUR1018","MONITOR INTAKE AND OUTPUT","Monitor Intake And Output","NUR1018","NURSING - ASSESSMENT","Hospital Performed","376355","","","Sent",1,"",,,,"",,,10/12/2009 00:17,"","",10/12/2009 00:17,10/12/2009 00:17,,10/12/2009 04:00,,10/12/2009 00:00,,,,,"Inpatient"
            4530091,"11715476458129",417026,11/19/2009 00:00,"Nursing",498171,"NUR1940","NURSING COMMUNICATION","Give patient "Bedside Insulin Pump Flow Sheet" to document insulin delivery, BG and carbohydrates","NUR1940","NURSING - TREATMENT","Hospital Performed","355432","","","",1,"S",,,1,"",,,11/19/2009 11:55,"CONTINUOUS","",,11/19/2009 11:55,,11/19/2009 12:00,,,,11/19/2009 00:00,,,"Inpatient"
            5905631,"10720939760322",387975,01/16/2010 00:00,"Nursing",473324,"NUR1182","SIGN ABOVE BED 'DO NOT REPOSITION NG'","Sign above bed"Do not reposition NG"","NUR1182","NURSING - DRAINS AND TUBES","Hospital Performed","314969","","","Canceled",1,"S",,,1,"",,,01/16/2010 18:31,"CONTINUOUS","",,01/16/2010 18:31,,01/16/2010 18:45,,,,01/16/2010 00:00,,,"Inpatient"
            """
        inFile = StringIO(inFileStr);
        reader = TabDictReader(inFile, delimiter=",");
        parsedData = list(reader); # Convert to an in-memory list
        expectedData = \
            [   {"order_proc_id":"3488535", "display_name":"Monitor Intake And Output"},
                {"order_proc_id":"4530091", "display_name":"Give patient \"Bedside Insulin Pump Flow Sheet\" to document insulin delivery, BG and carbohydrates"},
                {"order_proc_id":"5905631", "display_name":"Sign above bed\"Do not reposition NG\""},
            ];
        targetKeys = expectedData[0].keys();    # Check a subset of values for simplicity
        self.assertEqualDictList( expectedData, parsedData, targetKeys );

        # Another test on messed up order_med end double quote
        inFileStr = \
            """order_med_id,pat_id,pat_enc_csn_id,ordering_date,ORDER_CLASS_C,order_class_name,MEDICATION_ID,description,QUANTITY,REFILLS,start_taking_time,order_end_time,end_taking_time,RSN_FOR_DISCON_C,rsn_for_discon,MED_PRESC_PROV_ID,DISPLAY_NAME,ORDER_PRIORITY_C,order_priority,MED_ROUTE_C,med_route,discon_time,CHNG_ORDER_MED_ID,HV_DISCR_FREQ_ID,freq_name,discrete_frequency,HV_DISCRETE_DOSE,HV_DOSE_UNIT_C,hv_dose_unit,ORDER_STATUS_C,order_status,AUTHRZING_PROV_ID,ORD_PROV_ID,MIN_DISCRETE_DOSE,MAX_DISCRETE_DOSE,DOSE_UNIT_C,dose_unit,PAT_LOC_ID,department_name,MODIFY_TRACK_C,modify_track,ACT_ORDER_C,active_order,LASTDOSE,AMB_MED_DISP_NAME,REFILLS_REMAINING,RESUME_STATUS_C,resume_status,ORDERING_MODE_C,ordering_mode,MED_DIS_DISP_QTY,MED_DIS_DISP_UNIT_C,dispense_unit,number_of_doses,doses_remaining,min_rate,max_rate,rate_unit_c,rate_unit,min_duration,max_duration,med_duration_unit_c,duration_unit_name,min_volume,max_volume,volume_unit_c,volume_unit,calc_volume_yn,calc_min_dose,calc_max_dose,calc_dose_unit_c,calc_dose_unit,admin_min_dose,admin_max_dose,admin_dose_unit_c,admin_dose_unit
            4880261,-11815067487752,418519,09/16/2009 11:49,8,"Fax",2567,"DOCUSATE SODIUM 50 MG/5 ML PO LIQD","","",09/16/2009 12:00,09/17/2009 21:26,09/18/2009 04:26,,"",360247,"docusate (COLACE) capsule 250 mg",,"",15,"Oral",09/18/2009 04:26,,"200006","2 TIMES DAILY","BID","250",3,"mg",9,"Discontinued",360247,377971,250,,3,"mg",2000262,"E2-ICU","","",3,"Discontinued Medication","","",,,"",2,"Inpatient",,,"",,,,,,"",,,,"",,,,"","Y",250,,3,"mg",1,,5003,"Cap"
            5226027,-5331130233402,455118,06/26/2011 07:56,1,"Normal",8751,"WARFARIN 5 MG PO TABS","","",06/26/2011 18:00,06/27/2011 07:44,06/27/2011 14:44,,"",345517,"warfarin (COUMADIN) tablet 5 mg "Pharmacy Protocol"",,"",15,"Oral",06/27/2011 14:44,385146643,"200023","DAILY","QPM","5",3,"mg",9,"Discontinued",345517,372188,5,,3,"mg",2000273,"D3","2","MODIFIED",3,"Discontinued Medication","","",,,"",2,"Inpatient",,,"",,,,,,"",,,,"",,,,"","",5,,3,"mg",1,,5002,"Tab"
            3579366,4662062643677,385175,04/18/2013 14:09,60,"E-Prescribe",89742,"NPH INSULIN HUMAN RECOMB 100 UNIT/ML SC SUSP","10 mL","2",04/18/2013 00:00,09/14/2013 00:00,09/14/2013 22:05,,"",314742,"",6,"Routine",18,"Subcutaneous",09/14/2013 22:05,417486280,"200009","2 TIMES DAILY WITH MEALS","BID with Meals","10",5,"Units",2,"Sent",314742,396419,10,,5,"Units",2000253,"C3","1","REORDERED",1,"Active Medication","8/10/2013","insulin NPH 100 unit/mL injection",2,2,"Sent",1,"Outpatient",10,1,"mL",,,,,,"",,,,"",,,,"","",10,,5,"Units",10,,5,"Units"
            """;
        inFile = StringIO(inFileStr);
        reader = TabDictReader(inFile, delimiter=",");
        parsedData = list(reader); # Convert to an in-memory list
        expectedData = \
            [   {"order_med_id":"4880261", "DISPLAY_NAME":"docusate (COLACE) capsule 250 mg"},
                {"order_med_id":"5226027", "DISPLAY_NAME":"warfarin (COUMADIN) tablet 5 mg \"Pharmacy Protocol\""},
                {"order_med_id":"3579366", "DISPLAY_NAME":""},
            ];
        targetKeys = expectedData[0].keys();    # Check a subset of values for simplicity
        self.assertEqualDictList( expectedData, parsedData, targetKeys );

        #    1748628,-3085618212893,408616,06/27/2010 08:28,8,"Fax",21372,"WARFARIN 4 MG PO TABS","","",06/27/2010 18:00,06/28/2010 08:36,06/28/2010 15:36,,"",365888,"warfarin (COUMADIN) tablet 4 mg (Per Pharmacy Protocol"",,"",15,"Oral",06/28/2010 15:36,368883925,"200023","DAILY","QPM","4",3,"mg",9,"Discontinued",365888,372188,4,,3,"mg",2000253,"C3","2","MODIFIED",3,"Discontinued Medication","","",,,"",2,"Inpatient",,,"",,,,,,"",,,,"",,,,"","Y",4,,3,"mg",1,,5002,"Tab"
        #        {"order_med_id":"1748628", "DISPLAY_NAME":"warfarin (COUMADIN) tablet 4 mg (Per Pharmacy Protocol\""},



def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestResultsFormatter("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestResultsFormatter("test_insertFile_skipErrors"));
    #suite.addTest(TestResultsFormatter('test_insertFile_dateParsing'));
    #suite.addTest(TestResultsFormatter('test_deleteRows'));
    suite.addTest(unittest.makeSuite(TestResultsFormatter));
    return suite;

if __name__=="__main__":
    log.setLevel(LOGGER_LEVEL)

    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
