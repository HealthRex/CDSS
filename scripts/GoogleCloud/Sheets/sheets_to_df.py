'''
for JSON file, go to https://console.developers.google.com/apis/credentials for your project

useful references:
https://towardsdatascience.com/how-to-access-google-sheet-data-using-the-python-api-and-convert-to-pandas-dataframe-5ec020564f0e
https://developers.google.com/sheets/api/samples/
'''


import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd


class GoogleSheetsConnect:
    '''
    modified from Google Sheets API example
    '''

    def __init__(self, json_file):
        # Authenticate and connect

        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    json_file,
                    SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def get_sheet(self, sheet_id, range_name):
        # Get sheet result

        sheet_hook = self.service.spreadsheets()
        sheet_result = list(sheet_hook.values()).get(spreadsheetId=sheet_id, range=range_name).execute()
        return sheet_result

    def get_df(self, sheet_result, verbose=False, first_line_header=True):
        # Get DF from sheet result

        if first_line_header:
            # Assumes first line is headers
            headers = sheet_result.get('values', [])[0]
            values = sheet_result.get('values', [])[1:]
        else:
            values = sheet_result.get('values', [])
            headers = list(range(len(sheet_result.get('values', [])[0])))

        df = pd.DataFrame()

        for i, series_name in enumerate(headers):
            if verbose:
                print('Preparing {}/{} {}'.format(i + 1, len(headers), series_name))
            series_data = [row[i] for row in values]
            df[series_name] = series_data

        return df
