from GoogleAuthenticator import authenticate
from Ad import Ad
from pprint import pprint
import sys
import requests

GOOGLE_CREDENTIALS_JSON_PATH = "./google_credentials.json"
GOOGLE_SPREADSHEET_NAME = "Boligjakt"
WORKSHEET_INDEX = 0


def insert_row(worksheet, annonse):
    addresses = worksheet.col_values(1)[1:]
    if annonse.adresse in addresses:
        row = addresses.index(annonse.adresse) + 2
        print(f'⚠ Ad already exists in row {row}. Deleting...', end='')
        worksheet.delete_rows(row)
        print(" ✔ deleted 1 row.")

    insert_at_row = len(worksheet.col_values(1)) + 1
    return worksheet.insert_row(annonse.get_sheet_values(), insert_at_row, "USER_ENTERED")


def push_ad_to_sheets(client, ad):
    worksheet = client.open(
        GOOGLE_SPREADSHEET_NAME).get_worksheet(WORKSHEET_INDEX)
    return insert_row(worksheet, ad)


def ping_uri(uri):
    ping = requests.get(uri).status_code

    if ping != 200:
        raise ValueError(
            f"Received invalid response (code: {ping}) from URI: {uri}")
    else:
        print(f"✔ The URI responded with status code {ping}.")


def run():

    if ("--uri" in sys.argv):
        uri = sys.argv[sys.argv.index("--uri")+1]
    else:
        uri = input("> Finn URI: ")

    ping_uri(uri)

    ad = Ad(uri)

    if ("--no-google" in sys.argv):
        pprint(ad.get_sheet_dict())
    else:
        client = authenticate(json_path=GOOGLE_CREDENTIALS_JSON_PATH)
        result = push_ad_to_sheets(client, ad)
        print(
            f"✔ Success! Ad pushed to the spreadsheet ({result['updatedCells']} affected cells)")


if __name__ == "__main__":
    run()
