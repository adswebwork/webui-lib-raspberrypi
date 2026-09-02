#!/usr/bin/env python3
"""Fetch outside temperature from OpenWeatherMap.

What it does
    Gets the current outdoor conditions, so a node can compare inside against
    outside - the difference is what tells you whether opening a window would
    help.

Hardware
    Any machine with internet access.

Wiring
    None.

Run on a Pi
    OWM_API_KEY=... python3 recipes/net/fetch_weather.py

Run on your Mac
    OWM_API_KEY=... python3 recipes/net/fetch_weather.py

Copy into a project
    The API key comes from the environment, never from the source. An earlier
    version of this repo committed credentials, which is why the key is read
    this way and why secrets/ is gitignored.

    Free-tier OpenWeatherMap rate-limits at 60 calls/minute; poll every few
    minutes, not every loop.

requires: (nothing)
"""
import json
import os
import urllib.parse
import urllib.request

# --- tunables -------------------------------------------------------------
CITY = "Norcross,GA,US"
UNITS = "imperial"       # "imperial" for F, "metric" for C
TIMEOUT_SECONDS = 10
API_URL = "https://api.openweathermap.org/data/2.5/weather"
# --------------------------------------------------------------------------


def fetch_weather(city=CITY, units=UNITS, api_key=None):
    """Return {"temp_f": ..., "humidity": ..., "description": ...}."""
    api_key = api_key or os.environ.get("OWM_API_KEY")
    if not api_key:
        raise RuntimeError(
            "set OWM_API_KEY - get a free key at openweathermap.org/api")

    url = "{}?{}".format(API_URL, urllib.parse.urlencode(
        {"q": city, "units": units, "appid": api_key}))
    with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
        data = json.load(response)

    return {
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
    }


if __name__ == "__main__":
    try:
        weather = fetch_weather()
        print("{description}, {temp} deg, {humidity}% humidity".format(**weather))
    except Exception as exc:
        raise SystemExit("could not fetch weather: {}".format(exc))
