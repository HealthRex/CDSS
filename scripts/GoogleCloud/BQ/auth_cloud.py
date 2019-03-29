
'''
request .json api key
get project id
write sql
profit

Setting Up Virtual Environment

https://www.google.com/search?client=firefox-b-1-d&q=create+a+new+virtual+environment

#! [mac]        python -m virtualenv env_gcp
#! [windows]    py -m virtualenv env_gcp
#! [mac]        source env_gcp/bin/activate
#! [windows]    .\env_gcp\Scripts\activate

# [installing pip requirements]

#!              pip install -r  requirements.txt

Authentication for Big Query
https://cloud.google.com/docs/authentication/getting-started
https://cloud.google.com/bigquery/docs/authentication/
https://cloud.google.com/python/setup
'''

from google.cloud import bigquery

# PATH TO BOX SYNC: PLEASE CHANGE FOR LOCAL
print("DID YOU CHANGE YOUR PATH TO LOCAL BOX SYNC FOLDER ")
quiver_path = "/Users/jonc101/Box Sync/Jonathan Chiang's Files/quiver_test/"


# CONFIGURATION

client = bigquery.Client.from_service_account_json('gcp_key.json')
project_id = 'mining-clinical-decisions'
print("before sql")
sql = '''

select * from `datalake_47618_sample.encounter`
where appt_time_jittered > "2015-12-31" and appt_time_jittered < "2017-01-01"

    '''

print("sql saved")
"""
select patient_item_id, external_id, clinical_item_id, item_date, encounter_id, text_value, num_value, source_id from `clinical_inpatient.patient_item` where item_date >= timestamp('2014-01-01 00:00:00')
"""
# Run a Standard SQL query using the environment's default project
# df = client.query(sql).to_dataframe()
print("df")
df = client.query(sql, project=project_id).to_dataframe()
print("print df.head and df.shape")
print(df.shape)
print(df.head())
#df.to_csv("encounter_2016.csv")
print("df_csv")
print("quiver_sync_environment")
df.to_csv(quiver_path + "quiver_save2.csv")
print("check quiver save ")
