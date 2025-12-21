import os, requests
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")

# ✅ Aviation-safe fallback (small, correct)
IATA_COORDS = {
    "LHR": (51.4700, -0.4543),   # London Heathrow
    "JFK": (40.6413, -73.7781),
    "DEL": (28.5562, 77.1000),
    "BLR": (13.1986, 77.7066),
    "BOM": (19.0896, 72.8656),
    "DXB": (25.2532, 55.3657),
    "CDG": (49.0097, 2.5479),  # Paris Charles de Gaulle Airport
    "AMS": (52.3105, 4.7683),   # Amsterdam Schiphol

    # 🇰🇷 South Korea
    "ICN": (37.4602, 126.4407),  # Incheon
    "GMP": (37.5583, 126.7906),  # Gimpo
    "PUS": (35.1796, 128.9380),  # Busan
    # 🇸🇬 Singapore
    "SIN": (1.3644, 103.9915),   # Singapore Changi

    # 🇯🇵 Japan (Tokyo)
    "HND": (35.5494, 139.7798),  # Haneda
    "NRT": (35.7719, 140.3929),  # Narita

    # 🇹🇭 Thailand
    "BKK": (13.6900, 100.7501),  # Bangkok Suvarnabhumi
    "DMK": (13.9126, 100.6070),  # Don Mueang
    "HKT": (8.1132, 98.3169),    # Phuket

    # 🏴 Scotland
    "EDI": (55.9500, -3.3725),   # Edinburgh
    "GLA": (55.8719, -4.4331),   # Glasgow

    # 🇮🇪 Ireland
    "DUB": (53.4213, -6.2701),   # Dublin
    "SNN": (52.7019, -8.9248),   # Shannon

    # 🇨🇭 Switzerland
    "ZRH": (47.4581, 8.5555),    # Zurich
    "GVA": (46.2381, 6.1089),    # Geneva
}

def get_coords(iata: str):
    # 1️⃣ Try fallback first (guaranteed)
    if iata in IATA_COORDS:
        return IATA_COORDS[iata]

    # 2️⃣ Try OpenWeather geocoding
    r = requests.get(
        "https://api.openweathermap.org/geo/1.0/direct",
        params={
            "q": f"{iata} airport",
            "limit": 1,
            "appid": OPENWEATHER_KEY
        },
        timeout=5
    )
    data = r.json()
    if not data:
        return None
    return data[0]["lat"], data[0]["lon"]

def fetch_weather_for_airport(iata: str) -> Dict:
    iata = iata.upper()
    coords = get_coords(iata)

    if not coords:
        return {"summary": "Invalid airport", "severe": False}

    lat, lon = coords

    # CURRENT WEATHER
    curr = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_KEY,
            "units": "metric"
        },
        timeout=5
    ).json()

    # FORECAST
    fc = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params={
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_KEY,
            "units": "metric"
        },
        timeout=5
    ).json()

    now = datetime.utcnow()
    f = min(fc["list"], key=lambda x: abs(datetime.fromtimestamp(x["dt"]) - now))

    rain = f.get("rain", {}).get("3h", 0)
    wind = f["wind"]["speed"] * 3.6
    vis = f.get("visibility", 10000)
    main = f["weather"][0]["main"].lower()

    severe = (
        rain > 2 or wind > 25 or vis < 1000
        or "storm" in main or "thunder" in main
    )

    return {
        "summary": curr["weather"][0]["description"],
        "temp": curr["main"]["temp"],          # correct (≈11°C for LHR)
        "forecast_temp": f["main"]["temp"],
        "rain": rain,
        "wind": round(wind, 2),
        "visibility": vis,
        "storm": "storm" in main or "thunder" in main,
        "severe": severe
    }
