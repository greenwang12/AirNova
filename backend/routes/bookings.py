# backend/routes/bookings.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session
from ..db import get_session
from ..services.booking_service import BookingService
from ..services.payment_service import PaymentService
from ..config import RAZORPAY_WEBHOOK_SECRET
import json

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/create-order")
def create_order(customer_id: int, flight_id: int, seats: int = 1, session: Session = Depends(get_session)):
    try:
        data = BookingService.create_razorpay_order(session, customer_id, flight_id, seats)
        # return order id and amount; front-end should call Razorpay Checkout with key_id and order_id
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def razorpay_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    if not PaymentService.verify_webhook_signature(body, signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event = json.loads(body)
    # handle payment captured event
    # Razorpay event type for successful payment: "payment.captured"
    if event.get("event") == "payment.captured":
        payload = event.get("payload", {})
        payment_obj = payload.get("payment", {}).get("entity", {})
        razorpay_payment_id = payment_obj.get("id")
        razorpay_order_id = payment_obj.get("order_id")
        # finalize booking in DB
        from sqlmodel import Session
        from ..db import engine
        with Session(engine) as session:
            try:
                BookingService.finalize_on_payment_captured(session, razorpay_payment_id, razorpay_order_id)
            except Exception as e:
                # log and return 200 so Razorpay will not retry too aggressively (but you can return 500 to signal retry)
                print("Finalize error:", e)
    # Always return 200
    return {"status": "received"}
