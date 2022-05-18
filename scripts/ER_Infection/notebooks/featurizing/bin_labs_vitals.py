import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os 
from google.cloud import bigquery

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/ccorbin/.config/gcloud/application_default_credentials.json' 
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101' 

client=bigquery.Client()


def convert_to_dict(look_up_table):
    """Converts df look up table to dictionary for faster look up later"""
    bin_val_dict = {}
    for feature in look_up_table['features'].unique():
        feature_bin_vals = look_up_table[look_up_table['features'] == feature]
        for _bin in feature_bin_vals['bins'].unique():
            if feature not in bin_val_dict:
                bin_val_dict[feature] = {}
                bin_val_dict[feature]['min'] = []
                bin_val_dict[feature]['max'] = []

            min_val_for_bin = feature_bin_vals[feature_bin_vals['bins'] == _bin]['value']['min'].values[0]
            max_val_for_bin = feature_bin_vals[feature_bin_vals['bins'] == _bin]['value']['max'].values[0]

            bin_val_dict[feature]['min'].append(min_val_for_bin)
            bin_val_dict[feature]['max'].append(max_val_for_bin)
    return bin_val_dict

    
def train_featurizer(df_train):
    """
    Compute percent_ranks and generates a look up table of min and max bin values
    Input : long form dataframe with features and value where value are the continuous values of labs / vitals
    Output: look up table - dict of dict of lists (key1 = feature_name, key2 = max or min, values = lists of values)
    """
    # Compute percentiles and bins
    df_train['percentiles'] = df_train.groupby('features')['value'].transform(lambda x: x.rank(pct=True))
    df_train['bins'] = df_train['percentiles'].apply(lambda x: int(x * 10))
    
    # Generate look up table and conver to dictionary stucture
    look_up_table_df = df_train.groupby(['features', 'bins']).agg({'value' : ['min', 'max']}).reset_index()
    look_up_table = convert_to_dict(look_up_table_df)
    
    ### Sanity Check. Ensure that min vector for each feature is strictly increasing (no ties!)
    # Should be the case because ties are given same percentile rank in default pandas rank function
    for feature in look_up_table:
        mins = look_up_table[feature]['min']
        for i in range(len(mins)-1):
            assert mins[i] < mins[i+1]
    
    return look_up_table


def apply_featurizer(df, look_up_table):
    
    def get_appropriate_bin(feature, value, look_up_table):
        """Takes in feature, value and look up table and returns appropriate bin

        Quick Note: For some features, we do not have 10 bins.  This happens when we have many many ties in the 
        percent rank - and the percent rank alg returns ties as the average rank within that tie. So for instance
        we're trying to break each feature up into deciles where each bin covers range of 10% of the examples. But if more
        than 10% of the examples take on 1 value - then bins can be skipped. This shouldn't really be a problem
        for downstream tasks - just something to be aware of. This also means 'bins' and 'bins_applied' won't have
        perfect overlap in features that end up having less than 10 bins

        """
        mins = look_up_table[feature]['min']
        for i in range(len(mins) - 1):
            # If value is smaller than min value of smallest bin (in test time) - then return 0 (smallest bin)
            if i == 0 and value < mins[i]:
                return i

            if value >= mins[i] and value < mins[i+1] :
                return i

        # Then in last bin
        return len(mins)-1
    
    df['bins_applied'] = df[['features', 'value']].apply(
        lambda x: get_appropriate_bin(x['features'], x['value'], look_up_table), axis=1)
    
    return df

# Gets vitals and labs from feature timeline that we want to bin
query = """SELECT * FROM `mining-clinical-decisions.abx.feature_timeline_long`
           WHERE feature_type IN ('Lab Results', 'Flowsheet')
        """
query_job = client.query(query)
df = query_job.result().to_dataframe()

# Segment by validation split time
df_train = df[df['index_time'] < '2018-01-01']

# Train featurizer
look_up_table = train_featurizer(df_train)

# Apply featurizer
df_featurized = apply_featurizer(df, look_up_table)

# Sanity check in leui of test code for now
df_train = apply_featurizer(df_train, look_up_table)
look_up_table_df = df_train.groupby(['features', 'bins']).agg({'value' : ['min', 'max']}).reset_index()

features_with_0_9_bins = []
for feature in look_up_table_df:
    num_bins = len(look_up_table_df[look_up_table_df['features'] == feature]['bins'].values)
    ten_in_bins = 10 in look_up_table_df[look_up_table_df['features'] == feature]['bins'].values
    if num_bins == 10 and not ten_in_bins:
        features_with_0_9_bins.append(feature)

for feature in features_with_0_9_bins:
    df_test = df_train[df_train['features'] == 'feature']
    for b_real, b_computed in zip(df_test['bins'].values, df_test['bins_applied'].values):
        assert(b_real == b_computed)

# House Cleaning
columns = ['anon_id', 'pat_enc_csn_id_coded', 'index_time', 'observation_time' 'feature_type', 'features', 'value', 'bins_applied']
df_new = df_featurized[columns]

# New feature names
df_new['features'] = ['_'.join([x, str(y)]) for x, y in zip(df_new['features'].values, df_new['bins_applied'].values)] 
df_new['feature_type'] = [x + '_train' for x in df_new['feature_type'].values]

df_new.to_csv('lab_results_vitals_binned.csv', index=None)