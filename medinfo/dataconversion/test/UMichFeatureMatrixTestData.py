#!/usr/bin/env python
"""
Test input and output for FeatureMatrixFactory.
"""

from medinfo.db import DBUtil

# Dictionary mapping from database table name to test data.
FM_TEST_INPUT_TABLES = {
    "labs_columns" : ['pat_id','order_proc_id','order_time','result_time','proc_code','base_name','ord_num_value'],
    "labs_column_types" : ['INTEGER', 'INTEGER', 'TIMESTAMP', 'TIMESTAMP', 'TEXT', 'TEXT', 'TEXT'],
    'labs_data':[
        [1, 1, '2050-01-05 09:44:00', '2050-01-05 09:44:00', 'CBCP', 'WBC', 6],
        [1, 2, '2050-01-07 12:44:00', '2050-01-07 12:44:00', 'CBCP', 'WBC', 5],
        [1, 3, '2050-01-09 23:44:00', '2050-01-09 23:44:00', 'CBCP', 'WBC', 3],

        [1, 4, '2050-01-04 09:44:00', '2050-01-05 09:44:00', 'COMP', 'CO2', 6],
        [1, 5, '2050-01-07 13:44:00', '2050-01-07 12:44:00', 'COMP', 'CO2', 5],

        [1, 6, '2050-01-08 23:44:00', '2050-01-09 23:44:00', 'CBCP', 'HCT', 3],
    ],

    'pt_info_columns' : ['pat_id','Birth'],
    "pt_info_column_types" : ['INTEGER','TIMESTAMP'],
    "pt_info_data" : [
        [1, '1986-04-23 00:00:00']
    ],

    'encounters_columns' : ['pat_id','order_proc_id','AdmitDxDate'],
    "encounters_column_types" : ['INTEGER','INTEGER','TIMESTAMP'],
    "encounters_data" : [
        [1, 1, '2050-01-05 08:00:00'],
        [1, 2, '2050-01-07 10:44:00'],
        [1, 3, '2050-01-09 13:44:00']
    ],

    'diagnoses_columns' : ['pat_id', 'order_proc_id', 'diagnose_time', 'diagnose_code'],
    "diagnoses_column_types" : ['INTEGER','INTEGER','TIMESTAMP','TEXT'],
    "diagnoses_data" : [
        [1, 114, '2050-01-05 09:00:00'],
        [1, 115, '2050-01-07 11:44:00'],
        [1, 116, '2050-01-09 15:44:00']
    ],

    'demographics_columns' : ['pat_id','GenderName', 'RaceName'],
    'demographics_column_types': ['INTEGER','TEXT','TEXT'],
    'demographics_data' : [
        [1, 'Male', 'Caucasian'],
        [2, 'Female', 'Native Hawaiian and Other Pacific Islander'],
        [3, 'Male', 'Hispanic']
    ]
}

# Dictionary mapping from test function to expected output.
FM_TEST_OUTPUT = {
    "OUTPUT_RAW_TABLE":[[
        'pat_id', 'order_time',
         'HCT.preTimeDays', 'HCT.pre', 'HCT.pre.1d', 'HCT.pre.2d', 'HCT.pre.4d', 'HCT.pre.7d', 'HCT.pre.14d', 'HCT.pre.30d', 'HCT.pre.90d', 'HCT.pre.180d', 'HCT.pre.365d', 'HCT.pre.730d', 'HCT.pre.1460d',
         'HCT.postTimeDays', 'HCT.post', 'HCT.post.1d', 'HCT.post.2d', 'HCT.post.4d', 'HCT.post.7d', 'HCT.post.14d', 'HCT.post.30d', 'HCT.post.90d', 'HCT.post.180d', 'HCT.post.365d', 'HCT.post.730d', 'HCT.post.1460d',
         'Male.preTimeDays', 'Male.pre', 'Male.pre.1d', 'Male.pre.2d', 'Male.pre.4d', 'Male.pre.7d', 'Male.pre.14d', 'Male.pre.30d', 'Male.pre.90d', 'Male.pre.180d', 'Male.pre.365d', 'Male.pre.730d', 'Male.pre.1460d',
         'Male.postTimeDays', 'Male.post', 'Male.post.1d', 'Male.post.2d', 'Male.post.4d', 'Male.post.7d', 'Male.post.14d', 'Male.post.30d', 'Male.post.90d', 'Male.post.180d', 'Male.post.365d', 'Male.post.730d', 'Male.post.1460d'
    ],
    ['1', '2050-01-05 09:44:00',
     'None', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
     '3.58333333333', '1', '0', '0', '1', '1', '1', '1', '1', '1', '1', '1', '1',
     '-54791.4055556', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
     'None', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['1', '2050-01-07 12:44:00',
     'None', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
     '1.45833333333', '1', '0', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1',
     '-54793.5305556', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
     'None', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['1', '2050-01-09 23:44:00',
     '-1.0', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1',
     'None', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
     '-54795.9888889', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
     'None', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['1', '2050-01-04 09:44:00',
     'None', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
     '4.58333333333', '1', '0', '0', '0', '1', '1', '1', '1', '1', '1', '1', '1',
     '-54790.4055556', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
     'None', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['1', '2050-01-07 13:44:00',
     'None', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
     '1.41666666667', '1', '0', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1',
     '-54793.5722222', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
     'None', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
    ['1', '2050-01-08 23:44:00',
     'None', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0.0',
     '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1',
     '-54794.9888889', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
     'None', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
    ]
}
