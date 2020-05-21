from GoogleAuthenticator import authenticate
from Ad import Ad
import sys


def insert_row(worksheet, annonse):

    # check if ad already exists in the worksheet. If so, delete it.
    addresses = worksheet.col_values(1)[1:]
    if annonse.adresse in addresses:
        row = addresses.index(annonse.adresse) + 2
        worksheet.delete_rows(row)

    insert_at_row = len(worksheet.col_values(1)) + 1
    worksheet.insert_row(annonse.get_sheet_values(
    ), index=insert_at_row, value_input_option="USER_ENTERED")


def write_ad_to_sheets(client, uri):
    ad = Ad(uri)
    sheet_index = 0 if ad.soverom == 3 else 1
    worksheet = client.open("Boligjakt").get_worksheet(sheet_index)
    insert_row(worksheet, ad)


def run():
    print_err = False

    if len(sys.argv) > 1:
        uri = sys.argv[-1]
        if "finn.no" in uri:
            client = authenticate()
            write_ad_to_sheets(client, uri)
        else:
            print_err = True
    else:
        print_err = True

    if print_err:
        print("Error! You must provide a valid Finn URI as the only argument.")


if __name__ == "__main__":
    run()
