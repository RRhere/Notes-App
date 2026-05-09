import json
import logging
import os

import gspread
from google.oauth2.service_account import Credentials

from .models import User

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_NAME = os.environ.get("SHEET_NAME")


def get_google_sheet():
    # BUG FIX: guard against missing env vars — previously json.loads(None)
    # would raise TypeError and crash the caller with an opaque traceback.
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS")
    if not credentials_json:
        raise Exception("GOOGLE_CREDENTIALS missing")

    if not SHEET_NAME:
        raise EnvironmentError(
            "SHEET_NAME environment variable is not set. "
            "Google Sheets sync is disabled."
        )

    try:
        credentials_dict = json.loads(credentials_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"GOOGLE_CREDENTIALS is not valid JSON: {e}") from e

    credentials = Credentials.from_service_account_info(
        credentials_dict,
        scopes=SCOPES,
    )
    client = gspread.authorize(credentials)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet


def sync_with_google_sheets():

    try:

        sheet = get_google_sheet()

        users = User.query.all()

        data = [
            [
                "ID",
                "Email",
                "First Name",
                "Last Name",
                "Verified"
            ]
        ]

        for user in users:

            data.append([
                user.id,
                user.email,
                user.first_name,
                user.last_name,
                user.is_verified
            ])

        sheet.clear()

        sheet.update("A1", data)

        print("Google Sheets synced successfully")

    except Exception as e:

        print("Google Sheets sync error:", e)