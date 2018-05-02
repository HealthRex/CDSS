#!/usr/bin/python
"""
Test input and output for FeatureMatrixTransform.
"""

import pandas as pd

MANUAL_FM_TEST_CASE = {
    # Ensure input matrix has each of the following data types:
    #   * integer
    #   * float
    #   * True/False
    #   * string
    #   * timestamp
    'input': pd.DataFrame({
        'patient_id': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'index_time': [
            pd.Timestamp('2018-01-01 01:00:00'),
            pd.Timestamp('2018-01-02 02:00:00'),
            pd.Timestamp('2018-01-03 03:00:00'),
            pd.Timestamp('2018-01-04 04:00:00'),
            pd.Timestamp('2018-01-05 05:00:00'),
            pd.Timestamp('2018-01-06 06:00:00'),
            pd.Timestamp('2018-01-07 07:00:00'),
            pd.Timestamp('2018-01-08 08:00:00'),
            pd.Timestamp('2018-01-09 09:00:00')],
        'output': ['Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y'],
        'f1': [100, 200, 300, 400, 500, 600, 700, 800, 900],
        'f2': [1.0, 1.5, 2.0, None, 3.0, 3.5, None, 4.5, 5.0],
        'f3': [True, None, True, False, True, False, True, False, True],
        'f4': ['Foo', 'Bar', 'Baz', 'Foo', None, 'Baz', 'Foo', 'Bar', None]
    }),
    # test_remove_feature: Remove f2.
    "test_remove_feature": pd.DataFrame({
        'patient_id': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'index_time': [
            pd.Timestamp('2018-01-01 01:00:00'),
            pd.Timestamp('2018-01-02 02:00:00'),
            pd.Timestamp('2018-01-03 03:00:00'),
            pd.Timestamp('2018-01-04 04:00:00'),
            pd.Timestamp('2018-01-05 05:00:00'),
            pd.Timestamp('2018-01-06 06:00:00'),
            pd.Timestamp('2018-01-07 07:00:00'),
            pd.Timestamp('2018-01-08 08:00:00'),
            pd.Timestamp('2018-01-09 09:00:00')],
        'output': ['Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y'],
        'f1': [100, 200, 300, 400, 500, 600, 700, 800, 900],
        'f3': [True, None, True, False, True, False, True, False, True],
        'f4': ['Foo', 'Bar', 'Baz', 'Foo', None, 'Baz', 'Foo', 'Bar', None]
    }),
    # test_mean_data_imputation: Impute mean of f2.
    "test_mean_data_imputation": pd.DataFrame({
        'patient_id': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'index_time': [
            pd.Timestamp('2018-01-01 01:00:00'),
            pd.Timestamp('2018-01-02 02:00:00'),
            pd.Timestamp('2018-01-03 03:00:00'),
            pd.Timestamp('2018-01-04 04:00:00'),
            pd.Timestamp('2018-01-05 05:00:00'),
            pd.Timestamp('2018-01-06 06:00:00'),
            pd.Timestamp('2018-01-07 07:00:00'),
            pd.Timestamp('2018-01-08 08:00:00'),
            pd.Timestamp('2018-01-09 09:00:00')],
        'output': ['Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y'],
        'f1': [100, 200, 300, 400, 500, 600, 700, 800, 900],
        'f2': [1.0, 1.5, 2.0, 2.9285714286, 3.0, 3.5, 2.9285714286, 4.5, 5.0],
        'f3': [True, None, True, False, True, False, True, False, True],
        'f4': ['Foo', 'Bar', 'Baz', 'Foo', None, 'Baz', 'Foo', 'Bar', None]
    }),
    # test_mode_data_imputation: Impute mode of f4.
    "test_mode_data_imputation_single_feature": pd.DataFrame({
        'patient_id': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'index_time': [
            pd.Timestamp('2018-01-01 01:00:00'),
            pd.Timestamp('2018-01-02 02:00:00'),
            pd.Timestamp('2018-01-03 03:00:00'),
            pd.Timestamp('2018-01-04 04:00:00'),
            pd.Timestamp('2018-01-05 05:00:00'),
            pd.Timestamp('2018-01-06 06:00:00'),
            pd.Timestamp('2018-01-07 07:00:00'),
            pd.Timestamp('2018-01-08 08:00:00'),
            pd.Timestamp('2018-01-09 09:00:00')],
        'output': ['Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y'],
        'f1': [100, 200, 300, 400, 500, 600, 700, 800, 900],
        'f2': [1.0, 1.5, 2.0, None, 3.0, 3.5, None, 4.5, 5.0],
        'f3': [True, None, True, False, True, False, True, False, True],
        'f4': ['Foo', 'Bar', 'Baz', 'Foo', 'Foo', 'Baz', 'Foo', 'Bar', 'Foo']
    }),
    "test_mode_data_imputation_all_features": pd.DataFrame({
        'patient_id': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'index_time': [
            pd.Timestamp('2018-01-01 01:00:00'),
            pd.Timestamp('2018-01-02 02:00:00'),
            pd.Timestamp('2018-01-03 03:00:00'),
            pd.Timestamp('2018-01-04 04:00:00'),
            pd.Timestamp('2018-01-05 05:00:00'),
            pd.Timestamp('2018-01-06 06:00:00'),
            pd.Timestamp('2018-01-07 07:00:00'),
            pd.Timestamp('2018-01-08 08:00:00'),
            pd.Timestamp('2018-01-09 09:00:00')],
        'output': ['Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y'],
        'f1': [100, 200, 300, 400, 500, 600, 700, 800, 900],
        'f2': [1.0, 1.5, 2.0, 1.0, 3.0, 3.5, 1.0, 4.5, 5.0],
        'f3': [True, True, True, False, True, False, True, False, True],
        'f4': ['Foo', 'Bar', 'Baz', 'Foo', 'Foo', 'Baz', 'Foo', 'Bar', 'Foo']
    }),
    # test_add_logarithm_feature: Add log(f2).
    "test_add_logarithm_feature": pd.DataFrame({
        'patient_id': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'index_time': [
            pd.Timestamp('2018-01-01 01:00:00'),
            pd.Timestamp('2018-01-02 02:00:00'),
            pd.Timestamp('2018-01-03 03:00:00'),
            pd.Timestamp('2018-01-04 04:00:00'),
            pd.Timestamp('2018-01-05 05:00:00'),
            pd.Timestamp('2018-01-06 06:00:00'),
            pd.Timestamp('2018-01-07 07:00:00'),
            pd.Timestamp('2018-01-08 08:00:00'),
            pd.Timestamp('2018-01-09 09:00:00')],
        'output': ['Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y'],
        'f1': [100, 200, 300, 400, 500, 600, 700, 800, 900],
        'f2': [1.0, 1.5, 2.0, 2.9285714286, 3.0, 3.5, 2.9285714286, 4.5, 5.0],
        'ln(f2)': [0.0, 0.40546510810816438, 0.69314718055994529,
            1.0745147370988053, 1.0986122886681098, 1.2527629684953681,
            1.0745147370988053, 1.5040773967762742, 1.6094379124341003],
        'f3': [True, None, True, False, True, False, True, False, True],
        'f4': ['Foo', 'Bar', 'Baz', 'Foo', None, 'Baz', 'Foo', 'Bar', None]
    }),
    # test_add_indicator_feature: Add indicator(f2).
    "test_add_indicator_feature": pd.DataFrame({
        'patient_id': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'index_time': [
            pd.Timestamp('2018-01-01 01:00:00'),
            pd.Timestamp('2018-01-02 02:00:00'),
            pd.Timestamp('2018-01-03 03:00:00'),
            pd.Timestamp('2018-01-04 04:00:00'),
            pd.Timestamp('2018-01-05 05:00:00'),
            pd.Timestamp('2018-01-06 06:00:00'),
            pd.Timestamp('2018-01-07 07:00:00'),
            pd.Timestamp('2018-01-08 08:00:00'),
            pd.Timestamp('2018-01-09 09:00:00')],
        'output': ['Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y'],
        'f1': [100, 200, 300, 400, 500, 600, 700, 800, 900],
        'f2': [1.0, 1.5, 2.0, None, 3.0, 3.5, None, 4.5, 5.0],
        'I(f2)': [1, 1, 1, 0, 1, 1, 0, 1, 1],
        'f3': [True, None, True, False, True, False, True, False, True],
        'f4': ['Foo', 'Bar', 'Baz', 'Foo', None, 'Baz', 'Foo', 'Bar', None]
    }),
    # test_add_threshold_feature: Add threshold(f2, upper_bound=3.5)
    'test_add_threshold_feature': pd.DataFrame({
        'patient_id': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'index_time': [
            pd.Timestamp('2018-01-01 01:00:00'),
            pd.Timestamp('2018-01-02 02:00:00'),
            pd.Timestamp('2018-01-03 03:00:00'),
            pd.Timestamp('2018-01-04 04:00:00'),
            pd.Timestamp('2018-01-05 05:00:00'),
            pd.Timestamp('2018-01-06 06:00:00'),
            pd.Timestamp('2018-01-07 07:00:00'),
            pd.Timestamp('2018-01-08 08:00:00'),
            pd.Timestamp('2018-01-09 09:00:00')],
        'output': ['Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y'],
        'f1': [100, 200, 300, 400, 500, 600, 700, 800, 900],
        'f2': [1.0, 1.5, 2.0, None, 3.0, 3.5, None, 4.5, 5.0],
        'I(f2<=3.5)': [1, 1, 1, 0, 1, 1, 0, 0, 0],
        'f3': [True, None, True, False, True, False, True, False, True],
        'f4': ['Foo', 'Bar', 'Baz', 'Foo', None, 'Baz', 'Foo', 'Bar', None]
    }),
    # test_add_change_interval_feature: Add change(interval, 0.5, patient_id, f2)
    'test_add_change_interval_feature': pd.DataFrame({
        'patient_id': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'index_time': [
            pd.Timestamp('2018-01-01 01:00:00'),
            pd.Timestamp('2018-01-02 02:00:00'),
            pd.Timestamp('2018-01-03 03:00:00'),
            pd.Timestamp('2018-01-04 04:00:00'),
            pd.Timestamp('2018-01-05 05:00:00'),
            pd.Timestamp('2018-01-06 06:00:00'),
            pd.Timestamp('2018-01-07 07:00:00'),
            pd.Timestamp('2018-01-08 08:00:00'),
            pd.Timestamp('2018-01-09 09:00:00')],
        'output': ['Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y'],
        'f1': [100, 200, 300, 400, 500, 600, 700, 800, 900],
        'f2': [1.0, 1.5, 2.0, None, 3.0, 3.5, None, 4.5, 5.0],
        'change_yn': [0, 1, 1, 0, 1, 1, 0, 1, 1],
        'f3': [True, None, True, False, True, False, True, False, True],
        'f4': ['Foo', 'Bar', 'Baz', 'Foo', None, 'Baz', 'Foo', 'Bar', None]
    }),
    # test_add_change_percent_feature: Add change(percent, 0.35, patient_id, f2)
    'test_add_change_percent_feature': pd.DataFrame({
        'patient_id': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'index_time': [
            pd.Timestamp('2018-01-01 01:00:00'),
            pd.Timestamp('2018-01-02 02:00:00'),
            pd.Timestamp('2018-01-03 03:00:00'),
            pd.Timestamp('2018-01-04 04:00:00'),
            pd.Timestamp('2018-01-05 05:00:00'),
            pd.Timestamp('2018-01-06 06:00:00'),
            pd.Timestamp('2018-01-07 07:00:00'),
            pd.Timestamp('2018-01-08 08:00:00'),
            pd.Timestamp('2018-01-09 09:00:00')],
        'output': ['Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y'],
        'f1': [100, 200, 300, 400, 500, 600, 700, 800, 900],
        'f2': [1.0, 1.5, 2.0, None, 3.0, 3.5, None, 4.5, 5.0],
        'change_yn': [0, 0, 0, 0, 1, 0, 0, 1, 1],
        'f3': [True, None, True, False, True, False, True, False, True],
        'f4': ['Foo', 'Bar', 'Baz', 'Foo', None, 'Baz', 'Foo', 'Bar', None]
    }),
    # test_zero_data_imputation: Impute zero(f2).
    "test_zero_data_imputation": pd.DataFrame({
        'patient_id': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'index_time': [
            pd.Timestamp('2018-01-01 01:00:00'),
            pd.Timestamp('2018-01-02 02:00:00'),
            pd.Timestamp('2018-01-03 03:00:00'),
            pd.Timestamp('2018-01-04 04:00:00'),
            pd.Timestamp('2018-01-05 05:00:00'),
            pd.Timestamp('2018-01-06 06:00:00'),
            pd.Timestamp('2018-01-07 07:00:00'),
            pd.Timestamp('2018-01-08 08:00:00'),
            pd.Timestamp('2018-01-09 09:00:00')],
        'output': ['Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y'],
        'f1': [100, 200, 300, 400, 500, 600, 700, 800, 900],
        'f2': [1.0, 1.5, 2.0, 0.0, 3.0, 3.5, 0.0, 4.5, 5.0],
        'f3': [True, None, True, False, True, False, True, False, True],
        'f4': ['Foo', 'Bar', 'Baz', 'Foo', None, 'Baz', 'Foo', 'Bar', None]
    }),
    # test_median_data_imputation: Impute zero(f2).
    "test_median_data_imputation": pd.DataFrame({
        'patient_id': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'index_time': [
            pd.Timestamp('2018-01-01 01:00:00'),
            pd.Timestamp('2018-01-02 02:00:00'),
            pd.Timestamp('2018-01-03 03:00:00'),
            pd.Timestamp('2018-01-04 04:00:00'),
            pd.Timestamp('2018-01-05 05:00:00'),
            pd.Timestamp('2018-01-06 06:00:00'),
            pd.Timestamp('2018-01-07 07:00:00'),
            pd.Timestamp('2018-01-08 08:00:00'),
            pd.Timestamp('2018-01-09 09:00:00')],
        'output': ['Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y'],
        'f1': [100, 200, 300, 400, 500, 600, 700, 800, 900],
        'f2': [1.0, 1.5, 2.0, 3.0, 3.0, 3.5, 3.0, 4.5, 5.0],
        'f3': [True, None, True, False, True, False, True, False, True],
        'f4': ['Foo', 'Bar', 'Baz', 'Foo', None, 'Baz', 'Foo', 'Bar', None]
    }),
    'test_distribution_data_imputation': pd.DataFrame({
        'patient_id': [1, 2, 3, 1, 2, 3, 1, 2, 3],
        'index_time': [
            pd.Timestamp('2018-01-01 01:00:00'),
            pd.Timestamp('2018-01-02 02:00:00'),
            pd.Timestamp('2018-01-03 03:00:00'),
            pd.Timestamp('2018-01-04 04:00:00'),
            pd.Timestamp('2018-01-05 05:00:00'),
            pd.Timestamp('2018-01-06 06:00:00'),
            pd.Timestamp('2018-01-07 07:00:00'),
            pd.Timestamp('2018-01-08 08:00:00'),
            pd.Timestamp('2018-01-09 09:00:00')],
        'output': ['Y', 'Y', 'N', 'Y', 'N', 'Y', 'N', 'Y', 'Y'],
        'f1': [100, 200, 300, 400, 500, 600, 700, 800, 900],
        'f2': [1.0, 1.5, 2.0, 0.60648508830534575, 3.0, 3.5, 0.60648508830534575, 4.5, 5.0],
        'f3': [True, None, True, False, True, False, True, False, True],
        'f4': ['Foo', 'Bar', 'Baz', 'Foo', None, 'Baz', 'Foo', 'Bar', None]
    })
}
