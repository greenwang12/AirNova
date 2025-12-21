from fastapi import APIRouter, HTTPException
from backend.services.weather_service import fetch_weather_for_airport

router = APIRouter(prefix="/weather", tags=["Weather"])


# ---------------------------
# Utility: risk computation
# ---------------------------
def compute_risk(w: dict) -> float:
    risk = 0.0

    if w.get("rain", 0) > 2:
        risk += 0.3
    if w.get("wind", 0) > 25:
        risk += 0.3
    if w.get("visibility", 10000) < 1000:
        risk += 0.3
    if w.get("storm"):
        risk += 0.6

    return min(risk, 1.0)


# ---------------------------
# Full airport weather (API)
# ---------------------------
@router.get("/airport/{iata}")
def get_weather_by_airport(iata: str):
    iata = iata.upper()
    weather = fetch_weather_for_airport(iata)

    if weather.get("summary") == "Invalid airport":
        raise HTTPException(status_code=404, detail="Invalid airport code")

    risk = compute_risk(weather)

    return {
        "airport": iata,
        "weather": weather,
        "risk_score": risk,
        "status": "Risky" if risk > 0.6 else "Safe"
    }


# ---------------------------
# Global ticker (before search)
# ---------------------------
@router.get("/signal/global")
def global_weather_signal():
    return {
        "message": "Global Aviation Weather · No Significant Disruptions Reported"
    }


# ---------------------------
# Airport ticker (after search)
# ---------------------------
@router.get("/signal")
def weather_signal(depart: str):
    iata = depart.upper()
    w = fetch_weather_for_airport(iata)

    if w.get("summary") == "Invalid airport":
        raise HTTPException(status_code=404, detail="Invalid airport code")

    status = "ADVERSE CONDITIONS" if w["severe"] else "FAVORABLE CONDITIONS"

    return {
        "message": f"{iata} · {w['summary'].title()} · {round(w['temp'])}°C · {status}"
    }
