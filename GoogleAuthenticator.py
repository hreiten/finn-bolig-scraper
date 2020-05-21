import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]


def authenticate(json_path):
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        json_path, scope)
    return gspread.authorize(creds)
