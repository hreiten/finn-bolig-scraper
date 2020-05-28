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


def ping_uri(uri, verbose=0):
    ping = requests.get(uri).status_code

    if ping != 200:
        raise ValueError(
            f"Received invalid response (code: {ping}) from URI: {uri}")
    else:
        vprint(f"✔ The URI responded with status code {ping}.", verbose)


def get_index(array, *argv):
    for arg in argv:
        if arg in array:
            return arg, array.index(arg)
    return None, -1


def exists_flag_argument(flag, return_flag_value=False):
    found_flag, found_idx = get_index(sys.argv, flag, f'-{flag}', f'--{flag}')
    flag_exists = found_flag is not None

    def get_value(
        args, flag): return args[found_idx+1] if flag_exists else None

    return flag_exists if not return_flag_value else get_value(sys.argv, flag)


def update_existing_records(verbose=0):
    client = authenticate(json_path=GOOGLE_CREDENTIALS_JSON_PATH)
    worksheet = client.open(
        GOOGLE_SPREADSHEET_NAME).get_worksheet(WORKSHEET_INDEX)
    headers = worksheet.row_values(1)
    addresses = worksheet.col_values(1)[1:]

    def fmt_link(link): return link.split("\";")[0].split("=HYPERLINK(\"")[-1]

    links = [fmt_link(ad[0]) for ad in worksheet.get_all_values(
        value_render_option="FORMULA")[1:] if len(ad[0]) > 0]

    vprint("Scraping ad information...", verbose)

    dicts = []
    for i, link in enumerate(tqdm(links, ascii=True, unit="ad")):
        ad = Ad(link)
        sheet_dict = {
            "range": f"{i+2}:{i+2}",
            "values": [list(ad.get_sheet_dict(
                worksheet, headers, addresses).values())]
        }
        dicts.append(sheet_dict)

    vprint(f"Writing ${len(dicts)} to google sheets...", verbose)
    return worksheet.batch_update(dicts, value_input_option="USER_ENTERED")


def run():
    no_google_flag = exists_flag_argument("no-google")
    should_update_flag = exists_flag_argument("update")
    silent_flag = exists_flag_argument("silent")
    verbose = 0 if silent_flag else 1
    uri = exists_flag_argument("uri", True)

    if should_update_flag:
        confirm = input(
            "> Are you sure you wish to update all records in the spreadsheet? [yes | no] ")

        if confirm.lower() in ["yes", "y"]:
            update_existing_records(verbose=verbose)
        return

    if uri is None:
        uri = input("> Finn URI: ")

    ping_uri(uri, verbose)
    ad = Ad(uri)

    if no_google_flag:
        print(f"Data for URI {uri}")
        pprint(ad.get_ad_dict())
        return

    arg_dict = {}
    arg_dict["Vurdering"] = exists_flag_argument("v", True)
    arg_dict["Kommentar"] = exists_flag_argument("k", True)
    arg_dict["Tregulv + Takhøyde + Dobbeltdører"] = exists_flag_argument(
        "t", True)

    client = authenticate(json_path=GOOGLE_CREDENTIALS_JSON_PATH)
    worksheet = client.open(
        GOOGLE_SPREADSHEET_NAME).get_worksheet(WORKSHEET_INDEX)

    ad.push_to_worksheet(worksheet, arg_dict=arg_dict)
    vprint(
        f"✔ Success! Ad \"{ad.adresse}\" pushed to the spreadsheet.", verbose)


if __name__ == "__main__":
    run()
