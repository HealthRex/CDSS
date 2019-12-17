from google.cloud import bigquery
import pandas as pd
import os

client = bigquery.Client()

def featurize_lab_orders(query):
    """ Given a SQL query that joins a cohort table with order_procs labs,
        execute the query and keep in long form """
    query_job = client.query(query)
    df_lab_features = query_job.result().to_dataframe()

    df_labs = df_lab_features[['pat_enc_csn_id_coded',
                               'proc_code',
                               'order_proc_id_coded']].drop_duplicates().groupby(
                               ['pat_enc_csn_id_coded', 'proc_code']).agg(
                               'count').reset_index().rename(columns={
                               'order_proc_id_coded' : 'values',
                               'proc_code' : 'features'})
    return df_labs


def featurize_med_orders(query):
    """ Given a SQL query that joins cohort table and order_med,
        execute query, make historical meds its own feature, and
        save in long form
    """
    query_job = client.query(query)
    df_med_features = query_job.result().to_dataframe()

    df_med_features['order_class'] = df_med_features['order_class'].apply(
        lambda x: 'Normal' if x != 'Historical Med' else 'Historical')
    df_med_features['med_description'] = df_med_features[['med_description', 'order_class']].apply(
        lambda x: '_'.join([x.med_description, x.order_class]), axis=1)

    df_meds = df_med_features[['pat_enc_csn_id_coded',
                               'med_description',
                               'order_med_id_coded']].drop_duplicates().groupby(
                               ['pat_enc_csn_id_coded', 'med_description']).agg(
                               'count').reset_index().rename(columns={
                               'order_med_id_coded' : 'values',
                               'med_description' : 'features'})
    return df_meds


def featurize_imaging_orders(query):
    """ 
    Query imaging orders and return in long format
    """
    query_job = client.query(query)
    df_imaging_features = query_job.result().to_dataframe()
    df_images = df_imaging_features[['pat_enc_csn_id_coded',
                                     'description',
                                     'order_proc_id_coded']].drop_duplicates().groupby(
                                     ['pat_enc_csn_id_coded', 'description']).agg(
                                     'count').reset_index().rename(columns={
                                     'order_proc_id_coded' : 'values',
                                     'description' : 'features'})

    return df_images


def featurize_microbiology_orders(query):
    """
    Query micorbiology orders and return in long format
    """

    query_job = client.query(query)
    df_micro_features = query_job.result().to_dataframe()
    df_micro = df_micro_features[['pat_enc_csn_id_coded',
                                  'description',
                                  'order_proc_id_coded']].drop_duplicates().groupby(
                                  ['pat_enc_csn_id_coded', 'description']).agg(
                                  'count').reset_index().rename(columns={
                                  'order_proc_id_coded' : 'values',
                                  'description' : 'features'})

    return df_micro

def featurize_procedure_orders(query):
    """
    Query procedure orders and return in long format
    """
    query_job = client.query(query)
    df_proc_features = query_job.result().to_dataframe()

    df_proc = df_proc_features[['pat_enc_csn_id_coded',
                                'description',
                                'order_proc_id_coded']].drop_duplicates().groupby(
                                ['pat_enc_csn_id_coded', 'description']).agg(
                                'count').reset_index().rename(columns={
                                'order_proc_id_coded' : 'values',
                                'description' : 'features'})

    return df_proc

def featurize_dx_codes(query):
    """
    Query dx codes and return in long format
    """
    query_job = client.query(query)
    df_dx_features = query_job.result().to_dataframe()
    df_dx = df_dx_features[['pat_enc_csn_id_coded',
                            'dx_name',
                            'dx_id']].drop_duplicates().groupby(
                            ['pat_enc_csn_id_coded', 'dx_name']).agg(
                            'count').reset_index().rename(columns={
                            'dx_id' : 'values',
                            'dx_name' : 'features'})

    return df_dx

def featurize_demographics(query):
    """
    Query demographics and get features for age, gender, race, and ethnicity
    """

    query_job = client.query(query)
    df_demo = query_job.result().to_dataframe()

    df_demo['order_time_jittered_utc'] = pd.to_datetime(df_demo['order_time_jittered_utc'])
    df_demo['birth_date_jittered'] = pd.to_datetime(df_demo['birth_date_jittered'])
    df_demo = df_demo.assign(
        age=lambda x: (x.order_time_jittered_utc.dt.date - x.birth_date_jittered.dt.date).dt.days)
    df_demo = df_demo[['pat_enc_csn_id_coded', 
                       'age', 'gender',
                       'canonical_race',
                       'canonical_ethnicity']]
    df_demo['canonical_ethnicity'] = df_demo['canonical_ethnicity'].apply(
        lambda x: 'Unknown Ethnicity' if x == 'Unknown' else x)
    df_demo['canonical_race'] = df_demo['canonical_race'].apply(
        lambda x: 'Unknown Race' if x == 'Unknown' else x)
    df_demo = pd.concat([df_demo,
                         pd.get_dummies(df_demo.gender),
                         pd.get_dummies(df_demo.canonical_race),
                         pd.get_dummies(df_demo.canonical_ethnicity)], axis=1)
    df_demo = df_demo.drop(['gender',
                            'canonical_race',
                            'Female',
                            'canonical_ethnicity'], axis=1).drop_duplicates()

    df_demo = pd.melt(df_demo, id_vars=['pat_enc_csn_id_coded'],
                      var_name = 'features',
                      value_name = 'values')

    return df_demo


def featurize_cohort(out_file = './data/feature_matrix.csv', dx_codes = True,
                     lab_orders = True, image_orders = True, med_orders = True,
                     procedure_orders = True, micro_orders = True, demos=True):
    """
    Featurize Cohort, return and save long form dataframe
    """

    data_frames = []
    sql_path = './SQL'
    if dx_codes:
        f = os.path.join(sql_path, 'DxFeatures.sql')
        with open(f, 'r') as file:
            query = file.read()
        data_frames.append(featurize_dx_codes(query))

    if lab_orders:
        f = os.path.join(sql_path, 'LabFeatures.sql')
        with open(f, 'r') as file:
            query = file.read()
        data_frames.append(featurize_lab_orders(query))

    if image_orders:
        f = os.path.join(sql_path, 'ImagingFeatures.sql')
        with open(f, 'r') as file:
            query = file.read()
        data_frames.append(featurize_imaging_orders(query))

    if procedure_orders:
        f = os.path.join(sql_path, 'ProcedureFeatures.sql')
        with open(f, 'r') as file:
            query = file.read()
        data_frames.append(featurize_procedure_orders(query))

    if micro_orders:
        f = os.path.join(sql_path, 'MicrobiologyOrderFeatures.sql')
        with open(f, 'r') as file:
            query = file.read()
        data_frames.append(featurize_microbiology_orders(query))

    if med_orders:
        f = os.path.join(sql_path, 'MedFeatures.sql')
        with open(f, 'r') as file:
            query = file.read()
        data_frames.append(featurize_med_orders(query))

    if demos:
        f = os.path.join(sql_path, 'DemographicFeatures.sql')
        with open(f, 'r') as file:
            query = file.read()
        data_frames.append(featurize_demographics(query))

    feature_matrix = pd.concat(data_frames)
    feature_matrix.to_csv(out_file, index=None)

    return feature_matrix

if __name__ == "__main__":
    df = featurize_cohort()


