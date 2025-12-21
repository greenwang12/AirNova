from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from backend.db import get_session
from backend.model import Flight

router = APIRouter()

@router.get("/price-signal")
def price_signal(session: Session = Depends(get_session)):
    row = session.exec(
        select(
            Flight.Dept_Location,
            Flight.Arr_Location,
            func.avg(Flight.Price_Per_Seat).label("avg_price")
        )
        .group_by(Flight.Dept_Location, Flight.Arr_Location)
        .order_by(func.avg(Flight.Price_Per_Seat))
        .limit(1)
    ).first()

    if not row:
        return {"message": "Price trend unavailable"}

    return {
        "message": f"Lowest average fare: {row.Dept_Location} → {row.Arr_Location}"
    }
