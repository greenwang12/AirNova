# backend/routes/bookings.py

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session
from ..db import get_session
from ..services.booking_service import BookingService
from ..services.payment_service import PaymentService
from ..config import RAZORPAY_WEBHOOK_SECRET, USE_FAKE_PAYMENTS
import json
import traceback
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/bookings", tags=["bookings"])


# ---------------------------------------
# WEBHOOK BODY MODEL (for Fake + Swagger)
# ---------------------------------------
class FakeWebhook(BaseModel):
    event: str
    payload: dict


# ----------------------------------------------------
# CREATE ORDER (User → Backend → Razorpay / Fake Mode)
# ----------------------------------------------------
@router.post("/create-order")
def create_order(
    customer_id: int,
    flight_id: int,
    seats: int = 1,
    session: Session = Depends(get_session),
):
    try:
        result = BookingService.create_razorpay_order(
            session=session,
            customer_id=customer_id,
            flight_id=flight_id,
            seats=seats,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------
# WEBHOOK (Fake Mode OR Real Razorpay)
# ----------------------------------------------------
@router.post("/webhook")
async def razorpay_webhook(
    data: FakeWebhook,
    x_razorpay_signature: Optional[str] = Header(None),
    session: Session = Depends(get_session),
):
    """
    Receives payment.captured.
    In fake mode → signature is ignored.
    """

    body_dict = data.dict()
    body_bytes = json.dumps(body_dict).encode("utf-8")
    signature = x_razorpay_signature or ""

    # -----------------------------------
    # SIGNATURE CHECK IN REAL MODE ONLY
    # -----------------------------------
    if not USE_FAKE_PAYMENTS:
        valid = PaymentService.verify_webhook_signature(
            body=body_bytes,
            signature=signature,
            secret=RAZORPAY_WEBHOOK_SECRET
        )
        if not valid:
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

    # -----------------------------------
    # HANDLE EVENT TYPE
    # -----------------------------------
    event_type = body_dict.get("event")

    if event_type == "payment.captured":
        payment_entity = (
            body_dict.get("payload", {})
            .get("payment", {})
            .get("entity", {})
        )

        razorpay_payment_id = payment_entity.get("id")
        razorpay_order_id = payment_entity.get("order_id")

        try:
            BookingService.finalize_on_payment_captured(
                session=session,
                payment_id=razorpay_payment_id,
                order_id=razorpay_order_id,
            )
        except Exception as e:
            traceback.print_exc()
            print("Finalize error:", e)

    # -----------------------------------
    # ALWAYS ACKNOWLEDGE WEBHOOK
    # -----------------------------------
    return {"status": "received"}
