from google.cloud import bigquery;
from google.cloud.bigquery import dbapi;
import pandas as pd
import pdb
from dateutil.relativedelta import relativedelta

def compute_paients_demog(client_name, patient_id , query_demog):
    # pdb.set_trace()
    client = bigquery.Client(client_name); 
    conn = dbapi.connect(client);
    cursor = conn.cursor();

    print('Executing SQL query to extract demographic records ...')
    # cursor.execute(quenry_demog);
    demographic_data = pd.read_sql_query(query_demog, conn);

    metadata_columns=['anon_id', 'sex', 'bdate', 'canonical_race', 'canonical_ethnicity']
    metadata_list = []
    print('Extracting demographics and labeling the cohort ...')
    patient_counter= 0
    # pdb.set_trace()
    for idx, row in demographic_data.iterrows():

        patient_counter += 1
        if patient_counter % 10000 ==0:
            print('Finished processing {} patients'.format(patient_counter))

        sex = row['gender']
        bdate = row['birth_date_jittered']
        canonical_race = row['canonical_race']
        canonical_ethnicity = row['canonical_ethnicity']
        anon_id = row['anon_id']

        metadata_list.append([anon_id, sex, bdate, canonical_race, canonical_ethnicity])  

    metadata_pd = pd.DataFrame(metadata_list, columns=metadata_columns)
    metadata_pd.to_csv('intermediate_files/metadata.csv', index=False)
    
    