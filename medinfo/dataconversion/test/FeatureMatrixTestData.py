#!/usr/bin/env python
"""
Test input and output for FeatureMatrixFactory.
"""

from medinfo.db import DBUtil

# Dictionary mapping from database table name to test data.
FM_TEST_INPUT_TABLES = {
    "clinical_item_category" :
        "clinical_item_category_id\tsource_table\tdescription\n\
        -100\tTestTable\tTestCategory\n",
    "clinical_item" :
        "clinical_item_id\tname\tdescription\tclinical_item_category_id\n\
        -100\tTestItem100\tTest Item 100\t-100\n\
        -200\tTestItem200\tTest Item 200\t-100\n",
    "patient_item" :
        "patient_item_id\tpatient_id\tclinical_item_id\titem_date\n\
        -1000\t-123\t-100\t10/6/2113 10:20\n\
        -2000\t-123\t-200\t10/6/2113 11:20\n\
        -2500\t-123\t-100\t10/7/2113 11:20\n\
        -3000\t-456\t-100\t11/6/2113 10:20\n\
        -6000\t-789\t-200\t12/6/2113 11:20\n",
    "stride_order_proc" :
        "order_proc_id\tpat_id\torder_time\tproc_code\n\
        -100\t-123\t4/6/2009 6:00\tTNI\n\
        -200\t-123\t4/6/2009 16:00\tTNI\n\
        -300\t-123\t4/6/2009 15:00\tLABMETB\n\
        -400\t-456\t4/25/2009 6:00\tLABMETB\n\
        -500\t-456\t4/6/2009 16:00\tTNI\n\
        -600\t-456\t5/6/2009 15:00\tLABMETB\n\
        -700\t-789\t4/25/2009 6:00\tLABMETB\n\
        -750\t-789\t4/26/2009 6:00\tLABMETB\n\
        -800\t-789\t4/6/2009 16:00\tLABMETB\n\
        -900\t-789\t5/6/2009 15:00\tLABMETB\n",
    "stride_order_results" :
        "order_proc_id\tline\tresult_time\tbase_name\tord_num_value\t\
        result_flag\tresult_in_range_yn\n\
        -100\t1\t4/6/2009 6:36\tTNI\t0.2\tHigh Panic\tN\n\
        -200\t1\t4/6/2009 16:34\tTNI\t0\tNone\tY\n\
        -300\t2\t4/6/2009 15:12\tCR\t2.1\tHigh\tN\n\
        -400\t1\t4/25/2009 6:36\tNA\t145\tNone\tY\n\
        -500\t1\t4/6/2009 16:34\tTNI\t9999999\tNone\tNone\n\
        -600\t2\t5/6/2009 15:12\tCR\t0.5\tNone\tY\n\
        -700\t2\t4/25/2009 12:00\tCR\t0.3\tNone\tY\n\
        -750\t2\t4/26/2009 6:00\tCR\t0.7\tNone\tY\n\
        -800\t1\t4/6/2009 16:34\tNA\t123\tLow\tN\n\
        -800\t2\t4/6/2009 12:00\tCR\t1.0\tNone\tNone\n\
        -900\t1\t5/6/2009 15:12\tNA\t151\tHigh\tN\n",
    "stride_flowsheet" :
        "pat_anon_id\tflo_meas_id\tflowsheet_name\tflowsheet_value\t\
        shifted_record_dt_tm\n\
        -123\t-1\tFiO2\t0.2\t4/6/2009 6:36\n\
        -123\t-1\tFiO2\t0\t4/6/2009 16:34\n\
        -123\t-2\tGlasgow Coma Scale Score\t2.1\t4/6/2009 15:12\n\
        -456\t-3\tBP_High_Systolic\t145\t4/25/2009 6:36\n\
        -456\t-1\tFiO2\tNone\t4/6/2009 16:34\n\
        -456\t-2\tGlasgow Coma Scale Score\t0.5\t5/6/2009 15:12\n\
        -789\t-2\tGlasgow Coma Scale Score\t0.3\t4/25/2009 12:00\n\
        -789\t-2\tGlasgow Coma Scale Score\t0.7\t4/26/2009 6:00\n\
        -789\t-3\tBP_High_Systolic\t123\t4/6/2009 16:34\n\
        -789\t-2\tGlasgow Coma Scale Score\t1\t4/6/2009 12:00\n\
        -789\t-3\tBP_High_Systolic\t151\t5/6/2009 15:12\n",
    "stride_order_med" :
        "order_med_id\tpat_id\tmedication_id\tdescription\t\
            start_taking_time\tend_taking_time\tfreq_name\t\
            min_discrete_dose\tmin_rate\n\
        -123000\t-123\t16426\tNS WITH POTASSIUM CHLORIDE 20 MEQ/L IV SOLP\t\
            4/6/2009 12:30\t4/6/2009 15:00\tCONTINUOUS\t\t500\n\
        -123010\t-123\t540102\tNS IV BOLUS\t4/6/2009 12:30\t\
            4/6/2009 12:30\tONCE\t250\t\n\
        -123020\t-123\t16426\tNS WITH POTASSIUM CHLORIDE 20 MEQ/L IV SOLP \
            (missing end date, means cancelled. Ignore)\t4/6/2009 13:00\t\t\
            CONTINUOUS\t\t50\n\
        -123030\t-123\t27838\tSODIUM CHLORIDE 0.9 % 0.9 % IV SOLP (ignore \
            PACU)\t4/6/2009 10:00\t4/7/2009 10:00\tPACU ONLY\t\t125\n\
        -123040\t-123\t4318\tLACTATED RINGERS IV SOLP (ignore PRN)\t\
            4/6/2009 10:00\t4/7/2009 10:00\tPRN\t\t250\n\
        -123050\t-123\t16426\tNS WITH POTASSIUM CHLORIDE 20 MEQ/L IV SOLP \
            (ignore endoscopy PRN)\t4/6/2009 13:00\t4/7/2009 10:00\t\
            ENDOSCOPY PRN\t\t75\n\
        -123060\t-123\t540115\tLACTATED RINGERS IV BOLUS\t4/6/2009 14:00\t\
            4/6/2009 14:00\tONCE\t500\t\n\
        -123070\t-123\t540102\tNS IV BOLUS (register first daily admin, \
            though may expand to capture multiple)\t4/6/2009 16:00\t\
            4/10/2009 16:00\tDAILY\t250\t\n\
        -123080\t-123\t14863\tD5-1/2 NS & POTASSIUM CHLORIDE 20 MEQ/L IV \
            SOLP (should ignore hypotonic IVF for now)\t4/6/2009 14:00\t\
            4/7/2009 14:00\tCONTINUOUS\t\t75\n\
        -123090\t-123\t8982\tALBUMIN, HUMAN 5 % 5 % IV SOLP (should ignore \
            albumin for now)\t4/6/2009 14:00\t4/7/2009 14:00\tONCE\t500\t\n\
        -123100\t-123\t27838\tSODIUM CHLORIDE 0.9 % 0.9 % IV SOLP\t\
            4/6/2009 16:30\t4/6/2009 18:00\tCONTINUOUS\t\t500\n\
        -123110\t-123\t4318\tLACTATED RINGERS IV SOLP\t4/6/2009 17:00\t\
            4/6/2009 18:00\tCONTINUOUS\t\t1000\n"
}

