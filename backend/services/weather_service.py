# backend/services/weather_service.py
from ..model import Notification, Flight
from sqlmodel import Session, select
from datetime import datetime
from typing import Dict

# Replace fetch_weather_for_airport with real API call
def fetch_weather_for_airport(iata: str) -> Dict:
    # placeholder: return safe weather. Integrate with OpenWeatherMap / Meteostat
    return {"iata": iata, "severe": False, "summary": "Clear skies"}

class WeatherService:
    @staticmethod
    def check_upcoming_flights(session: Session):
        # find flights in next 48h and check weather for origin+dest
        now = datetime.utcnow()
        later = now
        flights = session.exec(select(Flight)).all()
        created = []
        for f in flights:
            # simple example: check both airports
            w1 = fetch_weather_for_airport(f.Dept_Location)
            w2 = fetch_weather_for_airport(f.Arr_Location)
            if w1.get("severe") or w2.get("severe"):
                note = Notification(Customer_ID=0, Kind="disruption", Payload={"flight_id": f.Flight_ID, "reason": "weather", "detail": {"dept":w1,"arr":w2}}, Sent=False, Created_At=datetime.utcnow())
                session.add(note)
                created.append(note)
        if created:
            session.commit()
            for n in created: session.refresh(n)
        return created
