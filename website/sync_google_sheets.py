import os
import json
import gspread

from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_NAME = os.environ.get("SHEET_NAME")


def get_google_sheet():

    credentials_json = os.environ.get(
        "GOOGLE_CREDENTIALS"
    )

    credentials_dict = json.loads(
        credentials_json
    )

    credentials = Credentials.from_service_account_info(
        credentials_dict,
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)

    sheet = client.open(SHEET_NAME).sheet1

    return sheet


def add_user_to_google_sheet(user):

    try:

        sheet = get_google_sheet()

        sheet.append_row([
            user.id,
            user.email,
            user.first_name,
            user.last_name,
            user.is_verified
        ])

        print("User added to Google Sheets")

    except Exception as e:

        print("Google Sheets sync error:", e)