import os
import requests
from datetime import datetime
from typing import Dict
from sqlmodel import Session, select
from ..model import Notification, Flight


# 🔑 IMPORTANT: this loads .env
from backend.config import SECRET_KEY  

from ..model import Notification, Flight
from dotenv import load_dotenv
load_dotenv()   # 🔥 THIS FIXES EVERYTHING

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
print("WEATHER KEY LOADED:", bool(OPENWEATHER_KEY))

# Airport → lat/lon
AIRPORTS = {
    "DEL": (28.5562, 77.1000),
    "BOM": (19.0896, 72.8656),
    "BLR": (13.1986, 77.7066),
    "MAA": (12.9941, 80.1709),
}

def fetch_weather_for_airport(iata: str) -> Dict:
    if not OPENWEATHER_KEY:
        return {"summary": "API key missing", "severe": False}

    if iata not in AIRPORTS:
        return {"summary": "Unknown airport", "severe": False}

    lat, lon = AIRPORTS[iata]

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_KEY,
        "units": "metric"
    }

    try:
        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
    except Exception:
        return {"summary": "Weather unavailable", "severe": False}

    data = r.json()
    now = datetime.utcnow()

    forecast = min(
        data["list"],
        key=lambda x: abs(datetime.fromtimestamp(x["dt"]) - now)
    )

    rain = forecast.get("rain", {}).get("3h", 0)
    wind = forecast["wind"]["speed"] * 3.6  # km/h
    visibility = forecast.get("visibility", 10000)
    main = forecast["weather"][0]["main"].lower()

    severe = (
        rain > 2 or
        wind > 25 or
        visibility < 1000 or
        "storm" in main or "thunder" in main
    )

    return {
        "summary": forecast["weather"][0]["description"],
        "temp": forecast["main"]["temp"],
        "rain": rain,
        "wind": round(wind, 2),
        "visibility": visibility,
        "storm": "storm" in main or "thunder" in main,
        "severe": severe
    }


class WeatherService:
    @staticmethod
    def check_upcoming_flights(session: Session):
        flights = session.exec(select(Flight)).all()
        created = []

        for f in flights:
            dept = fetch_weather_for_airport(f.Dept_Location)
            arr = fetch_weather_for_airport(f.Arr_Location)

            if dept.get("severe") or arr.get("severe"):
                note = Notification(
                    Customer_ID=0,
                    Kind="disruption",
                    Payload={
                        "flight_id": f.Flight_ID,
                        "reason": "weather",
                        "detail": {"dept": dept, "arr": arr}
                    },
                    Sent=False,
                    Created_At=datetime.utcnow()
                )
                session.add(note)
                created.append(note)

        if created:
            session.commit()
            for n in created:
                session.refresh(n)

        return created
