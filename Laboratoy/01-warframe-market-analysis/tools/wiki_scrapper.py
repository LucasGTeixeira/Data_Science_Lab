import requests
from html.parser import HTMLParser
from pathlib import Path
import re
import logging
import pandas as pd
import time

AUGMENT_URL = "https://wiki.warframe.com/w/Warframe_Augment_Mods"
BOND_URL = "https://wiki.warframe.com/w/Bond_Mods"

class _TooltipParser(HTMLParser):
    """Coleta spans com data-param-name agrupados por data-param-source,
    uma entrada por linha da tabela."""

    def __init__(self, row_id_only):
        super().__init__()
        self.rows = []
        self._row = None
        self._row_id_only = row_id_only

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "tr":
            if not self._row_id_only or a.get("id"):
                self._row = {}
        elif tag == "span" and self._row is not None:
            name = a.get("data-param-name")
            if name:
                self._row.setdefault(a.get("data-param-source"), []).append(name)

    def handle_endtag(self, tag):
        if tag == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None


def _fetch(source, default_url):
    if source is None:
        return requests.get(default_url).text
    if str(source).startswith("http"):
        return requests.get(source).text
    if Path(source).exists():
        return Path(source).read_text(encoding="utf-8")
    return source


def _parse(html, row_id_only):
    parser = _TooltipParser(row_id_only)
    parser.feed(html)
    return parser.rows

def toSnakeCase(string):
    string = string.replace("'", "")
    string = string.replace("&", "and")
    string = re.sub(
        r"(?<=[a-z])(?=[A-Z])|[^a-zA-Z&]",
        " ",
        string
    ).strip().replace(" ", "_")
    return string.lower()


def get_augment_mod_names(source=None):
    """Retorna {nome_do_mod: [sindicatos]} da pagina Warframe Augment Mods."""
    out = {}
    for row in _parse(_fetch(source, AUGMENT_URL), row_id_only=True):
        for mod in row.get("Mods", []):
            mod = toSnakeCase(mod)
            out[mod] = row.get("Factions", [])
    return out

def get_bond_mod_names(source=None):
    """Retorna lista de nomes dos Bond Mods."""
    return [toSnakeCase(row["Mods"][0]) for row in _parse(_fetch(source, BOND_URL), row_id_only=False) if "Mods" in row]

def get_order_request(url):
    time.sleep(1)
    response = requests.get(url)
    response.raise_for_status()
    return response

def get_mod_offers_current(mod_names_list: list[str]):
    df_concat = pd.DataFrame()
    for mod_name in mod_names_list:
        logging.info(f"Collecting orders from {mod_name}")
        url = f"https://api.warframe.market/v2/orders/item/{mod_name}"
        try:
            mod_orders = get_order_request(url)
        except Exception as e:
            raise (f"Could not retrieve data from mod_name {mod_name}\nError: {e}")
        df_order = pd.DataFrame(mod_orders.json()["data"])
        df_order['mod_name'] = mod_name
        df_concat = pd.concat([df_concat, df_order])
    df_concat['user'] = df_concat['user'].str['ingameName']
    df_concat = df_concat.sort_values('rank', ascending=False)
    return df_concat

def get_mod_offers_statistics(augment_mods_list:list[str]):
    collect_modes = ["statistics_closed", "statistics_live"]
    time_period = ["90days", "48hours"]
    df_concat = pd.DataFrame()
    for mod_name in augment_mods_list:
        logging.info(f"Collecting timeseries from {mod_name}")
        url = f"https://api.warframe.market/v1/items/{mod_name}/statistics"
        try:
            mod_orders = get_order_request(url)
        except Exception as e:
            raise (f"Could not retrieve data from mod_name {mod_name}\nError: {e}")
        for mode in collect_modes:
            for period in time_period:
                df_order = pd.DataFrame(mod_orders.json()["payload"][mode][period])
                df_order['period'] = period
                df_order["mode"] = ("live" if mode == "statistics_live" else "closed")
                df_order["mod_name"] = mod_name
                df_concat = pd.concat([df_concat, df_order])
    df_concat = df_concat.sort_values('datetime', ascending=False)
    return df_concat