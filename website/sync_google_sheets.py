import os
import json
import gspread

from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_NAME = "Your Sheet Name"


def get_google_sheet():

    credentials_json = os.environ.get("GOOGLE_CREDENTIALS")

    credentials_dict = json.loads(credentials_json)

    credentials = Credentials.from_service_account_info(
        credentials_dict,
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)

    sheet = client.open(SHEET_NAME).sheet1

    return sheet