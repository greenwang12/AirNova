from fastapi import APIRouter, HTTPException, Depends
from backend.services.weather_service import fetch_weather_for_airport
from backend.routes.auth_dependency import get_current_user

router = APIRouter(
    prefix="/weather",
    tags=["Weather"],
)

def compute_risk(w: dict) -> float:
    risk = 0.0
    if w.get("rain", 0) > 2:
        risk += 0.3
    if w.get("wind", 0) > 25:
        risk += 0.3
    if w.get("visibility", 10000) < 1000:
        risk += 0.3
    if w.get("storm", False):
        risk += 0.6
    return min(risk, 1.0)

@router.get("/airport/{iata}")
def get_weather_by_airport(iata: str):
    iata = iata.upper()
    weather = fetch_weather_for_airport(iata)

    if "summary" not in weather:
        raise HTTPException(status_code=404, detail="Invalid airport code")

    risk = compute_risk(weather)

    return {
        "airport": iata,
        "weather": weather,
        "risk_score": risk,
        "status": "Risky" if risk > 0.6 else "Safe"
    }
