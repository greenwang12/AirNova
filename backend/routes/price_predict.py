# backend/routes/price_predict.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ..services.price_predictor_ml import PricePredictorML
from ..db import get_session
from sqlmodel import Session
from ..model import Flight

router = APIRouter(prefix="/predict", tags=["predict"])

class PredictIn(BaseModel):
    route: str
    depart_date: str    # ISO date/time
    base_price: float
    historical_mean: float | None = None
    demand_index: float | None = 1.0
    flight_id: int | None = None

@router.post("/")
def predict_price(payload: PredictIn, session: Session = Depends(get_session)):
    # If flight_id provided, try to fill missing fields from DB
    if payload.flight_id:
        f = session.get(Flight, payload.flight_id)
        if not f:
            raise HTTPException(404, "flight not found")
        payload.route = f"{f.Dept_Location}-{f.Arr_Location}"
        # you can also read known base price if you store it
    predictor = PricePredictorML()
    res = predictor.predict(payload.route, payload.depart_date, payload.base_price, payload.historical_mean, payload.demand_index)
    return res
