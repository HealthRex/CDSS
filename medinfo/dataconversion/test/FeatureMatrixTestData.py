#!/usr/bin/env python
"""
Test input and output for FeatureMatrixFactory.
"""

from medinfo.db import DBUtil

# Dictionary mapping from database table name to test data.
FM_TEST_INPUT_TABLES = {
    "clinical_item_category" :
        "clinical_item_category_id\tsource_table\tdescription\n\
        -100\tTestTable\tTestCategory\n\
        -200\tPerfTable\tPerfCategoryOne\n\
        -300\tPerfTable\tPerfCategoryTwo\n",
    "clinical_item" :
        "clinical_item_id\tname\tdescription\tclinical_item_category_id\n\
        -100\tTestItem100\tTest Item 100\t-100\n\
        -200\tTestItem200\tTest Item 200\t-100\n\
        -300\tPerfItem300\tPerf Item 300\t-200\n\
        -400\tPerfItem400\tPerf Item 400\t-200\n\
        -500\tPerfItem500\tPerf Item 500\t-300\n",
    "patient_item" :
        "patient_item_id\tpatient_id\tclinical_item_id\titem_date\n\
        -1000\t-123\t-100\t10/6/2113 10:20\n\
        -2000\t-123\t-200\t10/6/2113 11:20\n\
        -2500\t-123\t-100\t10/7/2113 11:20\n\
        -3000\t-456\t-100\t11/6/2113 10:20\n\
        -6000\t-789\t-200\t12/6/2113 11:20\n\
        -7000\t-1000\t-300\t10/6/2213 12:40\n\
        -8000\t-2000\t-400\t10/7/2213 12:40\n\
        -9000\t-3000\t-500\t10/8/2213 12:40\n\
        -10000\t-4000\t-300\t11/9/2213 12:40\n\
        -11000\t-5000\t-400\t11/10/2213 12:40\n\
        -12000\t-6000\t-500\t11/11/2213 12:40\n\
        -13000\t-7000\t-300\t12/12/2213 12:40\n\
        -14000\t-8000\t-400\t12/13/2213 12:40\n\
        -15000\t-9000\t-500\t12/14/2213 12:40\n\
        -16000\t-10000\t-300\t10/15/2213 12:40\n\
        -17000\t-1000\t-400\t10/16/2213 12:40\n\
        -18000\t-2000\t-500\t10/17/2213 12:40\n\
        -19000\t-3000\t-300\t11/18/2213 12:40\n\
        -20000\t-4000\t-400\t11/19/2213 12:40\n\
        -21000\t-5000\t-500\t11/20/2213 12:40\n\
        -22000\t-6000\t-300\t12/21/2213 12:40\n\
        -23000\t-7000\t-400\t12/22/2213 12:40\n\
        -24000\t-8000\t-500\t12/23/2213 12:40\n\
        -25000\t-9000\t-300\t10/24/2213 12:40\n\
        -26000\t-10000\t-400\t10/25/2213 12:40\n\
        -27000\t-1000\t-500\t10/26/2213 12:40\n\
        -28000\t-2000\t-300\t11/27/2213 12:40\n\
        -29000\t-3000\t-400\t11/28/2213 12:40\n\
        -30000\t-4000\t-500\t11/1/2213 12:40\n\
        -31000\t-5000\t-300\t12/2/2213 12:40\n\
        -32000\t-6000\t-400\t12/3/2213 12:40\n\
        -33000\t-7000\t-500\t12/4/2213 12:40\n\
        -34000\t-8000\t-300\t10/5/2213 12:40\n\
        -35000\t-9000\t-400\t10/6/2213 12:40\n\
        -36000\t-10000\t-500\t10/7/2213 12:40\n\
        -37000\t-1000\t-300\t11/8/2213 12:40\n\
        -38000\t-2000\t-400\t11/9/2213 12:40\n\
        -39000\t-3000\t-500\t11/10/2213 12:40\n\
        -40000\t-4000\t-300\t12/11/2213 12:40\n\
        -41000\t-5000\t-400\t12/12/2213 12:40\n\
        -42000\t-6000\t-500\t12/13/2213 12:40\n\
        -43000\t-7000\t-300\t10/14/2213 12:40\n\
        -44000\t-8000\t-400\t10/15/2213 12:40\n\
        -45000\t-9000\t-500\t10/16/2213 12:40\n\
        -46000\t-10000\t-300\t11/17/2213 12:40\n\
        -47000\t-1000\t-400\t11/18/2213 12:40\n\
        -48000\t-2000\t-500\t11/19/2213 12:40\n\
        -49000\t-3000\t-300\t12/20/2213 12:40\n\
        -50000\t-4000\t-400\t12/21/2213 12:40\n",
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
        -900\t-789\t5/6/2009 15:00\tLABMETB\n\
        -1000\t-1000\t10/1/2213 15:00\tFoo\n\
        -1100\t-2000\t11/2/2213 16:00\tFoo\n\
        -1200\t-3000\t12/3/2213 17:00\tFoo\n\
        -1300\t-4000\t10/4/2213 18:00\tBar\n\
        -1400\t-5000\t11/5/2213 19:00\tBar\n\
        -1500\t-6000\t12/6/2213 15:00\tBar\n\
        -1600\t-7000\t10/7/2213 15:00\tBaz\n\
        -1700\t-8000\t11/8/2213 16:00\tBaz\n\
        -1800\t-9000\t12/9/2213 17:00\tBaz\n\
        -1900\t-10000\t10/10/2213 18:00\tQux\n\
        -2000\t-1000\t11/11/2213 19:00\tQux\n\
        -2100\t-2000\t12/12/2213 15:00\tQux\n\
        -2200\t-3000\t10/13/2213 16:00\tFoo\n\
        -2300\t-4000\t11/14/2213 17:00\tFoo\n\
        -2400\t-5000\t12/15/2213 18:00\tFoo\n\
        -2500\t-6000\t10/16/2213 19:00\tBar\n\
        -2600\t-7000\t11/17/2213 15:00\tBar\n\
        -2700\t-8000\t12/18/2213 16:00\tBar\n\
        -2800\t-9000\t10/19/2213 17:00\tBaz\n\
        -2900\t-10000\t11/20/2213 18:00\tBaz\n\
        -3000\t-1000\t12/21/2213 19:00\tBaz\n\
        -3100\t-2000\t10/22/2213 15:00\tQux\n\
        -3200\t-3000\t11/23/2213 16:00\tQux\n\
        -3300\t-4000\t12/24/2213 17:00\tQux\n\
        -3400\t-5000\t10/25/2213 18:00\tFoo\n\
        -3500\t-6000\t11/26/2213 19:00\tFoo\n\
        -3600\t-7000\t12/27/2213 15:00\tFoo\n\
        -3700\t-8000\t10/28/2213 16:00\tBar\n\
        -3800\t-9000\t11/1/2213 17:00\tBar\n\
        -3900\t-10000\t12/2/2213 18:00\tBar\n\
        -4000\t-1000\t10/3/2213 19:00\tBaz\n",
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
        -900\t1\t5/6/2009 15:12\tNA\t151\tHigh\tN\n\
        -1000\t1\t10/3/2213 17:00\tFoo\t10\tMed\tN\n\
        -1100\t1\t11/4/2213 18:00\tFoo\t20\tMed\tN\n\
        -1200\t1\t12/5/2213 19:00\tFoo\t30\tHigh\tY\n\
        -1300\t1\t10/6/2213 15:00\tBar\t40\tMed\tN\n\
        -1400\t1\t11/7/2213 16:00\tBar\t50\tMed\tN\n\
        -1500\t1\t12/8/2213 17:00\tBar\t10\tLow\tY\n\
        -1600\t1\t10/9/2213 18:00\tBaz\t20\tMed\tN\n\
        -1700\t1\t11/10/2213 19:00\tBaz\t30\tMed\tN\n\
        -1800\t1\t12/11/2213 15:00\tBaz\t40\tHigh\tY\n\
        -1900\t1\t10/12/2213 16:00\tQux\t50\tMed\tN\n\
        -2000\t1\t11/13/2213 17:00\tQux\t10\tMed\tN\n\
        -2100\t1\t12/14/2213 18:00\tQux\t20\tLow\tY\n\
        -2200\t1\t10/15/2213 19:00\tFoo\t30\tMed\tN\n\
        -2300\t1\t11/16/2213 15:00\tFoo\t40\tMed\tN\n\
        -2400\t1\t12/17/2213 16:00\tFoo\t50\tHigh\tY\n\
        -2500\t1\t10/18/2213 17:00\tBar\t10\tMed\tN\n\
        -2600\t1\t11/19/2213 18:00\tBar\t20\tMed\tN\n\
        -2700\t1\t12/20/2213 19:00\tBar\t30\tLow\tY\n\
        -2800\t1\t10/21/2213 15:00\tBaz\t40\tMed\tN\n\
        -2900\t1\t11/22/2213 16:00\tBaz\t50\tMed\tN\n\
        -3000\t1\t12/23/2213 17:00\tBaz\t10\tHigh\tY\n\
        -3100\t1\t10/24/2213 18:00\tQux\t20\tMed\tN\n\
        -3200\t1\t11/25/2213 19:00\tQux\t30\tMed\tN\n\
        -3300\t1\t12/26/2213 15:00\tQux\t40\tLow\tY\n\
        -3400\t1\t10/27/2213 16:00\tFoo\t50\tMed\tN\n\
        -3500\t1\t11/28/2213 17:00\tFoo\t10\tMed\tN\n\
        -3600\t1\t12/1/2213 18:00\tFoo\t20\tLow\tY\n\
        -3700\t1\t10/2/2213 19:00\tBar\t30\tMed\tN\n\
        -3800\t1\t11/3/2213 15:00\tBar\t40\tMed\tN\n\
        -3900\t1\t12/4/2213 16:00\tBar\t50\tHigh\tY\n\
        -4000\t1\t10/5/2213 17:00\tBaz\t10\tMed\tN\n",
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
        -789\t-3\tBP_High_Systolic\t151\t5/6/2009 15:12\n\
        -1000\t-1\tPerflow\t151\t10/2/2213 15:12\n\
        -2000\t-2\tPerflow\t151\t10/3/2213 15:12\n\
        -3000\t-3\tPerflow\t151\t10/4/2213 15:12\n\
        -4000\t-1\tPerflow\t151\t10/5/2213 15:12\n\
        -5000\t-2\tPerflow\t151\t10/6/2213 15:12\n\
        -6000\t-3\tPerflow\t151\t10/7/2213 15:12\n\
        -7000\t-1\tPerflow\t151\t10/8/2213 15:12\n\
        -8000\t-2\tPerflow\t151\t10/9/2213 15:12\n\
        -9000\t-3\tPerflow\t151\t10/10/2213 15:12\n\
        -10000\t-1\tPerflow\t151\t10/11/2213 15:12\n\
        -1000\t-2\tPerflow\t151\t10/12/2213 15:12\n\
        -2000\t-3\tPerflow\t151\t10/13/2213 15:12\n\
        -3000\t-1\tPerflow\t151\t10/14/2213 15:12\n\
        -4000\t-2\tPerflow\t151\t10/15/2213 15:12\n\
        -5000\t-3\tPerflow\t151\t10/16/2213 15:12\n\
        -6000\t-1\tPerflow\t151\t10/17/2213 15:12\n\
        -7000\t-2\tPerflow\t151\t10/18/2213 15:12\n\
        -8000\t-3\tPerflow\t151\t10/19/2213 15:12\n\
        -9000\t-1\tPerflow\t151\t10/20/2213 15:12\n\
        -10000\t-2\tPerflow\t151\t10/21/2213 15:12\n",
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
    },
    "test_buildFeatureMatrix_multiFlowsheet" : {
        "expectedMatrix" : [
            [
                "pat_id", "order_proc_id", "proc_code", "order_time",
                "normal_results",
                "Resp.-90_0.count", "Resp.-90_0.countInRange",
                "Resp.-90_0.min", "Resp.-90_0.max", "Resp.-90_0.median",
                "Resp.-90_0.mean", "Resp.-90_0.std",
                "Resp.-90_0.first", "Resp.-90_0.last", "Resp.-90_0.diff",
                "Resp.-90_0.slope", "Resp.-90_0.proximate",
                "Resp.-90_0.firstTimeDays", "Resp.-90_0.lastTimeDays",
                "Resp.-90_0.proximateTimeDays",
                "FiO2.-90_0.count", "FiO2.-90_0.countInRange",
                "FiO2.-90_0.min", "FiO2.-90_0.max",	"FiO2.-90_0.median",
                "FiO2.-90_0.mean", "FiO2.-90_0.std",
                "FiO2.-90_0.first", "FiO2.-90_0.last", "FiO2.-90_0.diff",
                "FiO2.-90_0.slope", "FiO2.-90_0.proximate",
                "FiO2.-90_0.firstTimeDays", "FiO2.-90_0.lastTimeDays",
                "FiO2.-90_0.proximateTimeDays",
                "Glasgow Coma Scale Score.-90_0.count",
                "Glasgow Coma Scale Score.-90_0.countInRange",
                "Glasgow Coma Scale Score.-90_0.min",
                "Glasgow Coma Scale Score.-90_0.max",
                "Glasgow Coma Scale Score.-90_0.median",
                "Glasgow Coma Scale Score.-90_0.mean",
                "Glasgow Coma Scale Score.-90_0.std",
                "Glasgow Coma Scale Score.-90_0.first",
                "Glasgow Coma Scale Score.-90_0.last",
                "Glasgow Coma Scale Score.-90_0.diff",
                "Glasgow Coma Scale Score.-90_0.slope",
                "Glasgow Coma Scale Score.-90_0.proximate",
                "Glasgow Coma Scale Score.-90_0.firstTimeDays",
                "Glasgow Coma Scale Score.-90_0.lastTimeDays",
                "Glasgow Coma Scale Score.-90_0.proximateTimeDays"
            ],
            [
                "-789", "-900", "LABMETB", "2009-05-06 15:00:00",
                "0",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None",
                "3", "0", "0.3", "1.0", "0.7", "0.666666666667", "0.286744175568", "1.0",
                "0.7", "-0.3", "-0.0151898734177", "0.7", "-30.125", "-10.375", "-10.375"
            ],
            [
                "-789", "-800", "LABMETB", "2009-04-06 16:00:00",
                "0",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None",
                "1", "0", "1.0", "1.0", "1.0", "1.0", "0.0", "1.0", "1.0", "0.0",
                "0.0", "1.0", "-0.166666666667", "-0.166666666667", "-0.166666666667"
            ],
            [
                "-789", "-750", "LABMETB", "2009-04-26 06:00:00",
                "1",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None",
                "2", "0", "0.3", "1.0", "0.65", "0.65", "0.35", "1.0", "0.3",
                "-0.7", "-0.0368421052632", "0.3", "-19.75", "-0.75", "-0.75"
            ],
            [
                "-789", "-700", "LABMETB", "2009-04-25 06:00:00",
                "1", "0", "0", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None", "None",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None",
                "1", "0", "1.0", "1.0", "1.0", "1.0", "0.0", "1.0", "1.0", "0.0",
                "0.0", "1.0", "-18.75", "-18.75", "-18.75"
            ],
            [
                "-456", "-600", "LABMETB", "2009-05-06 15:00:00",
                "1",
                "0", "0", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None", "None",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None"
            ],
            [
                "-456", "-400", "LABMETB", "2009-04-25 06:00:00",
                "1",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None"
            ],
            [
                "-123", "-300", "LABMETB", "2009-04-06 15:00:00",
                "0",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None",
                "1", "0", "0.2", "0.2", "0.2", "0.2", "0.0", "0.2", "0.2", "0.0",
                "0.0", "0.2", "-0.35", "-0.35", "-0.35",
                "0", "0", "None", "None", "None", "None", "None", "None", "None",
                "None", "None", "None", "None", "None", "None"
            ]
        ]
    },
    "test_addTimeCycleFeatures" : {
        "expectedMatrix" : [
            [
                "pat_id", "order_proc_id", "proc_code", "order_time",
                "normal_results", "order_time.month", "order_time.month.sin",
                "order_time.month.cos", "order_time.hour",
                "order_time.hour.sin", "order_time.hour.cos"
            ],
            [   "-789", "-900", "LABMETB", "2009-05-06 15:00:00", "0",
                "5", "0.866025403784", "-0.5",
                "15", "-0.707106781187", "-0.707106781187" ],
            [   "-789", "-800", "LABMETB", "2009-04-06 16:00:00", "0",
                "4", "1.0", "6.12323399574e-17",
                "16", "-0.866025403784", "-0.5" ],
            [   "-789", "-750", "LABMETB", "2009-04-26 06:00:00", "1",
                "4", "1.0", "6.12323399574e-17",
                "6", "1.0", "6.12323399574e-17" ],
            [   "-789", "-700", "LABMETB", "2009-04-25 06:00:00", "1",
                "4", "1.0", "6.12323399574e-17",
                "6", "1.0", "6.12323399574e-17" ],
            [   "-456", "-600", "LABMETB", "2009-05-06 15:00:00", "1",
                "5", "0.866025403784", "-0.5",
                "15", "-0.707106781187", "-0.707106781187" ],
            [   "-456", "-400", "LABMETB", "2009-04-25 06:00:00", "1",
                "4", "1.0", "6.12323399574e-17",
                "6", "1.0", "6.12323399574e-17" ],
            [   "-123", "-300", "LABMETB", "2009-04-06 15:00:00", "0",
                "4", "1.0", "6.12323399574e-17",
                "15", "-0.707106781187", "-0.707106781187" ]
        ]
    }
}
