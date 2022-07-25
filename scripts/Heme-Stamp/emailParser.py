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
    data = []
    dataHead = []
    for row in table_body.findAll("tr"):
        cols = row.find_all("td")
        cols1 = [ele.text.strip() for ele in cols[:6]]
        cols2 = [ele.text for ele in cols[6:]]
        cols = cols1 + cols2
        # cols = [ele.text.strip() for ele in cols]
        # data.append([ele for ele in cols if ele])
        data.append(cols)

    print(table_head.findAll("tr"))
    for row in table_head.findAll("tr"):
        cols = row.find_all("th") #use 'td' to parse received emails. Else use 'th'
        if not cols:
            cols = row.find_all("td")
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
response_headers = set(('<10%', '10-30%', '30-50%', '50-70%', '70-90%', '>90%'))

for email in all_emails:
    response = None
    for k, v in email.items():
        #if k in response_headers and (v.strip() in response_set or v.strip() != ""):
        if k in response_headers and v.strip() != "":
            response = k
    print("email: ", email)

    email["Notes"] = email["Notes"].strip()

    if response:
        if email["Notes"]:
            update_query = """
            UPDATE `som-nero-phi-jonc101-secure.grace_db.test_table`
            SET Phys_estimate = {0}, Notes = {1}, Response = True
            WHERE MRN = {2}
            """.format("'"+response+"'", "'''"+email["Notes"]+"'''", email["MRN"])
            print(update_query)
        else:
            update_query = """
            UPDATE `som-nero-phi-jonc101-secure.grace_db.test_table`
            SET Phys_estimate = {0}, Response = True
            WHERE MRN = {1}
            """.format("'" + response + "'", email["MRN"])
            print(update_query)

    elif email["Notes"]:
        update_query = """
        UPDATE `som-nero-phi-jonc101-secure.grace_db.test_table`
        SET Notes = {0}, Response = True
        WHERE MRN = {1}
        """.format("'''" + email["Notes"] + "'''", email["MRN"])
        print(update_query)


    client.query(update_query)



