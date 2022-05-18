import os
from google.cloud import bigquery

new_order_dict = {
    "CSN": 9562,
    "MRN": 103741,
    "Name": "Venus Flytrap",
    "Ordering_Phys": "Rondeep Brar",
    "Msg_sent": False,
    "Latest_WBC": 4.3,
    "Latest_Hgb": 11.8,
    "Age": 46,
    "Sex": "Female"
}


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = (
    '/Users/g0123/.config/gcloud/application_default_credentials.json'
)
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101-secure'

client = bigquery.Client("som-nero-phi-jonc101")
table_id = "som-nero-phi-jonc101-secure.grace_db.test_table"
rows_to_insert = [new_order_dict]
errors = client.insert_rows_json(table_id, rows_to_insert)
if errors == []:
    print("New rows have been added.")
else:
    print("Encountered errors while inserting rows: {}".format(errors))



