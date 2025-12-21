from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from typing import List

from ..db import get_session
from ..model import Flight, Company, FlightStatus
from ..services.price_alerts import PriceAlertsService   

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post("/add", response_model=Flight)
def add_flight(flight: Flight, session: Session = Depends(get_session)):
    data = flight.dict(exclude_unset=True)
    data.pop("Flight_ID", None)

    for k in ("Departure_Time", "Arrival_Time"):
        v = data.get(k)
        if isinstance(v, str):
            try:
                data[k] = datetime.fromisoformat(v.replace("Z", "+00:00"))
            except Exception:
                raise HTTPException(status_code=400, detail=f"Invalid datetime for {k}")

    st = data.get("Status")
    if isinstance(st, str):
        try:
            data["Status"] = FlightStatus(st)
        except ValueError:
            name = st.strip().upper()
            for member in FlightStatus:
                if member.name == name:
                    data["Status"] = member
                    break
            else:
                raise HTTPException(status_code=400, detail="Invalid Status enum")

    comp_id = data.get("Company_ID")
    if comp_id is not None and session.get(Company, comp_id) is None:
        raise HTTPException(status_code=400, detail="Invalid Company_ID")

    new = Flight(**data)
    session.add(new)
    session.commit()
    session.refresh(new)
    return new


@router.get("/all", response_model=List[Flight])
def list_flights(session: Session = Depends(get_session)):
    return session.exec(select(Flight)).all()


@router.get("/search", response_model=List[Flight])
def search_flights(
    depart: str | None = None,
    arrive: str | None = None,
    session: Session = Depends(get_session),
):
    q = select(Flight)

    if depart:
        q = q.where(Flight.Dept_Location == depart)
    if arrive:
        q = q.where(Flight.Arr_Location == arrive)

    flights = session.exec(q).all()

    # 🔔 PRICE ALERT TRIGGER (CORRECT PLACE)
    for f in flights:
        route = f"{f.Dept_Location}-{f.Arr_Location}"
        PriceAlertsService.check_alerts_for_route(
            session,
            route=route,
            current_price=f.Price_Per_Seat,
        )

    return flights

@router.get("/{flight_id}", response_model=Flight)
def get_flight(
    flight_id: int,
    session: Session = Depends(get_session),
):
    flight = session.get(Flight, flight_id)
    if not flight:
        raise HTTPException(404, "Flight not found")
    return flight
