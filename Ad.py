from bs4 import BeautifulSoup as bs
import requests


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
    felleskost_per_måned = None
    forrige_salg_år = None
    forrige_salg_pris = None
    bud = None
    solgt = None
    finn_id = None
    kommentar = ""

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
        self.solgt = ad_scraper.body.find("span", text="SOLGT") is not None

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

    def get_sheet_dict(self):
        return {
            'Adresse': self.to_link(self.uri, self.adresse),
            'Område': self.område,
            'Prisantydning': self.prisantydning,
            'Fellesgjeld': self.fellesgjeld,
            'Omkostninger': self.omkostninger,
            'Totalpris': self.totalpris,
            'FK/mnd': self.felleskost_per_måned,
            'Primærrom': self.primærrom,
            'NOK/kvm': self.get_price_per_square_meter(),
            'Forrige salgsår': self.forrige_salg_år,
            'Forrige salgspris': self.forrige_salg_pris,
            'Bud': '',
            'Solgt': self.solgt,
            'Kommentar': ''
        }

    def get_sheet_values(self):
        return list(self.get_sheet_dict().values())
