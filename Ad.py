from bs4 import BeautifulSoup as bs
import requests
import datetime


def safe_get_from_dict(dictionary, key):
    return dictionary[key] if key in dictionary.keys() else None


def fmt_value(value):
    value = value.replace(" m²", "")
    value = value.replace(" kr", "")
    value = value.replace("\xa0", "")
    value = value.replace(",−", "")

    try:
        return int(value.strip())
    except:
        return value.strip()


class Scraper:

    def __init__(self, uri, body_tag="div", body_class=None):
        self.uri = uri
        page = requests.get(uri)
        self.soup = bs(page.content, 'html.parser')
        self.body = self.soup.find(
            body_tag, {"class": body_class}) if body_class else self.soup.find(body_tag)

    def find_by_value(self, label, tag):
        label_tag = self.body.find(tag, text=label)
        if label_tag:
            return fmt_value(label_tag.next_sibling.next_sibling.text.strip())


class Ad:
    adresse = None
    område = None
    boligtype = None
    eieform = None
    soverom = None
    primærrom = None
    bruksareal = None
    etasje = None
    energimerking = None
    prisantydning = None
    fellesgjeld = None
    omkostninger = None
    totalpris = None
    felleskost_per_måned = None
    forrige_salg_år = None
    forrige_salg_pris = None
    status = None
    finn_id = None

    def __init__(self, uri):
        self.uri = uri
        self.finn_id = int(uri.split("=")[-1].strip())
        self.scrape_info()

    def get_prev_sales_uri(self):
        return f'https://www.finn.no/realestate/ownershiphistory.html?finnkode={self.finn_id}'

    def scrape_info(self):
        ad_scraper = Scraper(self.uri, "div", "grid__unit u-r-size2of3")

        # area and geographic information
        område = ad_scraper.body.find(
            "span", {"class": "u-t3 u-display-block"})
        self.område = område.text.title() if område else None
        adresse = ad_scraper.body.find("p", {"class": "u-caption"})
        self.adresse = adresse.text.split(",")[0] if adresse else None

        # other info
        self.boligtype = ad_scraper.find_by_value("Boligtype", "dt")
        self.eieform = ad_scraper.find_by_value("Eieform", "dt")
        self.soverom = ad_scraper.find_by_value("Soverom", "dt")
        self.etasje = ad_scraper.find_by_value("Etasje", "dt")
        self.primærrom = ad_scraper.find_by_value("Primærrom", "dt")
        self.bruksareal = ad_scraper.find_by_value("Bruksareal", "dt")
        self.energimerking = ad_scraper.find_by_value("Energimerking", "dt")
        status = ad_scraper.body.find("span", {"class": "status"})
        if status:
            self.status = status.text.title()

        # pricing
        self.fellesgjeld = ad_scraper.find_by_value("Fellesgjeld", "dt")
        self.omkostninger = ad_scraper.find_by_value("Omkostninger", "dt")
        self.totalpris = ad_scraper.find_by_value("Totalpris", "dt")
        self.felleskost_per_måned = ad_scraper.find_by_value(
            "Felleskost/mnd.", "dt")
        self.prisantydning = ad_scraper.find_by_value(
            "Prisantydning", "span")

        # previous sales
        prev_sales_scraper = Scraper(self.get_prev_sales_uri(), "table")
        if prev_sales_scraper.body:
            self.forrige_salg_år = fmt_value(prev_sales_scraper.body.tbody.find(
                "td", {"class": "plm"}).text.strip().split(".")[-1])
            self.forrige_salg_pris = fmt_value(
                prev_sales_scraper.body.tbody.tr.findAll("td")[-1].text.strip())

    def get_price_per_square_meter(self):
        if not self.primærrom:
            return None

        ppsm = 0
        if self.prisantydning:
            ppsm += self.prisantydning
        if self.fellesgjeld:
            ppsm += self.fellesgjeld
        if self.omkostninger:
            ppsm += self.omkostninger

        return round(ppsm/self.primærrom, 0)

    def to_link(self, to, text):
        return '=HYPERLINK(\"{}\";\"{}\")'.format(to, text)

    def get_row_in_sheet(self, addresses=None, worksheet=None):
        if addresses is None:
            if worksheet is None:
                raise Exception("No worksheet supplied")
            addresses = worksheet.col_values(1)[1:]

        try:
            return addresses.index(self.adresse) + 2
        except:
            return -1

    def get_ad_dict(self):
        return {
            'Adresse': self.to_link(self.uri, self.adresse),
            'Område': self.område,
            'Boligtype': self.boligtype,
            'Eieform': self.eieform,
            'Soverom': self.soverom,
            'Primærrom': self.primærrom,
            'Bruksareal': self.bruksareal,
            'Etasje': self.etasje,
            'Energimerking': self.energimerking,
            'Prisantydning': self.prisantydning,
            'Fellesgjeld': self.fellesgjeld,
            'Omkostninger': self.omkostninger,
            'Totalpris': self.totalpris,
            'FK/mnd': self.felleskost_per_måned,
            'NOK/kvm': self.get_price_per_square_meter(),
            'Forrige salgsår': self.forrige_salg_år,
            'Forrige salgspris': self.forrige_salg_pris,
            'Status': self.status
        }

    def get_sheet_dict(self, worksheet, headers=None, addresses=None, arg_dict={}):
        ad_dict = self.get_ad_dict()

        if headers is None:
            headers = worksheet.row_values(1)

        sheet_dict = dict.fromkeys(headers)

        # populate the dictionary
        for key in sheet_dict:
            sheet_dict[key] = safe_get_from_dict(ad_dict, key)

        # keep "manual" data, e.g. user comments, that is not scraped
        ad_row = self.get_row_in_sheet(addresses, worksheet)
        if ad_row >= 0:
            ad_data = worksheet.row_values(ad_row)
            keep_columns = ["Vurdering",
                            "Max bud",
                            "Tregulv + Takhøyde + Dobbeltdører",
                            "Kommentar",
                            "Påmeldt budrunde",
                            "Lagt til"]

            for col_name in keep_columns:
                if col_name in headers:
                    sheet_dict[col_name] = ad_data[headers.index(col_name)]

        else:
            sheet_dict["Lagt til"] = datetime.datetime.now().strftime(
                "%d.%m.%Y")

        if len(arg_dict) > 0:
            for key, value in arg_dict.items():
                if key in sheet_dict and value:
                    sheet_dict[key] = value

        return sheet_dict

    def push_to_worksheet(self, worksheet, headers=None, addresses=None, arg_dict={}):
        sheet_dict = self.get_sheet_dict(
            worksheet=worksheet, headers=headers, addresses=addresses, arg_dict=arg_dict)
        ad_row = self.get_row_in_sheet(addresses, worksheet)

        if ad_row >= 0:
            return worksheet.update(f"{ad_row}:{ad_row}", [list(sheet_dict.values())], value_input_option="USER_ENTERED")

        return worksheet.append_row(list(sheet_dict.values()), value_input_option="USER_ENTERED")
