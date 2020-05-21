from GoogleAuthenticator import authenticate
from Ad import Ad
import sys
import requests


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
    sheet_index = 0 if ad.soverom == 3 else 1
    worksheet = client.open("Boligjakt").get_worksheet(sheet_index)
    return insert_row(worksheet, ad)


def ping_uri(uri):
    ping = requests.get(uri).status_code

    if ping != 200:
        raise ValueError(
            f"Received invalid response (code: {ping}) from URI: {uri}")
    else:
        print(f"✔ The URL responded with status code {ping}.")


def run():

    uri = input("> Finn URI: ")
    ping_uri(uri)
    client = authenticate()

    result = push_ad_to_sheets(client, Ad(uri))
    print(
        f"✔ Success! Ad pushed to the spreadsheet ({result['updatedCells']} affected cells)")


if __name__ == "__main__":
    run()
