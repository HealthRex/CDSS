from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import os
import pandas as pd

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/grolleau/Desktop/github repos/Cost variability/json_credentials/grolleau_application_default_credentials.json'
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101'

# Instantiate a client object so you can make queries
client = bigquery.Client()

# Create a connexion to that client
conn = dbapi.connect(client)

my_drg = 2592

query = f"""
WITH 
one_drg AS
(SELECT *
FROM `som-nero-phi-jonc101-secure.proj_IP_variation.matched_drg_cost_adms`
WHERE drg_id = '{my_drg}'),

one_drg_first_hospi AS
(SELECT anon_id, MIN(adm_date_jittered) AS date_first_hosp
FROM one_drg
GROUP BY anon_id)

SELECT cost.*
FROM one_drg_first_hospi LEFT JOIN one_drg AS cost
ON one_drg_first_hospi.anon_id = cost.anon_id AND one_drg_first_hospi.date_first_hosp = cost.adm_date_jittered
"""

df = pd.read_sql_query(query, conn)