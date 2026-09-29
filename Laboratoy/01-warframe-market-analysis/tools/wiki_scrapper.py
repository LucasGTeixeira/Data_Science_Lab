import requests
from html.parser import HTMLParser
from pathlib import Path
import re

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
    string = re.sub(r'(?<=[a-z])(?=[A-Z])|[^a-zA-Z]', ' ', string).strip().replace(' ', '_')
    return ''.join(string.lower())


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


if __name__ == "__main__":
    here = Path(__file__).parent
    bond = get_bond_mod_names(here / "html_bond_example.html")
    assert len(bond) == 14 and "Aerial Bond" in bond
    aug = get_augment_mod_names()
    assert aug["Seeking Shuriken"] == ["Arbiters of Hexis", "Red Veil"]
    assert len(aug) >= 200
    print(f"{len(aug)} augment mods, {len(bond)} bond mods")