import os
import json
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

from config import SPREADSHEET_ID, WORKSHEET_NAME

# ============================================================
# GOOGLE AUTH
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

if os.getenv("GOOGLE_CREDS_JSON"):

    creds_info = json.loads(os.environ["GOOGLE_CREDS_JSON"])

    creds = Credentials.from_service_account_info(
        creds_info,
        scopes=SCOPES
    )

else:

    creds = Credentials.from_service_account_file(
        "google_creds.json",
        scopes=SCOPES
    )

client = gspread.authorize(creds)

spreadsheet = client.open_by_key(SPREADSHEET_ID)
worksheet = spreadsheet.worksheet(WORKSHEET_NAME)

# ============================================================
# HELPERS
# ============================================================

def parse_birthday(text: str) -> datetime:
    """
    Supported formats:
        03/07/2004
        3/7/2004
        03/07
        3/7
        03-07-2004
        03-07
    """

    text = text.strip()

    formats = [
        "%d/%m/%Y",
        "%d/%m",
        "%d-%m-%Y",
        "%d-%m",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass

    raise ValueError(f"Invalid birthday format: {text}")

# ============================================================
# MAIN
# ============================================================

def load_birthdays():

    rows = worksheet.get_all_values()

    people = []

    # Skip first 4 header rows
    for row_number, row in enumerate(rows[4:], start=5):

        try:

            if len(row) < 7:
                continue

            name = row[1].strip()

            if not name:
                continue

            department = row[2].strip()

            birthday = parse_birthday(row[3])

            gen = int(row[4].strip())

            assignee = row[6].strip()

            people.append(
                {
                    "name": name,
                    "department": department,
                    "birthday": birthday,
                    "gen": gen,
                    "assignee": assignee,
                }
            )

        except Exception as e:
            print(f"[Sheets] Row {row_number} skipped: {e}")

    return people


# ============================================================
# DEBUG
# ============================================================

if __name__ == "__main__":

    birthdays = load_birthdays()

    print(f"Loaded {len(birthdays)} birthdays.\n")

    for person in birthdays:
        print(person)
