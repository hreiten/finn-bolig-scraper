from bs4 import BeautifulSoup as bs
import requests


def fmt_value(value):
    value = value.replace(" m²", "")
    value = value.replace(" kr", "")
    value = value.replace("\xa0", "")

    try:
        return int(value)
    except:
        return value.strip()


def get_dict(html):
    keys = [dt.text for dt in html.findAll("dt")]
    values = [fmt_value(dd.text) for dd in html.findAll("dd")]
    return dict(zip(keys, values))


def safe_ref(dictionary, key, default_return=None):
    if key in dictionary.keys():
        return dictionary[key]
    return default_return


class Ad:
    annonse_dict = None
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
    felleskostnader_per_måned = None
    forrige_salgsår = None
    forrige_salgspris = None
    bud = None
    solgt = None
    kommentar = ""

    def __init__(self, uri):
        self.uri = uri
        self.ad_id = int(uri.split("=")[-1].strip())
        self.scrape_info()

    def get_prev_sales_uri(self):
        return f'https://www.finn.no/realestate/ownershiphistory.html?finnkode={self.ad_id}'

    def scrape_info(self):
        page = requests.get(self.uri)
        soup = bs(page.content, 'html.parser')

        main_container = soup.findAll("div", {"class": "grid"})[1]
        sections = main_container.findAll("section", {"class": "panel"})
        divs = main_container.findAll("div", {"class": "panel"})

        ## Intro - area and address
        intro = sections[1]
        geography = {
            "Område": intro.span.text.strip(),
            "Adresse": intro.p.text.strip().split(",")[0]
        }

        # Info - all other information except pricing
        info_section = sections[2]
        info = get_dict(info_section.dl)
        # Pricing
        pricing = divs[2]
        pricing_dict = get_dict(pricing.findAll("dl")[1])
        pricing_dict["Prisantydning"] = fmt_value(
            pricing.find("span", {"class": "u-t3"}).text.strip())

        # Previous (most recent) sale
        previous_sale_dict = {
            "Forrige salgsår": "-",
            "Forrige salgspris": "-"
        }
        prev_sales_uri = self.get_prev_sales_uri()
        prev_sales_page = requests.get(prev_sales_uri)
        prev_sales_soup = bs(prev_sales_page.content, 'html.parser')

        table_contents = prev_sales_soup.table
        if table_contents:
            sale_year = int(table_contents.tbody.findAll(
                "td", {"class": "plm"})[0].text.strip().split(".")[-1])
            sale_price = table_contents.tbody.tr.findAll("td")[-1].text.strip()
            sale_price = int(sale_price.replace("\xa0", "").replace(",−", ""))

            previous_sale_dict["Forrige salgsår"] = sale_year
            previous_sale_dict["Forrige salgspris"] = sale_price

        # Finally, merge all the information to a single dict
        merged = {
            "Uri": self.uri,
            **geography,
            **info,
            **pricing_dict,
            **previous_sale_dict,
        }

        self.annonse_dict = merged

        self.adresse = safe_ref(merged, "Adresse")
        self.område = safe_ref(merged, "Område")

        self.boligtype = safe_ref(merged, "Boligtype")
        self.eieform = safe_ref(merged, "Eieform")
        self.soverom = safe_ref(merged, "Soverom")
        self.primærrom = safe_ref(merged, "Primærrom")
        self.bruksareal = safe_ref(merged, "Bruksareal")
        self.energimerking = safe_ref(merged, "Energimerking")
        self.etasje = safe_ref(merged, "Etasje")

        self.prisantydning = safe_ref(merged, "Prisantydning")
        self.fellesgjeld = safe_ref(merged, "Fellesgjeld")
        self.omkostninger = safe_ref(merged, "Omkostninger")
        self.totalpris = safe_ref(merged, "Totalpris")
        self.felleskostnader_per_måned = safe_ref(merged, "Felleskost/mnd.")

        self.forrige_salgsår = safe_ref(merged, "Forrige salgsår")
        self.forrige_salgspris = safe_ref(merged, "Forrige salgspris")

    def html_to_dict(self, html_list):
        labels = [label.text.strip() for label in html_list.findAll("dt")]
        values = [fmt_value(value.text.strip())
                  for value in html_list.findAll("dd")]

        return dict(zip(labels, values))

    def get_price_per_square_meter(self):
        return round((self.prisantydning + self.fellesgjeld) / self.primærrom, 0)

    def to_link(self, to, text):
        return '=HYPERLINK(\"{}\";\"{}\")'.format(to, text)

    def get_sheet_dict(self):
        return {
            'Adresse': self.to_link(self.uri, self.adresse),
            'Område': self.område,
            'Prisantydning': self.prisantydning,
            'Fellesgjeld': self.fellesgjeld,
            'Omkostninger': self.omkostninger,
            'Totalpris': self.totalpris,
            'FK/mnd': self.felleskostnader_per_måned,
            'Primærrom': self.primærrom,
            'NOK/kvm': self.get_price_per_square_meter(),
            'Forrige salgsår': self.forrige_salgsår,
            'Forrige salgspris': self.forrige_salgspris,
            'Bud': '',
            'Solgt': '',
            'Kommentar': ''
        }

    def get_sheet_values(self):
        return list(self.get_sheet_dict().values())
