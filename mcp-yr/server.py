"""Mały serwer MCP (Streamable HTTP) dla Google AI Edge Gallery.

Dwa narzędzia, krótkie odpowiedzi (okno kontekstu 4B jest małe):
  - pogoda(miejsce)                 -> prognoza z Yr / MET Norway
  - wikipedia(temat, jezyk)         -> krótkie streszczenie artykułu
Uruchomienie:  python server.py [--host 0.0.0.0] [--port 8000]
Adres w aplikacji:  http://<IP-komputera>:8000/mcp
"""
import argparse
import time
from datetime import datetime
from urllib.parse import quote
from zoneinfo import ZoneInfo

import httpx
from mcp.server.fastmcp import FastMCP

UA = "skille-pl-mcp/0.1 github.com/AInacodzien/skille-pl"  # MET wymaga identyfikacji aplikacji
TZ = ZoneInfo("Europe/Oslo")
MAX_WIKI = 1200  # znaków, żeby nie zapchać kontekstu 4B

MIEJSCA = {
    "figgjo": (58.81, 5.79),
    "sandnes": (58.85, 5.74),
    "stavanger": (58.97, 5.73),
    "bryne": (58.74, 5.65),
    "oslo": (59.91, 10.75),
    "bergen": (60.39, 5.32),
}

SYMBOLE = {
    "clearsky": "bezchmurnie",
    "fair": "prawie bezchmurnie",
    "partlycloudy": "częściowe zachmurzenie",
    "cloudy": "pochmurno",
    "fog": "mgła",
    "lightrain": "słaby deszcz",
    "rain": "deszcz",
    "heavyrain": "silny deszcz",
    "lightrainshowers": "przelotny słaby deszcz",
    "rainshowers": "przelotny deszcz",
    "heavyrainshowers": "przelotny silny deszcz",
    "lightsleet": "słaby deszcz ze śniegiem",
    "sleet": "deszcz ze śniegiem",
    "heavysleet": "silny deszcz ze śniegiem",
    "lightsnow": "słaby śnieg",
    "snow": "śnieg",
    "heavysnow": "silny śnieg",
    "lightsnowshowers": "przelotny słaby śnieg",
    "snowshowers": "przelotny śnieg",
    "heavysnowshowers": "przelotny silny śnieg",
    "rainandthunder": "deszcz z burzą",
    "heavyrainandthunder": "silny deszcz z burzą",
    "lightrainandthunder": "słaby deszcz z burzą",
    "snowandthunder": "śnieg z burzą",
    "sleetandthunder": "deszcz ze śniegiem i burza",
}

mcp = FastMCP("yr-figgjo")
_cache: dict[str, tuple[float, object]] = {}


def fetch_json(url: str, params: dict | None = None, ttl: int = 600):
    """GET z prostym cache (MET prosi, by nie pytać zbyt często)."""
    key = url + "?" + str(sorted((params or {}).items()))
    now = time.time()
    if key in _cache and now - _cache[key][0] < ttl:
        return _cache[key][1]
    r = httpx.get(url, params=params, headers={"User-Agent": UA}, timeout=15, follow_redirects=True)
    r.raise_for_status()
    data = r.json()
    _cache[key] = (now, data)
    return data


def opis(symbol: str | None) -> str:
    if not symbol:
        return "brak danych"
    return SYMBOLE.get(symbol.split("_")[0], symbol)


def lokalny(czas_iso: str) -> datetime:
    return datetime.fromisoformat(czas_iso.replace("Z", "+00:00")).astimezone(TZ)


@mcp.tool()
def pogoda(miejsce: str = "Figgjo") -> str:
    """Prognoza pogody z Yr na najbliższą dobę. Miejsca: Figgjo, Sandnes, Stavanger, Bryne, Oslo, Bergen."""
    klucz = miejsce.strip().lower()
    if klucz not in MIEJSCA:
        return "Nieznane miejsce. Dostępne: " + ", ".join(m.capitalize() for m in MIEJSCA)
    lat, lon = MIEJSCA[klucz]
    try:
        dane = fetch_json(
            "https://api.met.no/weatherapi/locationforecast/2.0/compact",
            {"lat": lat, "lon": lon},
        )
    except Exception as e:  # noqa: BLE001
        return f"Nie udało się pobrać pogody z Yr ({type(e).__name__})."
    serie = dane["properties"]["timeseries"]
    teraz = serie[0]
    d = teraz["data"]["instant"]["details"]
    h1 = teraz["data"].get("next_1_hours", {})
    linie = [
        f"{miejsce.capitalize()}, teraz ({lokalny(teraz['time']):%H:%M}): "
        f"{d['air_temperature']:.0f}°C, {opis(h1.get('summary', {}).get('symbol_code'))}, "
        f"wiatr {d['wind_speed']:.0f} m/s."
    ]
    ostatni = lokalny(teraz["time"])
    bloki = 0
    for wpis in serie[1:]:
        t = lokalny(wpis["time"])
        n6 = wpis["data"].get("next_6_hours")
        if not n6 or (t - ostatni).total_seconds() < 6 * 3600:
            continue
        det = n6.get("details", {})
        opad = det.get("precipitation_amount", 0)
        linie.append(
            f"Od {t:%d.%m %H:%M}: {opis(n6['summary']['symbol_code'])}, "
            f"{det.get('air_temperature_min', 0):.0f} do {det.get('air_temperature_max', 0):.0f}°C, "
            f"opad {opad:.1f} mm."
        )
        ostatni = t
        bloki += 1
        if bloki == 4:
            break
    linie.append("Źródło: Yr / MET Norway.")
    return "\n".join(linie)


@mcp.tool()
def wikipedia(temat: str, jezyk: str = "pl") -> str:
    """Krótkie streszczenie artykułu z Wikipedii. jezyk: pl, no, en."""
    if jezyk not in ("pl", "no", "en"):
        jezyk = "pl"
    url = f"https://{jezyk}.wikipedia.org/api/rest_v1/page/summary/{quote(temat.strip().replace(' ', '_'))}"
    try:
        dane = fetch_json(url, ttl=3600)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Nie znaleziono artykułu '{temat}' w Wikipedii ({jezyk})."
        return f"Błąd Wikipedii: {e.response.status_code}."
    except Exception as e:  # noqa: BLE001
        return f"Nie udało się pobrać Wikipedii ({type(e).__name__})."
    tekst = (dane.get("extract") or "").strip()
    if not tekst:
        return f"Artykuł '{temat}' nie ma streszczenia."
    if len(tekst) > MAX_WIKI:
        tekst = tekst[:MAX_WIKI].rsplit(" ", 1)[0] + "…"
    return f"{dane.get('title', temat)} (Wikipedia, {jezyk}): {tekst}"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    mcp.settings.host = a.host
    mcp.settings.port = a.port
    mcp.run(transport="streamable-http")
