'''
request .json api key
get project id
write sql
profit

Authentication for Big Query
https://cloud.google.com/docs/authentication/getting-started
https://cloud.google.com/bigquery/docs/authentication/
https://cloud.google.com/python/setup
'''

from google.cloud import bigquery

#client = bigquery.Client()
client = bigquery.Client.from_service_account_json('gcp_key.json')
sql = """
      SELECT
        jc_uid, order_type,  description
      FROM
        `datalake_47618_sample.order_proc`
      Order By
         ordering_date_jittered DESC
"""

# Run a Standard SQL query with the project set explicitly
project_id = 'mining-clinical-decisions'
df = client.query(sql, project=project_id).to_dataframe()
print(df)
