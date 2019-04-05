
''''''

from medinfo.db.Model import SQLQuery
query = SQLQuery()
query.addSelect('p1.pat_enc_csn_id_coded as referral_enc_id')

import os
import pandas as pd

from google.cloud import bigquery

ENCOUNTER_TABLE = 'datalake_47618.encounter'
ORDERPROC_TABLE = 'datalake_47618.order_proc'
DIAGNOSIS_TABLE = 'datalake_47618.diagnosis_code'
DEPMAP_TABLE = 'datalake_47618.dep_map'

result_folderpath = 'queried_results'
if not os.path.exists(result_folderpath):
    os.mkdir(result_folderpath)

def setup_client(jsonkey_filepath):
    client = bigquery.Client.from_service_account_json(jsonkey_filepath)
    return client

def make_bigquery(query, client, project_id):
    df = client.query(query, project=project_id).to_dataframe()

    return df

def get_queried_data(query):
    query_id = hash(query)

    cached_filepath = os.path.join(result_folderpath, 'queried_%d.csv'%query_id)

    if os.path.exists(cached_filepath):
        return pd.read_csv(cached_filepath,
                           comment='#',
                           )
    else:
        client = setup_client('MiningClinicalDecisions_Song.json')
        project_id = 'mining-clinical-decisions'
        df = make_bigquery(query, client=client, project_id=project_id)

        f = open(cached_filepath, 'a')
        f.write('#' + query.__str__() + '\n')
        df.to_csv(f, index=False)
        f.close()

        return df

print get_queried_data(query)