from __future__ import print_function
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GoogleModel:
    def __init__(self, google_private_key, spreadsheet_id, range_name, google_client_email):
        self.google_private_key = google_private_key.replace('\\n', '\n')
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name
        self.google_client_email = google_client_email

    def get_google_credentials(self):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        account_info = {
            "private_key": self.google_private_key,
            "client_email": self.google_client_email,
            "token_uri": "https://accounts.google.com/o/oauth2/token",
        }

        credentials = service_account.Credentials.from_service_account_info(account_info, scopes=scopes)
        return credentials

    def get_google_credentials_v2(self):
        # If modifying these scopes, delete the file token.json.
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return creds

    def get_google_service(self, service_name='sheets', api_version='v4'):
        # credentials = self.get_google_credentials()
        credentials = self.get_google_credentials_v2()
        service = build(service_name, api_version, credentials=credentials)
        return service

    def write_to_google_sheet(self, values):
        service = self.get_google_service()
        body = {
            'values': values
        }
        value_input_option = 'RAW'
        service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=self.range_name,
            valueInputOption=value_input_option,
            body=body).execute()

    def read_from_google_sheet(self) -> dict:
        service = self.get_google_service()
        result = service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id,
                                                     range=self.range_name, ).execute()
        values = result.get('values', [])
        return self.reformat_data(values)

    def reformat_data(self, values) -> dict:
        data = {}
        for item in values:
            item[4] = float(item[4])
            data[item[-1]] = item
        return data
