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
            Hello, thank you for participating in our study. To respond, please click the Reply button, press "..." to show the
            email chain, and directly edit the table below. Please mark X in the corresponding column to indicate your
            estimation of the likelihood that the Heme-STAMP test will result in at least one pathogenic variant for each patient.  
            Please try to avoid  adding anything other than an X in these cells to ensure that we can automatically parse responses. 
            Please feel free to utilize the Notes column to add any additional comments.
            
            This data was pulled from Epic and based on orders that have been submitted in the last week. If one of these orders
            have since been canceled or you believe was mistakenly included, please write Canceled in the Notes section.
            
            We have added the latest WBC and Hgb count for your convenience. 
            
            Thank you!
            {table} 
        """
        self.html_content = """
            <html>
            <head>
                <style> 
                  table, th, td {{ border: 1px solid black; border-collapse: collapse; overflow: hidden; white-space: nowrap;}}
                  th, td, tr {{ padding: 5px; overflow: hidden; white-space: nowrap;}}
                </style>
                </head>
            <body><p>Hello, thank you for participating in our study. 
            <br>
            <br>
            To respond, please click the Reply button, press "..." to show the
            email chain, and directly edit the table below. Please mark X in the corresponding column to indicate your
            estimation of the likelihood that the Heme-STAMP test will result in at least one pathogenic variant for each patient.
            <br>
            <br>  
            Please try to avoid  adding anything other than an X in these cells to ensure that we can automatically parse responses. 
            Please feel free to utilize the Notes column to add any additional comments.
            <br>
            <br>
            This data was pulled from Epic and based on orders that have been submitted in the last week. If one of these orders
            have since been canceled or you believe was mistakenly included, please mark Canceled in the Notes section.
            <br>
            <br>
            We have added the latest WBC and Hgb count for your convenience. 
            <br>
            <br>
            Thank you! </p>
            {table}
            </body>
            </html>
        """


    def send_email(self):
        data = self.patient_data
        col_names = data.columns.tolist()
        #data.set_index("MRN", inplace=True)
        text = self.text_content.format(table=tabulate(data, showindex=False, headers=col_names, tablefmt="fancy_grid"))
        html = self.html_content.format(table=tabulate(data, showindex=False, headers=col_names, tablefmt="html"))

        message = MIMEMultipart(
            "alternative", None, [MIMEText(text), MIMEText(html,'html')])

        message['Subject'] = "Secure: Heme-STAMP Estimates"
        message['From'] = self.sender
        message['To'] = self.email
        message['CC'] = self.sender
        server = smtplib.SMTP(self.server)
        server.ehlo()
        server.starttls()
        server.login(self.sender, self.password)
        server.sendmail(self.sender, ([self.email] + [self.sender]), message.as_string())
        server.quit()
        print("email sent")