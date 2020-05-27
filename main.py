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


def update_existing_records(verbose=0):
    client = authenticate(json_path=GOOGLE_CREDENTIALS_JSON_PATH)
    worksheet = client.open(
        GOOGLE_SPREADSHEET_NAME).get_worksheet(WORKSHEET_INDEX)

    def fmt_link(link): return link.split("\";")[0].split("=HYPERLINK(\"")[-1]

    links = [fmt_link(ad[0]) for ad in worksheet.get_all_values(
        value_render_option="FORMULA")[1:] if len(ad[0]) > 0]

    for finn_uri in tqdm(links, unit="ad"):
        ad = Ad(finn_uri)
        ad.push_to_worksheet(worksheet)


def any_match(container_list, *argv):
    return any([arg in container_list for arg in argv])


def run():
    verbose = 0 if any_match(sys.argv, "--silent", "-silent") else 1

    if any_match(sys.argv, "--update", "-update"):
        confirm = input(
            "> Are you sure you wish to update all records in the spreadsheet? [yes | no] ")
        if confirm.lower() == "yes" or confirm.lower() == "y":
            update_existing_records(verbose=0)
        else:
            print("Aborting...")
        return

    uri = ""
    if any_match(sys.argv, "--uri", "-uri"):
        uri = sys.argv[sys.argv.index(
            "--uri" if "--uri" in sys.argv else "-uri")+1]
    else:
        uri = input("> Finn URI: ")

    ping_uri(uri, verbose)
    ad = Ad(uri)

    if any_match(sys.argv, "--no-google", "-no-google"):
        print(f"Data for URI {uri}")
        pprint(ad.get_values_dict())
        return

    arg_dict = dict.fromkeys(["Kommentar", "Vurdering"])
    if any_match(sys.argv, "-k", "--k"):
        arg_dict["Kommentar"] = sys.argv[sys.argv.index(
            "--k" if "--k" in sys.argv else "-k")+1]

    if any_match(sys.argv, "-v", "--v"):
        arg_dict["Vurdering"] = sys.argv[sys.argv.index(
            "--v" if "--v" in sys.argv else "-v")+1]

    client = authenticate(json_path=GOOGLE_CREDENTIALS_JSON_PATH)
    worksheet = client.open(
        GOOGLE_SPREADSHEET_NAME).get_worksheet(WORKSHEET_INDEX)

    ad.push_to_worksheet(worksheet, arg_dict)
    vprint(
        f"✔ Success! Ad \"{ad.adresse}\" pushed to the spreadsheet.", verbose)


if __name__ == "__main__":
    run()
