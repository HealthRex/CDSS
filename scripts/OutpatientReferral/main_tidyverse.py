

'''
https://cloud.google.com/bigquery/docs/reference/libraries
'''

from google.cloud import bigquery

client = bigquery.Client.from_service_account_json('MiningClinicalDecisions_Song.json')
project_id = 'mining-clinical-decisions'
sql =\
'''
select * from `datalake_47618_sample.encounter`
where appt_time_jittered > "2015-12-31" and appt_time_jittered < "2017-01-01"
'''
print("sql saved")
"""
select patient_item_id, external_id, clinical_item_id, item_date, encounter_id, text_value, num_value, source_id from 
`clinical_inpatient.patient_item` where item_date >= timestamp('2014-01-01 00:00:00')
"""
# Run a Standard SQL query using the environment's default project
# df = client.query(sql).to_dataframe()
print("df")

df = client.query(sql, project=project_id).to_dataframe()
print("print df.head and df.shape")
print(df.shape)
print(df.head())