# Dictionary mapping from test function to expected output.
FM_TEST_OUTPUT = {
    "test_processPatientEpisodeInput" : [
        { "pat_id": -789, "proc_code": "LABMETB", "normal_results": "0",
            "order_proc_id": "-900",
            "order_time": DBUtil.parseDateValue("5/6/2009 15:00") },
        { "pat_id": -789, "proc_code": "LABMETB", "normal_results": "0",
            "order_proc_id": "-800",
            "order_time": DBUtil.parseDateValue("4/6/2009 16:00") },
        { "pat_id": -789, "proc_code": "LABMETB", "normal_results": "1",
            "order_proc_id": "-750",
            "order_time": DBUtil.parseDateValue("4/26/2009 6:00") },
        { "pat_id": -789, "proc_code": "LABMETB", "normal_results": "1",
            "order_proc_id": "-700",
            "order_time": DBUtil.parseDateValue("4/25/2009 6:00") },
        { "pat_id": -456, "proc_code": "LABMETB", "normal_results": "1",
            "order_proc_id": "-600",
            "order_time": DBUtil.parseDateValue("5/6/2009 15:00") },
        { "pat_id": -456, "proc_code": "LABMETB", "normal_results": "1",
            "order_proc_id": "-400",
            "order_time": DBUtil.parseDateValue("4/25/2009 6:00") },
        { "pat_id": -123, "proc_code": "LABMETB", "normal_results": "0",
            "order_proc_id": "-300",
            "order_time": DBUtil.parseDateValue("4/6/2009 15:00") }
    ],
    "test_buildFeatureMatrix_multiClinicalItem" : [
        [
            "pat_id", "order_proc_id", "proc_code", "order_time", "normal_results",
            "TestItem100.preTimeDays", "TestItem100.pre",
            "TestItem100.pre.1d", "TestItem100.pre.2d", "TestItem100.pre.4d",
            "TestItem100.pre.7d", "TestItem100.pre.14d", "TestItem100.pre.30d",
            "TestItem100.pre.90d", "TestItem100.pre.180d", "TestItem100.pre.365d",
            "TestItem100.pre.730d", "TestItem100.pre.1460d",
            "TestItem100.postTimeDays", "TestItem100.post",
            "TestItem100.post.1d", "TestItem100.post.2d", "TestItem100.post.4d",
            "TestItem100.post.7d", "TestItem100.post.14d", "TestItem100.post.30d",
            "TestItem100.post.90d",	"TestItem100.post.180d", "TestItem100.post.365d",
            "TestItem100.post.730d", "TestItem100.post.1460d",
            "TestItem200.preTimeDays", "TestItem200.pre",
            "TestItem200.pre.1d", "TestItem200.pre.2d",	"TestItem200.pre.4d",
            "TestItem200.pre.7d", "TestItem200.pre.14d", "TestItem200.pre.30d",
            "TestItem200.pre.90d", "TestItem200.pre.180d", "TestItem200.pre.365d",
            "TestItem200.pre.730d", "TestItem200.pre.1460d",
            "TestItem200.postTimeDays",	"TestItem200.post",
            "TestItem200.post.1d", "TestItem200.post.2d", "TestItem200.post.4d",
            "TestItem200.post.7d", "TestItem200.post.14d", "TestItem200.post.30d",
            "TestItem200.post.90d", "TestItem200.post.180d", "TestItem200.post.365d",
            "TestItem200.post.730d", "TestItem200.post.1460d"
        ],
        [
            "-789", "-900", "LABMETB", "2009-05-06 15:00:00", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "38198.8472222", "1",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0"
        ],
        [
            "-789", "-800", "LABMETB", "2009-04-06 16:00:00", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "38228.8055556", "1",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0"
        ],
        [
            "-789", "-750", "LABMETB", "2009-04-26 06:00:00", "1",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "38209.2222222", "1",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0"
        ],
        [
            "-789", "-700", "LABMETB", "2009-04-25 06:00:00", "1",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "38210.2222222", "1",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0"
        ],
        [
            "-456", "-600", "LABMETB", "2009-05-06 15:00:00", "1",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "38168.8055556", "1",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0"
        ],
        [
            "-456", "-400", "LABMETB", "2009-04-25 06:00:00", "1",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "38180.1805556", "1",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0"
        ],
        [
            "-123", "-300", "LABMETB", "2009-04-06 15:00:00", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "38167.8055556", "2",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "None", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0",
            "38167.8472222", "1",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0", "0",
            "0", "0"
        ]
    ],
    "test_buildFeatureMatrix_multiLabTest" : {
        "expectedLabResults" : [
            {
                "pat_id": -789,
                "base_name": "CR",
                "ord_num_value": 1.0,
                "result_flag": None,
                "result_in_range_yn": None,
                "result_time": DBUtil.parseDateValue("4/6/2009 12:00")
            },
            {
                "pat_id": -789,
                "base_name": "CR",
                "ord_num_value": 0.7,
                "result_flag": None,
                "result_in_range_yn": "Y",
                "result_time": DBUtil.parseDateValue("4/26/2009 6:00")
            },
            {
                "pat_id": -789,
                "base_name": "CR",
                "ord_num_value": 0.3,
                "result_flag": None,
                "result_in_range_yn": "Y",
                "result_time": DBUtil.parseDateValue("4/25/2009 12:00")
            },
            {
                "pat_id": -456,
                "base_name":"TNI",
                "ord_num_value": 9999999,
                "result_flag": None,
                "result_in_range_yn": None,
                "result_time": DBUtil.parseDateValue("4/6/2009 16:34")
            },
            {
                "pat_id": -456,
                "base_name":"CR",
                "ord_num_value": 0.5,
                "result_flag": None,
                "result_in_range_yn":"Y",
                "result_time": DBUtil.parseDateValue("5/6/2009 15:12")
            },
            {
                "pat_id": -123,
                "base_name":"TNI",
                "ord_num_value": 0.2,
                "result_flag": "High Panic",
                "result_in_range_yn": "N",
                "result_time": DBUtil.parseDateValue("4/6/2009 6:36")
            },
            {
                "pat_id": -123,
                "base_name":"CR",
                "ord_num_value": 2.1,
                "result_flag": "High",
                "result_in_range_yn":"N",
                "result_time": DBUtil.parseDateValue("4/6/2009 15:12")
            },
            {
                "pat_id": -123,
                "base_name":"TNI",
                "ord_num_value": 0,
                "result_flag": None,
                "result_in_range_yn": "Y",
                "result_time": DBUtil.parseDateValue("4/6/2009 16:34")
            }
        ],
        "expectedMatrix" : [
            [
                "pat_id", "order_proc_id", "proc_code", "order_time",
                "normal_results",
                "TNI.-90_0.count", "TNI.-90_0.countInRange",
                "TNI.-90_0.min", "TNI.-90_0.max", "TNI.-90_0.median",
                "TNI.-90_0.mean", "TNI.-90_0.std",
                "TNI.-90_0.first", "TNI.-90_0.last", "TNI.-90_0.diff",
                "TNI.-90_0.slope", "TNI.-90_0.proximate",
                "TNI.-90_0.firstTimeDays", "TNI.-90_0.lastTimeDays",
                "TNI.-90_0.proximateTimeDays",
                "CR.-90_0.count", "CR.-90_0.countInRange",
                "CR.-90_0.min", "CR.-90_0.max",	"CR.-90_0.median",
                "CR.-90_0.mean", "CR.-90_0.std",
                "CR.-90_0.first", "CR.-90_0.last", "CR.-90_0.diff",
                "CR.-90_0.slope", "CR.-90_0.proximate",
                "CR.-90_0.firstTimeDays", "CR.-90_0.lastTimeDays",
                "CR.-90_0.proximateTimeDays",
                "LAC.-90_0.count", "LAC.-90_0.countInRange",
                "LAC.-90_0.min", "LAC.-90_0.max", "LAC.-90_0.median",
                "LAC.-90_0.mean", "LAC.-90_0.std",
                "LAC.-90_0.first", "LAC.-90_0.last", "LAC.-90_0.diff",
                "LAC.-90_0.slope", "LAC.-90_0.proximate",
                "LAC.-90_0.firstTimeDays", "LAC.-90_0.lastTimeDays",
                "LAC.-90_0.proximateTimeDays"
            ],
            [
                "-789", "-900", "LABMETB", "2009-05-06 15:00:00",
                "0",
                "0", "0", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "None", "None", "None", "None",
                "None",
                "3", "2", "0.3", "1.0", "0.7",
                "0.666666666667", "0.286744175568", "1.0", "0.7", "-0.3",
                "-0.0151898734177", "0.7", "-30.125", "-10.375", "-10.375",
                "0", "0", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "None", "None",	"None", "None", "None"
            ],
            [
                "-789", "-800", "LABMETB", "2009-04-06 16:00:00",
                "0",
                "0", "0", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "1", "0", "1.0", "1.0", "1.0",
                "1.0", "0.0", "1.0", "1.0", "0.0",
                "0.0", "1.0", "-0.166666666667", "-0.166666666667",	"-0.166666666667",
                "0", "0", "None", "None", "None",
                "None", "None", "None",	"None",	"None",
                "None",	"None",	"None",	"None",	"None"
            ],
            [
                "-789",	"-750",	"LABMETB",	"2009-04-26 06:00:00",
                "1",
                "0", "0", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "None", "None", "None", "None",	"None",
                "2", "1", "0.3", "1.0", "0.65",
                "0.65", "0.35",	"1.0", "0.3", "-0.7",
                "-0.0368421052632", "0.3", "-19.75", "-0.75", "-0.75",
                "0", "0", "None", "None", "None",
                "None", "None",	"None",	"None",	"None",
                "None", "None", "None", "None", "None"
            ],
            [
                "-789", "-700", "LABMETB", "2009-04-25 06:00:00",
                "1",
                "0", "0", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "1", "0", "1.0", "1.0", "1.0",
                "1.0", "0.0", "1.0", "1.0", "0.0",
                "0.0", "1.0", "-18.75", "-18.75", "-18.75",
                "0", "0", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None"
            ],
            [
                "-456", "-600", "LABMETB", "2009-05-06 15:00:00",
                "1",
                "0", "0", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "0", "0", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "0", "0", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None"
            ],
            [
                "-456", "-400", "LABMETB", "2009-04-25 06:00:00",
                "1",
                "0", "0", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "0", "0", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "0", "0", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None"
            ],
            [
                "-123", "-300", "LABMETB", "2009-04-06 15:00:00",
                "0",
                "1", "0", "0.2", "0.2", "0.2",
                "0.2", "0.0", "0.2", "0.2", "0.0",
                "0.0", "0.2", "-0.35", "-0.35", "-0.35",
                "0", "0", "None", "None", "None",
                "None", "None", "None",	"None",	"None",
                "None", "None", "None", "None", "None",
                "0",  "0", "None", "None", "None",
                "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None"
            ]
        ]
    }
}
