# backend/services/booking_service.py
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Optional
from .payment_service import PaymentService
from ..model import Payment, Flight
from datetime import datetime

class BookingService:
    @staticmethod
    def create_razorpay_order(session: Session, customer_id: int, flight_id: int, seats: int = 1, currency: str = "INR", idempotency_key: Optional[str] = None) -> Dict:
        if seats < 1:
            raise ValueError("seats must be >= 1")

        flight = session.get(Flight, flight_id)
        if not flight:
            raise ValueError("flight not found")
        if flight.F_Seats < seats:
            raise ValueError("not enough seats available")

        # TODO: replace price_per_seat with real flight price
        price_per_seat = 1000.00   # ₹1000
        total_amount_paise = int(price_per_seat * seats * 100)  # paise

        notes = {"customer_id": str(customer_id), "flight_id": str(flight_id), "seats": str(seats)}
        order = PaymentService.create_order(total_amount_paise, currency=currency, notes=notes)

        # Create a pending local payment record linking the order_id
        pay = Payment(
            Payment_Customer_ID=customer_id,
            Payment_Cost=total_amount_paise / 100.0,
            Payment_Tax=0.0,
            Payment_Date=datetime.utcnow().date(),
            Payment_Type="razorpay_order",
            Payment_Card_No=None,
            F_Company=flight.F_Company,
            gateway_provider="razorpay",
            gateway_txn_id=order["order_id"],
            status="created",
            idempotency_key=idempotency_key
        )
        try:
            session.add(pay)
            session.commit()
            session.refresh(pay)
        except SQLAlchemyError:
            session.rollback()
            raise

        return {"order_id": order["order_id"], "amount": order["amount"], "currency": order["currency"], "payment_id": pay.Payment_ID}

    @staticmethod
    def finalize_on_payment_captured(session: Session, razorpay_payment_id: str, razorpay_order_id: str):
        # fetch local payment by order id
        stmt = select(Payment).where(Payment.gateway_txn_id == razorpay_order_id)
        payment = session.exec(stmt).first()
        if not payment:
            raise ValueError("local payment record not found")

        # fetch payment details from Razorpay (optional)
        rp_payment = PaymentService.fetch_payment(razorpay_payment_id)

        # read metadata from local payment or from rp_payment['notes'] if used
        # decrement seats using metadata stored earlier in order notes
        flight_id = None
        seats = 1
        try:
            if "flight_id" in rp_payment.get("notes", {}):
                flight_id = int(rp_payment["notes"]["flight_id"])
                seats = int(rp_payment["notes"].get("seats", 1))
        except Exception:
            pass

        if flight_id is None:
            # try reading from local payment.F_Company mapping (best-effort)
            raise ValueError("flight_id not present in payment notes")

        flight = session.get(Flight, flight_id)
        if not flight:
            raise ValueError("flight not found")

        try:
            payment.status = "captured"
            payment.gateway_txn_id = razorpay_payment_id  # store payment id
            payment.last4 = None
            payment.card_brand = rp_payment.get("method")  # rough
            payment.captured_at = datetime.utcnow()
            session.add(payment)

            flight.F_Seats -= seats
            session.add(flight)

            session.commit()
            session.refresh(payment)
            return payment
        except SQLAlchemyError:
            session.rollback()
            raise
