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

cost_drg_query = """
SELECT *
FROM `som-nero-phi-jonc101.francois_db.cost_drg`
"""

df_cost_drg = pd.read_sql_query(cost_drg_query, conn)

all_drg_ids = df_cost_drg['drg_id'].unique() # len(all_drg_ids) = 1022 unique DRGs
all_drg_ids_str = ', '.join(list(map(lambda x: f"'{x}'", all_drg_ids)))
drg_ids_sql_list = f'({all_drg_ids_str})'


create_table_query = f"""
CREATE OR REPLACE TABLE `som-nero-phi-jonc101.francois_db.cost_pivot_drg` AS (
WITH pivoted as 
(
SELECT * FROM 
(SELECT observation_id, drg_id, adm_date_jittered disch_date_jittered, Cost_Direct_Scaled, Cost_Indirect_Scaled, Cost_Total_Scaled,
FROM `som-nero-phi-jonc101.francois_db.cost_drg`
)
PIVOT(SUM(1) FOR drg_id IN {drg_ids_sql_list})
)

SELECT * FROM pivoted
)
"""

# Execute the query
query_job = client.query(create_table_query) 

# Wait for the query to finish
query_job.result()
