import os
from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import generateEmail

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = (
    '/Users/g0123/.config/gcloud/application_default_credentials.json'
)
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101-secure'

client = bigquery.Client("som-nero-phi-jonc101")
conn = dbapi.connect(client)
cursor = conn.cursor()

query = """
SELECT MRN, CSN, Name, Sex, Age, Latest_WBC, Latest_Hgb, Ordering_phys
FROM `som-nero-phi-jonc101-secure.grace_db.test_table`
WHERE Msg_sent = FALSE
"""

df = (
    client.query(query).result().to_dataframe()
)

email_dict = {
    'Rondeep Brar': 'yek1354@stanford.edu',
    'David Iberri': 'yek1354@stanford.edu',
    'Jason Gotlib': 'yek1354@stanford.edu'
}



bkt_list = ["<10%", "10-30%", "30-50%", "50-70%", "70-90%", ">90%"]
for bkt in bkt_list:
    df[bkt] = "[]"

for phys in email_dict.keys():
    phys_df = df.loc[df['Ordering_phys'] == phys]#.drop('Ordering_phys', 1)
    if len(phys_df) > 0:
        email = generateEmail.email(email=email_dict[phys],
                                    patient_data=phys_df)
        email.send_email()
        for index, row in phys_df.iterrows():
            print(row)
            mrn_val = row['MRN']
            csn_val = row['CSN']
            update_msg_status_query = """
            UPDATE `som-nero-phi-jonc101-secure.grace_db.test_table`
            SET Msg_sent = True
            WHERE MRN = {0} and CSN = {1}
            """.format(mrn_val, csn_val)
            client.query(update_msg_status_query)
