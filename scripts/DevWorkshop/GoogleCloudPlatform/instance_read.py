# basic script to  read  data  from BigQuery from compute instance: 

from google.cloud import bigquery
client = bigquery.Client(project='mining-clinical-decisions')

project_id = 'mining-clinical-decisions'

sql = '''
      SELECT
        jc_uid, order_type,  description
      FROM
        `datalake_47618_sample.order_proc`
      Order By
         ordering_date_jittered DESC
    '''

# Run a Standard SQL query using the environment's default project
df = client.query(sql).to_dataframe()

df = client.query(sql, project=project_id).to_dataframe()
print(df)
