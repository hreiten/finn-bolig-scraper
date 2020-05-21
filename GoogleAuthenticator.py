import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]


def authenticate():
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "creds.json", scope)
    return gspread.authorize(creds)
