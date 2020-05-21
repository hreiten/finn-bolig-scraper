from GoogleAuthenticator import authenticate
from Ad import Ad
from pprint import pprint
from tqdm import tqdm
import sys
import requests

GOOGLE_CREDENTIALS_JSON_PATH = "./google_credentials.json"
GOOGLE_SPREADSHEET_NAME = "Boligjakt"
WORKSHEET_INDEX = 0


def vprint(to_print, v=0, **args):
    if v != 0:
        print(to_print, **args)


def insert_row(worksheet, annonse, verbose=0):
    addresses = worksheet.col_values(1)[1:]

    comment, bids = "", ""
    comment_column = worksheet.row_values(1).index("Kommentar")
    bids_column = worksheet.row_values(1).index("Bud")

    if annonse.adresse in addresses:
        row = addresses.index(annonse.adresse) + 2
        vprint(
            f'⚠ Ad \"{annonse.adresse}\" already exists in row {row}. Deleting...', verbose, end='')
        comment = worksheet.cell(row, comment_column+1).value
        bids = worksheet.cell(row, bids_column+1).value

        worksheet.delete_rows(row)
        vprint(" ✔ deleted 1 row.", verbose)

    insert_at_row = len(worksheet.col_values(1)) + 1
    row_values = annonse.get_sheet_values()
    if comment != "":
        row_values[comment_column] = comment
    if bids != "":
        row_values[bids_column] = bids

    return worksheet.insert_row(
        row_values, insert_at_row, "USER_ENTERED")


def push_ad_to_sheets(worksheet, ad, verbose=0):
    return insert_row(worksheet, ad, verbose)


def ping_uri(uri, verbose=0):
    ping = requests.get(uri).status_code

    if ping != 200:
        raise ValueError(
            f"Received invalid response (code: {ping}) from URI: {uri}")
    else:
        vprint(f"✔ The URI responded with status code {ping}.", verbose)


def update_existing_records(verbose=0):
    client = authenticate(json_path=GOOGLE_CREDENTIALS_JSON_PATH)
    worksheet = client.open(
        GOOGLE_SPREADSHEET_NAME).get_worksheet(WORKSHEET_INDEX)

    def fmt_link(link): return link.split("\";")[0].split("=HYPERLINK(\"")[-1]
    links = [fmt_link(ad[0]) for ad in worksheet.get_all_values(
        value_render_option="FORMULA")[1:] if len(ad[0]) > 0]

    for finn_uri in tqdm(links, unit="finn_ad"):
        ad = Ad(finn_uri)
        push_ad_to_sheets(worksheet, ad, verbose)


def run():

    verbose = 0 if "--silent" in sys.argv else 1

    if "--update" in sys.argv:
        confirm = input(
            "> Are you sure you wish to update all records in the spreadsheet? [yes | no] ")
        if confirm.lower() == "yes":
            update_existing_records(verbose=0)
        return

    uri = ""
    if ("--uri" in sys.argv):
        uri = sys.argv[sys.argv.index("--uri")+1]
    else:
        uri = input("> Finn URI: ")

    ping_uri(uri, verbose)
    ad = Ad(uri)

    if ("--no-google" in sys.argv):
        print(f"Data for URI {uri}")
        pprint(ad.get_sheet_dict())
        return

    client = authenticate(json_path=GOOGLE_CREDENTIALS_JSON_PATH)
    worksheet = client.open(
        GOOGLE_SPREADSHEET_NAME).get_worksheet(WORKSHEET_INDEX)
    result = push_ad_to_sheets(worksheet, ad, verbose)
    vprint(
        f"✔ Success! Ad pushed to the spreadsheet ({result['updatedCells']} affected cells)", verbose)


if __name__ == "__main__":
    run()
