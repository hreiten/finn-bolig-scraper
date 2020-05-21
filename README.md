# finn-bolig-scraper

This python program scrapes real estate listings on <a href="https://finn.no">finn.no</a> and populates a google sheets document with the scraped information.

As of 21st of May 2020, the following information is scraped from an ad:

- Address and area
- Asking price, collective debt, sales costs, monthly collective expenses and the total price
- Previous sales of the real estate object
- Other information about the real estate object such as type, floor, number of bedrooms, floor area etc.

The program is written purely in python3, using Google's sheets API and `gspread` for communication with the online spreadsheets, and Beautifulsoup4 for the web scraping.

## Getting started

Make sure that you have python3 installed along with [pipenv](https://pypi.org/project/pipenv/).

1. Clone this project and navigate into the cloned folder locally
2. Install packages and activate the virtual environment
3. Optional: Obtain google credentials (see own documentation for this further down). If you do not do this, you _must_ run the program with the `no-google`-flag, otherwise it will fail.

```
pipenv install
pipenv shell
```

4. Change the program parameters (found in `./main.py`)

   - GOOGLE_CREDENTIALS_JSON_PATH: path to the json with google credentials obtained in the previous step. Default: "./creds.json"
   - GOOGLE_SPREADSHEET_NAME: name of the spreadsheet you wish to edit via the API. Default: "Boligjakt".
   - WORKSHEET_INDEX: the index of the sheet to use within the spreadsheet. Defaults to 0 (first sheet).

5. The program is run with

```
python main.py
```

The program has the following flags implemented:

| flag        | description                                                                                  | usage                         |
| ----------- | -------------------------------------------------------------------------------------------- | ----------------------------- |
| --uri       | Specify real estate URI after this flag. If not specified, user will be prompted to type it. | --uri www.finn/some-estate.no |
| --no-google | Ignores google sheets functionality, i.e. does not require usage of the google sheets API.   | --no-google                   |
| --silent    | Silence all printing.                                                                        | --silent                      |
| --update    | Update existing records in the spreadsheet (Refetch data)                                    | --update                      |

All flags can be combined.

## Obtaining google credentials

In order to use the Google sheets API you must first obtain the necessary credentials. [This guy](https://www.youtube.com/watch?v=cnplklegr7e&t=338s) explains it pretty well, but I'll also explain in textually here.

1. Go to console.cloud.google.com
2. Create a new project. Name it anything you want, no organization.
3. Navigate to your project if you're not redirected there.
4. Go to APIs and services -> Enable APIs and services and enable Google Drive.
5. Click `create credentials` and follow the steps. Eventually, a .json-file should be downloaded.
6. Repeat the process from step 4 and enable the Google Sheets API.
7. Go to your spreadsheet and share it with your user. The email found in the json-file.

Save the .json-file somewhere and change the `GOOGLE_CREDENTIALS_JSON_PATH`-variable to point to it.
