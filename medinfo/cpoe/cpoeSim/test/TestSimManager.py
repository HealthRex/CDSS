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
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable;

from medinfo.cpoe.cpoeSim.SimManager import SimManager;

class TestSimManager(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);

        self.manager = SimManager();  # Instance to test on

        from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader; 
        ClinicalItemDataLoader.build_clinical_item_psql_schemata();
        self.manager.buildCPOESimSchema();

        self.testPatientId = None;

        self.purgeTestRecords();

        log.info("Populate the database with test data")

        self.clinicalItemCategoryIdStrList = list();
        headers = ["clinical_item_category_id","source_table"];
        dataModels = \
            [
                RowItemModel( [-1, "Labs"], headers ),
                RowItemModel( [-2, "Imaging"], headers ),
                RowItemModel( [-3, "Meds"], headers ),
                RowItemModel( [-4, "Nursing"], headers ),
                RowItemModel( [-5, "Problems"], headers ),
                RowItemModel( [-6, "Lab Results"], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", dataModel );
            self.clinicalItemCategoryIdStrList.append( str(dataItemId) );

        headers = ["clinical_item_id","clinical_item_category_id","name","analysis_status"];
        dataModels = \
            [
                RowItemModel( [-1, -1, "CBC",1], headers ),
                RowItemModel( [-2, -1, "BMP",1], headers ),
                RowItemModel( [-3, -1, "Hepatic Panel",1], headers ),
                RowItemModel( [-4, -1, "Cardiac Enzymes",1], headers ),
                RowItemModel( [-5, -2, "CXR",1], headers ),
                RowItemModel( [-6, -2, "RUQ Ultrasound",1], headers ),
                RowItemModel( [-7, -2, "CT Abdomen/Pelvis",1], headers ),
                RowItemModel( [-8, -2, "CT PE Thorax",1], headers ),
                RowItemModel( [-9, -3, "Acetaminophen",1], headers ),
                RowItemModel( [-10, -3, "Carvedilol",1], headers ),
                RowItemModel( [-11, -3, "Enoxaparin",1], headers ),
                RowItemModel( [-12, -3, "Warfarin",1], headers ),
                RowItemModel( [-13, -3, "Ceftriaxone",1], headers ),
                RowItemModel( [-14, -4, "Foley Catheter",1], headers ),
                RowItemModel( [-15, -4, "Vital Signs",1], headers ),
                RowItemModel( [-16, -4, "Fall Precautions",1], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", dataModel );


        dataTextStr = \
"""sim_user_id;name
-1;Test User
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "sim_user", delim=";");

        dataTextStr = \
"""sim_patient_id;age_years;gender;name
-1;60;Female;Test Female Patient
-2;55;Male;Test Male Patient
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "sim_patient", delim=";");

        dataTextStr = \
"""sim_result_id;name;description;group_string;priority
-10;Temp;Temperature (F);Flowsheet>Vitals;10
-20;Pulse;Pulse / Heart Rate (HR);Flowsheet>Vitals;20
-30;SBP;Blood Pressure, Systolic (SBP);Flowsheet>Vitals;30
-40;DBP;Blood Pressure, Diastolic (DBP);Flowsheet>Vitals;40
-50;Resp;Respirations (RR);Flowsheet>Vitals;50
-60;FiO2;Fraction Inspired Oxygen;Flowsheet>Vitals;60
-70;Urine;Urine Output (UOP);Flowsheet>Vitals;70
-11000;WBC;WBC;LAB BLOOD ORDERABLES>Hematology>Automated Blood Count;11000
-11010;HGB;HEMOGLOBIN;LAB BLOOD ORDERABLES>Hematology>Automated Blood Count;11010
-11020;HCT;HEMATOCRIT;LAB BLOOD ORDERABLES>Hematology>Automated Blood Count;11020
-11030;PLT;PLATELET COUNT;LAB BLOOD ORDERABLES>Hematology>Automated Blood Count;11030
-13010;NA;SODIUM, SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13010
-13020;K;POTASSIUM, SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13020
-13030;CL;CHLORIDE, SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13030
-13040;CO2;CO2, SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13040
-13050;BUN;UREA NITROGEN,SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13050
-13060;CR;CREATININE, SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13060
-13070;GLU;GLUCOSE, SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13070
-13090;CA;CALCIUM, SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13090
-13110;MG;MAGNESIUM, SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13110
-13120;PHOS;PHOSPHORUS, SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13120
-13210;TBIL;TOTAL BILIRUBIN;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13210
-13220;DBIL;CONJUGATED BILI;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13220
-13230;IBIL;UNCONJUGATED BILIRUBIN;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13230
-13240;AST;AST (SGOT), SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13240
-13250;ALT;ALT (SGPT), SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13250
-13260;ALKP;ALK P'TASE, TOTAL, SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13260
-13270;ALB;ALBUMIN, SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13270
-13280;TP;PROTEIN, TOTAL, SER/PLAS;LAB BLOOD ORDERABLES>Chemistry>General Chemistry;13280
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "sim_result", delim=";");

        # Map orders to expected results.
        # Simplify expect vital signs to result in 5 minutes. Basic chemistry labs in 10 minutes, CBC in 15 minutes
        dataTextStr = \
"""sim_order_result_map_id;clinical_item_id;sim_result_id;turnaround_time
-1;-15;-10;300
-2;-15;-20;300
-3;-15;-30;300
-4;-15;-40;300
-5;-15;-50;300
-6;-1;-11000;900
-7;-1;-11010;900
-8;-1;-11020;900
-9;-1;-11030;900
-10;-2;-13010;600
-11;-2;-13020;600
-12;-2;-13030;600
-13;-2;-13040;600
-14;-2;-13050;600
-15;-2;-13060;600
-16;-2;-13070;600
-17;-2;-13090;600
-18;-3;-13210;600
-19;-3;-13240;600
-20;-3;-13250;600
-21;-3;-13260;600
-22;-3;-13270;600
-23;-3;-13280;600
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "sim_order_result_map", delim=";");


        dataTextStr = \
"""sim_state_id;name;description
0;Test 0; Test State 0
-1;Test 1;Test State 1
-2;Test 2;Test State 2
-3;Test 3;Test State 3
-4;Test 4;Test State 4
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "sim_state", delim=";");

        dataTextStr = \
"""sim_state_transition_id;pre_state_id;post_state_id;clinical_item_id;time_trigger;description
-1;-1;-2;None;9000;Passive time from 1 to 2
-2;-2;-3;-11;None;Transition 2 to 3 if order for 11 (Enoxaparin)
-3;-2;-3;-12;None;Transition 2 to 3 if order for 12 (Warfarin) (don't need both anti-coagulants. One adequate to trigger transition)
-4;-2;-4;-13;None;Transition 2 to 4 if order for 13 (Ceftriaxone)
-5;-3;-1;-10;9000;Transition 3 back to 1 if order for 10 (Carvedilol) OR 9000 seconds pass
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "sim_state_transition", delim=";");

        dataTextStr = \
"""sim_patient_state_id;sim_patient_id;sim_state_id;relative_time_start;relative_time_end
-1;-1;-1;-7200;0
-3;-1;-1;0;1800
-2;-1;-2;1800;None
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "sim_patient_state", delim=";");

        # Order Vital Signs at time 0, then basic labs (CBC, BMP, LFTs) at 10 minutes (600 seconds)
        dataTextStr = \
"""sim_patient_order_id;sim_user_id;sim_patient_id;sim_state_id;clinical_item_id;relative_time_start;relative_time_end
-1;-1;-1;-1;-15;0;None
-2;-1;-1;-1;-1;600;None
-3;-1;-1;-1;-2;600;None
-4;-1;-1;-1;-3;600;None
-5;-1;-1;-2;-15;1800;None
-6;-1;-1;-2;-1;1800;None
-7;-1;-1;-2;-2;1800;None
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "sim_patient_order", delim=";");

        dataTextStr = \
"""sim_state_result_id;sim_result_id;sim_state_id;num_value;num_value_noise;text_value;result_flag
-1;-10;0;98.7;0.2;;
-2;-20;0;75;3;;
-3;-30;0;130;4;;
-4;-40;0;85;2;;
-5;-50;0;12;1;;
-6;-60;0;0.21;0;;
-7;-70;0;500;100;;
-8;-11000;0;7;1;;
-9;-11010;0;13;0.5;;
-10;-11020;0;40;1;;
-11;-11030;0;300;25;;
-12;-13010;0;140;4;;
-13;-13020;0;4.5;0.4;;
-14;-13030;0;95;3;;
-15;-13040;0;24;1;;
-16;-13050;0;12;3;;
-17;-13060;0;0.7;0.2;;
-18;-13070;0;140;12;;
-19;-13090;0;9;0.4;;
-20;-13110;0;2;0.3;;
-21;-13120;0;3;0.5;;
-22;-13210;0;0.2;0.1;;
-23;-13240;0;29;5;;
-24;-13250;0;20;4;;
-25;-13260;0;85;8;;
-26;-13270;0;4;0.4;;
-27;-13280;0;6;0.5;;
-28;-10;-1;101.4;0.4;Fever;H
-29;-20;-1;115;4;Tachycardia;H
-30;-30;-1;92;5;Hypotension;L
-31;-40;-1;55;3;Hypotension;L
-32;-70;-1;50;10;Low UOP;L
-33;-11000;-1;12;1;Leukocytosis;H
-34;-13060;-1;2.4;0.3;AKI;H
-35;-20;-2;105;4;Tachycardia;H
-36;-11000;-2;10;1;;
-37;-13060;-2;1.9;0.3;AKI;H
-38;-13070;-2;250;13;;H
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "sim_state_result", delim=";");

        dataTextStr = \
"""sim_note_id;sim_state_id;relative_state_time;content
-1;-1;7200;Initial Note
-2;-2;0;Later Note
"""     # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "sim_note", delim=";");

    def purgeTestRecords(self):
        log.info("Purge test records from the database")
        if self.testPatientId is not None:
            # Delete test generated data
            DBUtil.execute("delete from sim_patient_order where sim_patient_id = %s", (self.testPatientId,) );
            DBUtil.execute("delete from sim_patient_state where sim_patient_id = %s", (self.testPatientId,) );
            DBUtil.execute("delete from sim_patient where sim_patient_id = %s", (self.testPatientId,) );

        DBUtil.execute("delete from sim_note where sim_note_id < 0");
        DBUtil.execute("delete from sim_state_result where sim_state_result_id < 0");
        DBUtil.execute("delete from sim_patient_order where sim_state_id < 0 or sim_patient_order_id < 0");
        DBUtil.execute("delete from sim_order_result_map where sim_order_result_map_id < 0");
        DBUtil.execute("delete from sim_result where sim_result_id < 0");
        DBUtil.execute("delete from sim_patient_state where sim_state_id < 0 or sim_patient_state_id < 0");
        DBUtil.execute("delete from sim_state_transition where pre_state_id < 0");
        DBUtil.execute("delete from sim_state where sim_state_id <= 0");
        DBUtil.execute("delete from sim_user where sim_user_id < 0");
        DBUtil.execute("delete from sim_patient where sim_patient_id < 0");
        DBUtil.execute("delete from clinical_item where clinical_item_id < 0");

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        self.purgeTestRecords();
        DBTestCase.tearDown(self);

    def test_copyPatientTemplate(self):
        # Copy a patient template, including deep copy of notes, orders, states, but only up to relative time zero
        newPatientData = {"name":"Template Copy"};
        templatePatientId = -1;
        self.testPatientId = self.manager.copyPatientTemplate( newPatientData, templatePatientId );
        futureTime = 1000000;   # Far future time to test that we still only copied the results up to time zero

        # Verify basic patient information
        patientCols = ["name","age_years","gender","sim_state_id"];
        patientModel = self.manager.loadPatientInfo([self.testPatientId])[0];
        expectedPatientModel = RowItemModel(["Template Copy",60,"Female",-1], patientCols);
        self.assertEqualDict(expectedPatientModel, patientModel, patientCols);

        # Verify notes
        dataCols = ["sim_patient_id","content"];
        sampleData = self.manager.loadNotes(self.testPatientId, futureTime);
        verifyData = \
            [   RowItemModel([self.testPatientId,"Initial Note"], dataCols),
                RowItemModel([self.testPatientId,"Initial Note"], dataCols),    # Second copy because another state initiation at time zero and negative onset time
            ];
        self.assertEqualDictList(verifyData, sampleData, dataCols);

        # Verify orders
        dataCols = ["sim_user_id","sim_patient_id","sim_state_id","clinical_item_id","relative_time_start","relative_time_end"];
        sampleData = self.manager.loadPatientOrders(self.testPatientId, futureTime, loadActive=None);
        verifyData = \
            [   RowItemModel([-1,self.testPatientId,-1,-15,0,None], dataCols),
            ];
        self.assertEqualDictList(verifyData, sampleData, dataCols);

        # Verify states
        dataCols = ["sim_patient_id","sim_state_id","relative_time_start","relative_time_end"];
        query = SQLQuery();
        for dataCol in dataCols:
            query.addSelect(dataCol);
        query.addFrom("sim_patient_state");
        query.addWhereEqual("sim_patient_id", self.testPatientId );
        query.addOrderBy("relative_time_start");
        sampleDataTable = DBUtil.execute(query,includeColumnNames=True);
        sampleData = modelListFromTable(sampleDataTable);
        verifyData = \
            [   RowItemModel([self.testPatientId,-1,-7200,0], dataCols),
                RowItemModel([self.testPatientId,-1,0,None], dataCols),
            ];
        self.assertEqualDictList(verifyData, sampleData, dataCols);

    def test_loadResults(self):
        # Query for results based on simulated turnaround times, including fallback to default normal values
        #   if no explicit (abnormal) values specified for simulated state

        colNames = ["name", "num_value", "result_relative_time"];

        # Time zero, no orders for diagnostics, so no results should exist
        patientId = -1;
        relativeTime = 0;
        sampleResults = self.manager.loadResults(patientId, relativeTime);
        verifyResults = \
            [
            ];
        self.assertEqualDictList(verifyResults, sampleResults, colNames);

        # Time 2 minutes, orders done, but not long-enough to get results back, so no results should exist
        relativeTime = 120;
        sampleResults = self.manager.loadResults(patientId, relativeTime);
        verifyResults = \
            [
            ];
        self.assertEqualDictList(verifyResults, sampleResults, colNames);

        # Time 5 minutes, vital signs should result now
        relativeTime = 300;
        sampleResults = self.manager.loadResults(patientId, relativeTime);
        verifyResults = \
            [
                RowItemModel(["Temp", 101.4, 300], colNames),
                RowItemModel(["Pulse", 115, 300], colNames),
                RowItemModel(["SBP", 92, 300], colNames),
                RowItemModel(["DBP", 55, 300], colNames),
                RowItemModel(["Resp", 12, 300], colNames),  # Normal result retrieve from default state 0
            ];
        self.assertEqualDictList(verifyResults, sampleResults, colNames);

        # Time 10 minutes, labs ordered, but not results expected yet. Prior vital signs should still be available.
        relativeTime = 600;
        sampleResults = self.manager.loadResults(patientId, relativeTime);
        verifyResults = \
            [
                RowItemModel(["Temp", 101.4, 300], colNames),
                RowItemModel(["Pulse", 115, 300], colNames),
                RowItemModel(["SBP", 92, 300], colNames),
                RowItemModel(["DBP", 55, 300], colNames),
                RowItemModel(["Resp", 12, 300], colNames),  # Normal result retrieve from default state 0
            ];
        self.assertEqualDictList(verifyResults, sampleResults, colNames);

        # Time 20 minutes, labs ordered 10 minutes ago, should have chemistry results
        relativeTime = 1200;
        sampleResults = self.manager.loadResults(patientId, relativeTime);
        verifyResults = \
            [
                RowItemModel(["Temp", 101.4, 300], colNames),
                RowItemModel(["Pulse", 115, 300], colNames),
                RowItemModel(["SBP", 92, 300], colNames),
                RowItemModel(["DBP", 55, 300], colNames),
                RowItemModel(["Resp", 12, 300], colNames),  # Normal result retrieve from default state 0

                RowItemModel(["NA", 140, 1200], colNames),
                RowItemModel(["K", 4.5, 1200], colNames),
                RowItemModel(["CL", 95, 1200], colNames),
                RowItemModel(["CO2", 24, 1200], colNames),
                RowItemModel(["BUN", 12, 1200], colNames),
                RowItemModel(["CR", 2.4, 1200], colNames),  # Abnormal value in state 1, all others default state 0
                RowItemModel(["GLU", 140, 1200], colNames),
                RowItemModel(["CA", 9, 1200], colNames),
                RowItemModel(["TBIL", 0.2, 1200], colNames),
                RowItemModel(["AST", 29, 1200], colNames),
                RowItemModel(["ALT", 20, 1200], colNames),
                RowItemModel(["ALKP", 85, 1200], colNames),
                RowItemModel(["ALB", 4, 1200], colNames),
                RowItemModel(["TP", 6, 1200], colNames),
            ];
        self.assertEqualDictList(verifyResults, sampleResults, colNames);

        # Time 25 minutes, CBC results should now be available as well
        relativeTime = 1500;
        sampleResults = self.manager.loadResults(patientId, relativeTime);
        verifyResults = \
            [
                RowItemModel(["Temp", 101.4, 300], colNames),
                RowItemModel(["Pulse", 115, 300], colNames),
                RowItemModel(["SBP", 92, 300], colNames),
                RowItemModel(["DBP", 55, 300], colNames),
                RowItemModel(["Resp", 12, 300], colNames),  # Normal result retrieve from default state 0

                RowItemModel(["NA", 140, 1200], colNames),
                RowItemModel(["K", 4.5, 1200], colNames),
                RowItemModel(["CL", 95, 1200], colNames),
                RowItemModel(["CO2", 24, 1200], colNames),
                RowItemModel(["BUN", 12, 1200], colNames),
                RowItemModel(["CR", 2.4, 1200], colNames),  # Abnormal value in state 1, all others default state 0
                RowItemModel(["GLU", 140, 1200], colNames),
                RowItemModel(["CA", 9, 1200], colNames),
                RowItemModel(["TBIL", 0.2, 1200], colNames),
                RowItemModel(["AST", 29, 1200], colNames),
                RowItemModel(["ALT", 20, 1200], colNames),
                RowItemModel(["ALKP", 85, 1200], colNames),
                RowItemModel(["ALB", 4, 1200], colNames),
                RowItemModel(["TP", 6, 1200], colNames),

                RowItemModel(["WBC", 12, 1500], colNames),  # Abnormal state value
                RowItemModel(["HGB", 13, 1500], colNames),
                RowItemModel(["HCT", 40, 1500], colNames),
                RowItemModel(["PLT", 300, 1500], colNames),

            ];
        self.assertEqualDictList(verifyResults, sampleResults, colNames);

        # Time 30 minutes, patient entered new state (-2), and repeat vitals + labs ordered, but no new results yet due to turnaround time
        relativeTime = 1800;
        sampleResults = self.manager.loadResults(patientId, relativeTime);
        verifyResults = \
            [
                RowItemModel(["Temp", 101.4, 300], colNames),
                RowItemModel(["Pulse", 115, 300], colNames),
                RowItemModel(["SBP", 92, 300], colNames),
                RowItemModel(["DBP", 55, 300], colNames),
                RowItemModel(["Resp", 12, 300], colNames),  # Normal result retrieve from default state 0

                RowItemModel(["NA", 140, 1200], colNames),
                RowItemModel(["K", 4.5, 1200], colNames),
                RowItemModel(["CL", 95, 1200], colNames),
                RowItemModel(["CO2", 24, 1200], colNames),
                RowItemModel(["BUN", 12, 1200], colNames),
                RowItemModel(["CR", 2.4, 1200], colNames),  # Abnormal value in state 1, all others default state 0
                RowItemModel(["GLU", 140, 1200], colNames),
                RowItemModel(["CA", 9, 1200], colNames),
                RowItemModel(["TBIL", 0.2, 1200], colNames),
                RowItemModel(["AST", 29, 1200], colNames),
                RowItemModel(["ALT", 20, 1200], colNames),
                RowItemModel(["ALKP", 85, 1200], colNames),
                RowItemModel(["ALB", 4, 1200], colNames),
                RowItemModel(["TP", 6, 1200], colNames),

                RowItemModel(["WBC", 12, 1500], colNames),  # Abnormal state value
                RowItemModel(["HGB", 13, 1500], colNames),
                RowItemModel(["HCT", 40, 1500], colNames),
                RowItemModel(["PLT", 300, 1500], colNames),

            ];
        self.assertEqualDictList(verifyResults, sampleResults, colNames);

        # Time 45 minutes, patient second state and repeat labs, should retrieve both new and old results (with relative timestamps)
        relativeTime = 2700;
        sampleResults = self.manager.loadResults(patientId, relativeTime);
        verifyResults = \
            [
                RowItemModel(["Temp", 101.4, 300], colNames),
                RowItemModel(["Pulse", 115, 300], colNames),
                RowItemModel(["SBP", 92, 300], colNames),
                RowItemModel(["DBP", 55, 300], colNames),
                RowItemModel(["Resp", 12, 300], colNames),  # Normal result retrieve from default state 0

                RowItemModel(["NA", 140, 1200], colNames),
                RowItemModel(["K", 4.5, 1200], colNames),
                RowItemModel(["CL", 95, 1200], colNames),
                RowItemModel(["CO2", 24, 1200], colNames),
                RowItemModel(["BUN", 12, 1200], colNames),
                RowItemModel(["CR", 2.4, 1200], colNames),  # Abnormal value in state 1, all others default state 0
                RowItemModel(["GLU", 140, 1200], colNames),
                RowItemModel(["CA", 9, 1200], colNames),
                RowItemModel(["TBIL", 0.2, 1200], colNames),
                RowItemModel(["AST", 29, 1200], colNames),
                RowItemModel(["ALT", 20, 1200], colNames),
                RowItemModel(["ALKP", 85, 1200], colNames),
                RowItemModel(["ALB", 4, 1200], colNames),
                RowItemModel(["TP", 6, 1200], colNames),

                RowItemModel(["WBC", 12, 1500], colNames),  # Abnormal state value
                RowItemModel(["HGB", 13, 1500], colNames),
                RowItemModel(["HCT", 40, 1500], colNames),
                RowItemModel(["PLT", 300, 1500], colNames),

                # State 2 Results
                RowItemModel(["Temp", 98.7, 2100], colNames),
                RowItemModel(["Pulse", 105, 2100], colNames),   # Still abnormal, other vitals revert to default
                RowItemModel(["SBP", 130, 2100], colNames),
                RowItemModel(["DBP", 85, 2100], colNames),
                RowItemModel(["Resp", 12, 2100], colNames),

                RowItemModel(["NA", 140, 2400], colNames),
                RowItemModel(["K", 4.5, 2400], colNames),
                RowItemModel(["CL", 95, 2400], colNames),
                RowItemModel(["CO2", 24, 2400], colNames),
                RowItemModel(["BUN", 12, 2400], colNames),
                RowItemModel(["CR", 1.9, 2400], colNames),  # Abnormal value in state 1, all others default state 0
                RowItemModel(["GLU", 250, 2400], colNames), # Newly abnormal value in state 2
                RowItemModel(["CA", 9, 2400], colNames),

                RowItemModel(["WBC", 10, 2700], colNames),  # Abnormal state value, but not as bad as prior state
                RowItemModel(["HGB", 13, 2700], colNames),
                RowItemModel(["HCT", 40, 2700], colNames),
                RowItemModel(["PLT", 300, 2700], colNames),
            ];
        self.assertEqualDictList(verifyResults, sampleResults, colNames);


    def test_discontinueOrders(self):
        # Query for results based on simulated turnaround times, including fallback to default normal values
        #   if no explicit (abnormal) values specified for simulated state

        colNames = ["name", "num_value", "result_relative_time"];

        # See setUp for test data construction
        userId = -1;
        patientId = -1;

        # Time zero, vital sign orders check entered (clinical_item_id = -15, sim_patient_order_id = -1)
        # Time 2 minutes, orders done, but not long-enough to get results back, so no results should exist
        relativeTime = 120;
        sampleResults = self.manager.loadResults(patientId, relativeTime);
        verifyResults = \
            [
            ];
        self.assertEqualDictList(verifyResults, sampleResults, colNames);

        # Time 5 minutes, vital signs should result now
        relativeTime = 300;
        sampleResults = self.manager.loadResults(patientId, relativeTime);
        verifyResults = \
            [
                RowItemModel(["Temp", 101.4, 300], colNames),
                RowItemModel(["Pulse", 115, 300], colNames),
                RowItemModel(["SBP", 92, 300], colNames),
                RowItemModel(["DBP", 55, 300], colNames),
                RowItemModel(["Resp", 12, 300], colNames),  # Normal result retrieve from default state 0
            ];
        self.assertEqualDictList(verifyResults, sampleResults, colNames);

        # Go back and simulate the vitals check order being discontinued before results came back
        discontinueTime = 120;
        newOrderItemIds = [];   # No new orders
        discontinuePatientOrderIds = [-1];  # See setUp data for the ID of the order to simulate canceling
        self.manager.signOrders(userId, patientId, discontinueTime, newOrderItemIds, discontinuePatientOrderIds);

        # Redo simulation of Time 5 minutes, vital signs should not appear now, since order was cancelled
        relativeTime = 300;
        sampleResults = self.manager.loadResults(patientId, relativeTime);
        verifyResults = \
            [
            ];
        self.assertEqualDictList(verifyResults, sampleResults, colNames);

        # Check that there is still a record of orders, including the cancelled one
        orderCols = ["name","relative_time_start","relative_time_end"];
        sampleOrders = self.manager.loadPatientOrders(patientId, 300, loadActive=None);
        verifyOrders = \
            [
                RowItemModel(["Vital Signs", 0, 120], orderCols),
            ];
        self.assertEqualDictList(verifyOrders, sampleOrders, orderCols);

        # Go back and simulate the vitals check order being discontinued immediately (same time as order),
        #   then don't even keep a record of it to clean up data entry error
        discontinueTime = 0;
        newOrderItemIds = [];   # No new orders
        discontinuePatientOrderIds = [-1];  # See setUp data for the ID of the order to simulate canceling
        self.manager.signOrders(userId, patientId, discontinueTime, newOrderItemIds, discontinuePatientOrderIds);

        # Check that there is no record of the order anymore, even including the cancelled one
        orderCols = ["name","relative_time_start","relative_time_end"];
        sampleOrders = self.manager.loadPatientOrders(patientId, 300, loadActive=None);
        verifyOrders = \
            [
            ];
        self.assertEqualDictList(verifyOrders, sampleOrders, orderCols);

    def test_stateTransition(self):
        # Query for results based on simulated turnaround times, including fallback to default normal values
        #   if no explicit (abnormal) values specified for simulated state

        colNames = ["sim_state_id"];

        userId = -1;
        patientId = -1;

        # Time zero, initial state expected
        relativeTime = 0;
        samplePatient = self.manager.loadPatientInfo([patientId], relativeTime)[0];
        verifyPatient = RowItemModel([-1], colNames);
        self.assertEqualDict(samplePatient, verifyPatient, colNames);

        # After previously recorded second state
        relativeTime = 2000;
        samplePatient = self.manager.loadPatientInfo([patientId], relativeTime)[0];
        verifyPatient = RowItemModel([-2], colNames);
        self.assertEqualDict(samplePatient, verifyPatient, colNames);

        # Sign orders that do not affect this state
        orderItemIds = [-4,-5];
        self.manager.signOrders(userId, patientId, relativeTime, orderItemIds);

        # Expect to stay in same state
        relativeTime = 2100;
        samplePatient = self.manager.loadPatientInfo([patientId], relativeTime)[0];
        verifyPatient = RowItemModel([-2], colNames);
        self.assertEqualDict(samplePatient, verifyPatient, colNames);

        # Sign orders that should trigger state transition
        relativeTime = 2100;
        orderItemIds = [-11,-6];
        self.manager.signOrders(userId, patientId, relativeTime, orderItemIds);

        # Expect transition to new state
        relativeTime = 2100;
        samplePatient = self.manager.loadPatientInfo([patientId], relativeTime)[0];
        verifyPatient = RowItemModel([-3], colNames);
        self.assertEqualDict(samplePatient, verifyPatient, colNames);

        # Expect transition to original state 1 then further to state 2 with enough time passage
        relativeTime = 22000;
        samplePatient = self.manager.loadPatientInfo([patientId], relativeTime)[0];
        verifyPatient = RowItemModel([-2], colNames);
        self.assertEqualDict(samplePatient, verifyPatient, colNames);

        # Retroactive query to verify state 1 intermediate transition state
        relativeTime = 12000;
        samplePatient = self.manager.loadPatientInfo([patientId], relativeTime)[0];
        verifyPatient = RowItemModel([-1], colNames);
        self.assertEqualDict(samplePatient, verifyPatient, colNames);

        # Sign alternative order to trigger state 2 to 3 transition as well as order to immediately trigger state 3 to 1
        relativeTime = 22000;
        orderItemIds = [-12,-10];
        self.manager.signOrders(userId, patientId, relativeTime, orderItemIds);

        # Expect transition to new state 3 them 1 immediately
        relativeTime = 22100;
        samplePatient = self.manager.loadPatientInfo([patientId], relativeTime)[0];
        verifyPatient = RowItemModel([-1], colNames);
        self.assertEqualDict(samplePatient, verifyPatient, colNames);

        # Expect transition back to state 2 with enough time
        relativeTime = 32200;
        samplePatient = self.manager.loadPatientInfo([patientId], relativeTime)[0];
        verifyPatient = RowItemModel([-2], colNames);
        self.assertEqualDict(samplePatient, verifyPatient, colNames);

        # Sign orders simultaneously that could trigger two different branching state transition paths
        #   Arbitrarily go based on the first action provided / encountered
        relativeTime = 32200;
        orderItemIds = [-13,-11,-12];
        self.manager.signOrders(userId, patientId, relativeTime, orderItemIds);

        # Expect transition back to branched state 4
        relativeTime = 32300;
        samplePatient = self.manager.loadPatientInfo([patientId], relativeTime)[0];
        verifyPatient = RowItemModel([-4], colNames);
        self.assertEqualDict(samplePatient, verifyPatient, colNames);

    def test_loadPatientLastEventTime(self):
        # Query for last time have a record of a patient order start or cancellation
        #   as natural point to resume a simulated case

        # See setUp for test data construction
        userId = -1;
        patientId = -1;

        # Initial test data already loaded with example orders
        sampleValue = self.manager.loadPatientLastEventTime(patientId);
        verifyValue = 1800;
        self.assertEqual(verifyValue, sampleValue);

        # Sign an additional order
        relativeTime = 2000;
        newOrderItemIds = [-1];   # Any additional order
        self.manager.signOrders(userId, patientId, relativeTime, newOrderItemIds);

        # Verify update of last order time
        sampleValue = self.manager.loadPatientLastEventTime(patientId);
        verifyValue = 2000;
        self.assertEqual(verifyValue, sampleValue);

        # Find and cancel the last order at a later time
        relativeTime = 2200;
        patientOrders = self.manager.loadPatientOrders(patientId, relativeTime);
        lastOrder = patientOrders[0];
        for patientOrder in patientOrders:
            if lastOrder["relative_time_start"] < patientOrder["relative_time_start"]:
                lastOrder = patientOrder;

        newOrderItemIds = [];   # No new orders
        discontinuePatientOrderIds = [lastOrder["sim_patient_order_id"]];
        self.manager.signOrders(userId, patientId, relativeTime, newOrderItemIds, discontinuePatientOrderIds);

        # Verify update of last order time includes discontinue times
        sampleValue = self.manager.loadPatientLastEventTime(patientId);
        verifyValue = 2200;
        self.assertEqual(verifyValue, sampleValue);

        # Lookup patient with no prior orders recorded, then should default to time 0
        patientId = -2;
        sampleValue = self.manager.loadPatientLastEventTime(patientId);
        verifyValue = 0;
        self.assertEqual(verifyValue, sampleValue);



def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestSimManager("test_copyPatientTemplate"));
    #suite.addTest(TestSimManager("test_loadPatientLastEventTime"));
    #suite.addTest(TestSimManager('test_executeIterator'));
    #suite.addTest(TestSimManager('test_stateTransition'));
    #suite.addTest(TestSimManager('test_discontinueOrders'));
    suite.addTest(unittest.makeSuite(TestSimManager));

    return suite;

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
