from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..db import get_session
from ..model import Flight

router = APIRouter(prefix="/flights", tags=["flights"])

@router.post("/add")
def add_flight(flight: Flight, session: Session = Depends(get_session)):
    session.add(flight)
    session.commit()
    session.refresh(flight)
    return flight

@router.get("/all")
def list_flights(session: Session = Depends(get_session)):
    return session.exec(select(Flight)).all()

@router.get("/search")
def search_flights(depart: str | None = None, arrive: str | None = None, session: Session = Depends(get_session)):
    q = select(Flight)
    if depart:
        q = q.where(Flight.F_Dept_Location == depart)
    if arrive:
        q = q.where(Flight.F_Arr_Location == arrive)
    return session.exec(q).all()
