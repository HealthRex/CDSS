import glob
import email
from email import policy
from email.parser import BytesParser
import os
from bs4 import BeautifulSoup
from google.cloud import bigquery

all_emails = []

for filepath in glob.glob('/Users/g0123/Downloads/emails/*.eml'):
    with open(filepath, 'rb') as fp:
        name = fp.name
        msg = BytesParser(policy=policy.default).parse(fp)
    text = msg.get_body(preferencelist='html').get_content()
    soup = BeautifulSoup(text, 'html.parser')
    table_body = soup.find('tbody')
    table_head = soup.find('thead')
    print(table_head)
    data = []
    dataHead = []
    for row in table_body.findAll("tr"):
        cols = row.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])

    for row in table_head.findAll("tr"):
        cols = row.find_all("th") #use 'td' to parse received emails. Else use 'th'
        cols = [ele.text.strip() for ele in cols]
        dataHead.append([ele for ele in cols if ele])

    print(dataHead)
    print(data)

    for row in data:
        vals_dict = {}
        for k, v in zip(dataHead[0], row):
            vals_dict[k] = v
        all_emails.append(vals_dict)
    fp.close()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = (
    '/Users/g0123/.config/gcloud/application_default_credentials.json'
)
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101-secure'

client = bigquery.Client("som-nero-phi-jonc101")
table_id = "som-nero-phi-jonc101-secure.grace_db.test_table"

response_set = set(('[x]', '[X]', 'x', 'X'))

for email in all_emails:
    response = None
    for k, v in email.items():
        if v in response_set:
            response = k
    print(email)

    update_query = """
    UPDATE `som-nero-phi-jonc101-secure.grace_db.test_table`
    SET Phys_estimate = {0}
    WHERE MRN = {1} and CSN = {2}
    """.format("'"+response+"'", email["MRN"], email["CSN"])
    print(update_query)

    client.query(update_query)
