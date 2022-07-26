import os
from google.cloud import bigquery
import generateEmail


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = (
    '/Users/g0123/.config/gcloud/application_default_credentials.json'
)
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101-secure'

client = bigquery.Client("som-nero-phi-jonc101")
table_id = "som-nero-phi-jonc101-secure.grace_db.test_table"

bkt_list = ["<10%", "10-30%", "30-50%", "50-70%", "70-90%", ">90%"]

query = """
SELECT MRN, Name, Ordered, Age, WBC, Hgb, Physician, Notes
FROM `som-nero-phi-jonc101-secure.grace_db.test_table`
WHERE Msg_sent is not TRUE
"""



email_dict = {
    'Rondeep Singh Brar': 'rbrar@stanford.edu',
    'David Joseph Iberri': 'diberri@stanford.edu',
    'William Elias Shomali': 'wshomali@stanford.edu'
}

# email_dict = {
#     'Rondeep Singh Brar': 'yek1354@stanford.edu',
#     'David Joseph Iberri': 'yek1354@stanford.edu',
#     'William Elias Shomali': 'yek1354@stanford.edu'
# }

def upload_order(new_order_dict):
    print("new order dict: ", new_order_dict)
    rows_to_insert = [new_order_dict]

    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))

def send_email():
    df = (
        client.query(query).result().to_dataframe()
    )
    print(df)
    for bkt in bkt_list:
        df[bkt] = ""

    for phys in email_dict.keys():
        phys_df = df.loc[df['Physician'] == phys]
        del phys_df["Physician"]
        cols = phys_df.columns.tolist()
        cols = cols[:6] + cols[7:] + [cols[6]]
        phys_df = phys_df[cols]
        print(phys_df)
        if len(phys_df) > 0:
            print(phys_df)
            email = generateEmail.email(email=email_dict[phys],
                                        patient_data=phys_df)
            email.send_email()
            for index, row in phys_df.iterrows():
                print(row)
                mrn_val = row['MRN']
                update_msg_status_query = """
                UPDATE `som-nero-phi-jonc101-secure.grace_db.test_table`
                SET Msg_sent = True
                WHERE MRN = {0}
                """.format(mrn_val)
                print(update_msg_status_query)
                client.query(update_msg_status_query)
