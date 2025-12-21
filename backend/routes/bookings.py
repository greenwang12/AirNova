from fastapi import APIRouter, Depends, HTTPException, Header, Body
from sqlmodel import Session, select
from typing import Optional
import json
from datetime import datetime, timedelta
from pydantic import BaseModel

from backend.db import get_session
from backend.model import Booking, Flight, BookingStatus
from backend.routes.auth_dependency import get_current_user, security
from backend.services.booking_service import BookingService
from backend.services.payment_service import PaymentService
from backend.config import RAZORPAY_WEBHOOK_SECRET, USE_FAKE_PAYMENTS

router = APIRouter(prefix="/bookings", tags=["Bookings"])


# =========================
# BODY MODELS
# =========================
class CreateBookingIn(BaseModel):
    flight_id: int
    seats: int = 1


class FakeWebhook(BaseModel):
    event: str
    payload: dict


# =========================
# CREATE BOOKING + ORDER
# =========================
@router.post("", dependencies=[Depends(security)])
def create_booking(
    body: CreateBookingIn = Body(...),
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    flight = session.get(Flight, body.flight_id)
    if not flight:
        raise HTTPException(404, "Flight not found")

    result = BookingService.create_razorpay_order(
        session=session,
        customer_id=user["user_id"],
        flight_id=body.flight_id,
        seats=body.seats,
    )

    return {
        "booking_id": result["booking_id"],
        "order_id": result["order_id"],
        "amount": result["amount"],
        "currency": result["currency"],
    }


# =========================
# GET MY BOOKINGS
# =========================
@router.get("/my", dependencies=[Depends(security)])
def my_bookings(
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    rows = session.exec(
        select(Booking, Flight)
        .join(Flight, Flight.Flight_ID == Booking.Flight_ID)
        .where(Booking.Customer_ID == user["user_id"])
    ).all()

    return [
        {
            "booking": booking,
            "flight": flight
        }
        for booking, flight in rows
    ]


# =========================
# CANCEL BOOKING (24H RULE)
# =========================
@router.post("/{booking_id}/cancel", dependencies=[Depends(security)])
def cancel_booking(
    booking_id: int,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    booking = session.get(Booking, booking_id)
    if not booking or booking.Customer_ID != user["user_id"]:
        raise HTTPException(404, "Booking not found")

    if booking.Status == BookingStatus.CANCELLED:
        raise HTTPException(400, "Booking already cancelled")

    flight = session.get(Flight, booking.Flight_ID)
    if not flight:
        raise HTTPException(404, "Flight not found")

    # ❌ Block cancellation within 24 hours
    if flight.Departure_Time - datetime.utcnow() < timedelta(hours=24):
        raise HTTPException(
            400, "Cancellation not allowed within 24 hours of departure"
        )

    # ✅ Allow cancellation even if PAID
    booking.Status = BookingStatus.CANCELLED
    flight.Available_Seats += booking.Seats

    session.add(booking)
    session.add(flight)
    session.commit()

    return {
        "status": "cancelled",
        "booking_id": booking.Booking_ID
    }


# =========================
# RAZORPAY WEBHOOK
# =========================
@router.post("/webhook")
async def razorpay_webhook(
    data: FakeWebhook,
    x_razorpay_signature: Optional[str] = Header(None),
    session: Session = Depends(get_session),
):
    body = json.dumps(data.dict()).encode()

    if not USE_FAKE_PAYMENTS:
        valid = PaymentService.verify_webhook_signature(
            body=body,
            signature=x_razorpay_signature or "",
            secret=RAZORPAY_WEBHOOK_SECRET,
        )
        if not valid:
            raise HTTPException(400, "Invalid webhook signature")

    if data.event == "payment.captured":
        entity = data.payload["payment"]["entity"]
        BookingService.finalize_on_payment_captured(
            session=session,
            payment_id=entity["id"],
            order_id=entity["order_id"],
        )

    return {"status": "ok"}
