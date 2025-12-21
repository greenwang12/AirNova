from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from pydantic import BaseModel

from backend.db import get_session
from backend.model import Traveller, Booking
from backend.routes.auth_dependency import get_current_user, security

router = APIRouter(prefix="/travellers", tags=["Travellers"])

class TravellerIn(BaseModel):
    full_name: str
    age: int
    gender: str

@router.post(
    "/add/{booking_id}",
    dependencies=[Depends(security)]
)
def add_travellers(
    booking_id: int,
    travellers: List[TravellerIn],
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    booking = session.get(Booking, booking_id)

    if not booking or booking.Customer_ID != user["user_id"]:
        raise HTTPException(404, "Booking not found")

    for t in travellers:
        session.add(
            Traveller(
                Booking_ID=booking_id,
                Full_Name=t.full_name,
                Age=t.age,
                Gender=t.gender,
            )
        )

    session.commit()
    return {"success": True}
