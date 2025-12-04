from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from typing import List

from ..db import get_session
from ..model import Flight, Company, FlightStatus

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post("/add", response_model=Flight)
def add_flight(flight: Flight, session: Session = Depends(get_session)):
    # use dict to avoid client-supplied id
    data = flight.dict(exclude_unset=True)
    data.pop("Flight_ID", None)

    # normalize datetimes (accept ISO strings)
    for k in ("Departure_Time", "Arrival_Time"):
        v = data.get(k)
        if isinstance(v, str):
            try:
                data[k] = datetime.fromisoformat(v.replace("Z", "+00:00"))
            except Exception:
                raise HTTPException(status_code=400, detail=f"Invalid datetime for {k}")

    # normalize status
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

    # company id exists?
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
def search_flights(depart: str | None = None, arrive: str | None = None, session: Session = Depends(get_session)):
    q = select(Flight)
    if depart:
        q = q.where(Flight.Dept_Location == depart)
    if arrive:
        q = q.where(Flight.Arr_Location == arrive)
    return session.exec(q).all()
