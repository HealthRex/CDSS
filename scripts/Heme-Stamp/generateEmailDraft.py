from appscript import app, k
import texttable as tt
import csv
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

outlook = app('Microsoft Outlook')

# tb = tt.Texttable()
# tb.header(["ID","Name", "Major","Grade"])
# tb.add_row([1,"Chi", "Statistics","3.5"])
# tb.add_row([2,"John","Business Administration","3.6"])
# tb.add_row([3,"Lily","Satistics","3.7"])
#print(tb.draw())

# d = [["Mark", 12, 95],
#      ["Jay", 11, 88],
#      ["Jack", 14, 90]]
#
# #print("{:<8} {:<15} {:<10}".format('Name', 'Age', 'Percent'))
# pps = ""
# for v in d:
#     name, age, perc = v
#     pps += "{:<8} {:<15} {:<10}".format(name, age, perc)
#     pps += "\n"
# print('pps')
# print(pps)

with open('input.csv') as input_file:
    reader = csv.reader(input_file)
    data = list(reader)

text = """
Hello, Friend.

Here is your data:

{table}

Regards,

Me"""

html = """
<html><body><p>Hello, Friend.</p>
<p>Here is your data:</p>
{table}
<p>Regards,</p>
<p>Me</p>
</body></html>
"""


text = text.format(table=tabulate(data, headers="firstrow", tablefmt="grid"))
html = html.format(table=tabulate(data, headers="firstrow", tablefmt="html"))

message = MIMEMultipart(
    "alternative", None, [MIMEText(text), MIMEText(html,'html')])




msg = outlook.make(
    new=k.outgoing_message,
    with_properties={
        k.subject: 'Test Email',
        k.plain_text_content: message.as_string(),
        k.html
    }
)

msg.make(
    new=k.recipient,
    with_properties={
        k.email_address: {
            k.name: 'Grace Kim',
            k.address: 'yek1354@stanford.edu'
        }
    }
)

msg.open()
msg.activate()

# import json
# import os
# import csv
# from tabulate import tabulate
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import smtplib
#
#
# class email(object):
#     def __init__(self, email, patient_dict):
#         self.email = email
#         self.patient_dict = patient_dict
#
#         with open(os.path.join(os.sys.path[0], "emailAuth.confg"), "r") as json_file:
#             creds = json.load(json_file)
#
#         self.sender = creds["sender"]
#         self.password = creds["password"]
#         self.server = 'smtp.stanford.edu'  # 'smtp.office365.com:587' for normal outlook
#         self.text = """
#             Hello,
#             {table}
#         """
#         self.html = """
#             <html><body><p>Hello</p>
#             {table}
#             </body></html>
#         """
#
#     with open('input.csv') as input_file:
#         reader = csv.reader(input_file)
#         data = list(reader)
#
#     text = text.format(table=tabulate(data, headers="firstrow", tablefmt="grid"))
#     html = html.format(table=tabulate(data, headers="firstrow", tablefmt="html"))
#
#     message = MIMEMultipart(
#         "alternative", None, [MIMEText(text), MIMEText(html, 'html')])
#
#     message['Subject'] = "Your data"
#     message['From'] = sender
#     message['To'] = receiver
#     server = smtplib.SMTP(server)
#     server.ehlo()
#     server.starttls()
#     server.login(sender, password)
#     server.sendmail(sender, receiver, message.as_string())
#     server.quit()