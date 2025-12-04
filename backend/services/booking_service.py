# backend/services/booking_service.py

from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Optional
from .payment_service import PaymentService
from ..model import Payment, Flight
from datetime import datetime
from ..config import USE_FAKE_PAYMENTS
import random
import string


# -------------------------------
# FAKE HELPERS
# -------------------------------
def _fake_card():
    brands = ["Visa", "Mastercard", "Amex", "RuPay"]
    brand = random.choice(brands)
    last4 = str(random.randint(1000, 9999))
    return last4, brand


def _fake_gateway():
    providers = [
        "VisaNet", "MasterSwitch", "AmexRoute",
        "RuPaySwitch", "PayFlex", "SwiftPay",
        "NetClear", "TestRail", "UniRoute"
    ]
    return "FakeGateway-" + random.choice(providers)


def _fake_upi():
    names = ["rahul", "avi", "demo", "airnova", "testuser", "payment"]
    handles = ["upi", "ybl", "okaxis", "oksbi", "okicici", "okhdfcbank"]
    return f"{random.choice(names)}@{random.choice(handles)}"


def _fake_reference():
    return "BRN" + "".join(random.choices(string.digits, k=9))


def _simulate_failure(prob=0.05):
    return random.random() < prob


# -------------------------------
# BOOKING SERVICE
# -------------------------------
class BookingService:

    @staticmethod
    def create_razorpay_order(
        session: Session,
        customer_id: int,
        flight_id: int,
        seats: int = 1,
        currency: str = "INR",
        idempotency_key: Optional[str] = None
    ) -> Dict:

        if seats < 1:
            raise ValueError("Seats must be >= 1")

        flight = session.get(Flight, flight_id)
        if not flight:
            raise ValueError("Flight not found")

        if flight.Seats < seats:
            raise ValueError("Not enough seats available")

        # Price logic
        price_per_seat = 1000.00
        total_amount_paise = int(price_per_seat * seats * 100)

        notes = {
            "customer_id": str(customer_id),
            "flight_id": str(flight_id),
            "seats": str(seats)
        }

        # Razorpay order (real or fake)
        order = PaymentService.create_order(
            amount_cents=total_amount_paise,
            currency=currency,
            notes=notes
        )

        # -------------------------------
        # FAKE PAYMENT DETAILS
        # -------------------------------
        if USE_FAKE_PAYMENTS:
            # 70% card, 30% UPI
            use_card = random.random() < 0.7

            if use_card:
                fake_last4, fake_brand = _fake_card()
                pay_type = "card"
            else:
                fake_last4, fake_brand = None, None
                pay_type = "UPI"

            fake_gateway = _fake_gateway()

        else:
            fake_last4 = None
            fake_brand = None
            fake_gateway = "razorpay"
            pay_type = "card"

        # -------------------------------
        # Create pending payment row
        # -------------------------------
        payment = Payment(
            Customer_ID=customer_id,
            Company_ID=flight.Company_ID,
            Amount=total_amount_paise / 100.0,
            Tax=0.0,
            Payment_Date=datetime.utcnow(),
            Payment_Type=pay_type,

            Card_Last4=fake_last4,
            Card_Brand=fake_brand,

            Gateway_Provider=fake_gateway,
            Gateway_Txn_ID=order["order_id"],

            Status="authorized" if USE_FAKE_PAYMENTS else "created",
            Idempotency_Key=idempotency_key
        )

        try:
            session.add(payment)
            session.commit()
            session.refresh(payment)
        except SQLAlchemyError:
            session.rollback()
            raise

        return {
            "order_id": order["order_id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "payment_id": payment.Payment_ID
        }

    # --------------------------------------------------------------------

    @staticmethod
    def finalize_on_payment_captured(
        session: Session,
        payment_id: str,
        order_id: str
    ):
        # Find payment using order ID
        stmt = select(Payment).where(Payment.Gateway_Txn_ID == order_id)
        payment = session.exec(stmt).first()

        if not payment:
            raise ValueError("Local payment record not found")

        # NOTE: pass order_id so fake mode can return the correct notes
        rp_data = PaymentService.fetch_payment(payment_id, order_id=order_id)
        notes = rp_data.get("notes", {})

        flight_id = int(notes.get("flight_id", 0))
        seats = int(notes.get("seats", 1))

        if not flight_id:
            raise ValueError("flight_id missing in payment notes")

        flight = session.get(Flight, flight_id)
        if not flight:
            raise ValueError("Flight not found")

        # -------------------------------
        # 5% FAILURE SIMULATION
        # -------------------------------
        if USE_FAKE_PAYMENTS and _simulate_failure():
            payment.Status = "failed"
            payment.Gateway_Txn_ID = payment_id
            payment.Captured_At = None

            session.add(payment)
            session.commit()
            return payment

        # -------------------------------
        # SUCCESS: CAPTURED
        # -------------------------------
        payment.Status = "captured"
        payment.Gateway_Txn_ID = payment_id
        payment.Captured_At = datetime.utcnow()

        # UPI flow
        if USE_FAKE_PAYMENTS and payment.Payment_Type == "UPI":
            payment.Card_Last4 = None
            payment.Card_Brand = "UPI"
            payment.Gateway_Provider = _fake_gateway()

        # Card flow
        else:
            # If missing, generate new realistic card details
            if not payment.Card_Last4 or not payment.Card_Brand:
                last4, brand = _fake_card()
                payment.Card_Last4 = last4
                payment.Card_Brand = brand

        # Deduct seats only on success
        flight.Seats -= seats

        try:
            session.add(payment)
            session.add(flight)
            session.commit()
            session.refresh(payment)
            return payment

        except SQLAlchemyError:
            session.rollback()
            raise
