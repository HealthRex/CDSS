#!/usr/bin/python
"""
Test data for TestFeatureMatrixIO.
"""

import datetime
import pandas as pd

MANUAL_TEST_CASE = {
    'custom_header': [
        'test-matrix-with-header.tab',
        '',
        'This matrix file is for testing only.',
        "Doesn't contain anything of value."
    ],
    'default_header': [
        'header-temp-file.tab',
        'Created: %s' % datetime.datetime.today().date()
    ],
    'matrix_no_header': pd.DataFrame({
        'patient_id': [1, 2, 3, 4, 5],
        'index_time': [
            pd.Timestamp('2018-01-01 12:00:00'),
            pd.Timestamp('2018-01-01 12:00:00'),
            pd.Timestamp('2018-01-01 12:00:00'),
            pd.Timestamp('2018-01-01 12:00:00'),
            pd.Timestamp('2018-01-01 12:00:00'),
        ],
        'label': [True, False, True, False, True],
        'f1': [1.0, 2.0, 3.0, 4.0, 5.0],
        'f2': [1, 0, 1, 1, 0],
        'f3': [False, True, False, True, False],
        'f4': ["Foo", "Bar", "Baz", "Foo", "Bar"]
    },
    # Specify ordering of columns because pandas alphabetizes by default.
    columns=['patient_id', 'index_time', 'label', 'f1', 'f2', 'f3', 'f4'])
}
