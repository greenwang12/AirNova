from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.db import get_session
from backend.routes.auth_dependency import get_current_user, security
from backend.model import Booking, Payment

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

# =========================
# GET PAYMENT BY BOOKING
# =========================
@router.get(
    "/by-booking/{booking_id}",
    dependencies=[Depends(security)]
)
def get_payment_for_booking(
    booking_id: int,
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    booking = session.get(Booking, booking_id)

    if not booking or booking.Customer_ID != user["user_id"]:
        raise HTTPException(404, "Booking not found")

    payment = session.exec(
        select(Payment).where(Payment.Booking_ID == booking_id)
    ).first()

    if not payment:
        raise HTTPException(404, "Payment not found")

    return {
        "booking_id": booking.Booking_ID,
        "order_id": payment.Gateway_Txn_ID,
        "status": payment.Status,
        "amount": payment.Amount,
        "payment_id": payment.Gateway_Payment_ID,
    }
