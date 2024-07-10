import os
os.chdir('/Users/grolleau/Desktop/github repos/CDSS/scripts/cost_variability_2024/scripts/pipeline/')
from drg_to_plot import drg_to_plot
from dat_to_conformal import drg_to_imp, drg_to_cqr
from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import pandas as pd

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/grolleau/Desktop/github repos/Cost variability/json_credentials/grolleau_application_default_credentials.json'
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101'

# Instantiate a client object so you can make queries
client = bigquery.Client()

# Create a connexion to that client
conn = dbapi.connect(client)

drg_query = """
SELECT drg_id FROM
(
SELECT drg_id, COUNT(*) as count
FROM `som-nero-phi-jonc101.francois_db.cost_drg`
GROUP BY drg_id
HAVING count > 400
)
"""

drg_list = pd.read_sql_query(drg_query, conn).iloc[:, 0].tolist()

for i, drg in enumerate(drg_list):
    print(f"DRG No. {i+1} of {len(drg_list)}")
    #drg_to_plot(drg)
    drg_to_cqr(drg)
