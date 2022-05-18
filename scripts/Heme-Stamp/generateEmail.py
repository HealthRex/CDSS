import json
import os
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

class email(object):
    def __init__(self, email, patient_data):
        self.email = email
        self.patient_data = patient_data

        with open(os.path.join(os.sys.path[0], "emailAuth.confg"), "r") as json_file:
            creds = json.load(json_file)

        self.sender = creds["sender"]
        self.password = creds["password"]
        self.server = 'smtp.stanford.edu'
        self.text_content = """
            Hello,
            {table} 
        """
        self.html_content = """
            <html><body><p>Hello</p>
            {table}
            </body></html>
        """



    def send_email(self):
        data = self.patient_data
        col_names = data.columns.tolist()
        #data.set_index("MRN", inplace=True)
        text = self.text_content.format(table=tabulate(data, showindex=False, headers=col_names, tablefmt="fancy_grid"))
        html = self.html_content.format(table=tabulate(data, showindex=False, headers=col_names, tablefmt="html"))

        message = MIMEMultipart(
            "alternative", None, [MIMEText(text), MIMEText(html,'html')])

        message['Subject'] = "HS Estimates"
        message['From'] = self.sender
        message['To'] = self.email
        server = smtplib.SMTP(self.server)
        server.ehlo()
        server.starttls()
        server.login(self.sender, self.password)
        server.sendmail(self.sender, self.email, message.as_string())
        server.quit()
        print("email sent")