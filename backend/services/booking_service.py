from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Optional, List
from datetime import datetime
import random

from .payment_service import PaymentService
from ..model import Payment, Flight, Booking, BookingStatus
from ..config import USE_FAKE_PAYMENTS


# -------------------------------
# FAKE HELPERS
# -------------------------------
def _fake_gateway():
    providers = [
        "VisaNet", "MasterSwitch", "AmexRoute",
        "RuPaySwitch", "PayFlex", "SwiftPay",
        "NetClear", "TestRail", "UniRoute"
    ]
    return "FakeGateway-" + random.choice(providers)


def _simulate_failure(prob=0.05):
    return random.random() < prob


# -------------------------------
# BOOKING SERVICE
# -------------------------------
class BookingService:

    # ============================
    # CREATE BOOKING + ORDER
    # ============================
    @staticmethod
    def create_razorpay_order(
        session: Session,
        customer_id: int,
        flight_id: int,
        seats: int = 1,
        selected_seats: Optional[List[str]] = None,
        extra_baggage_kg: int = 0,
        currency: str = "INR",
        idempotency_key: Optional[str] = None
    ) -> Dict:

        if seats < 1:
            raise ValueError("Seats must be >= 1")

        flight = session.get(Flight, flight_id)
        if not flight:
            raise ValueError("Flight not found")

        if flight.Available_Seats < seats:
            raise ValueError("Not enough seats available")

        # ---------------------------
        # BASE PRICE
        # ---------------------------
        price_per_seat = float(flight.Price_Per_Seat)
        base_total = price_per_seat * seats

        # ---------------------------
        # SEAT PRICING
        # ---------------------------
        # ---------------------------
        seat_total = 0
        if selected_seats:
            for s in selected_seats:
                row = int(s[:-1])   # "12A" → 12
                col = s[-1]         # "A"
        # row-based pricing (0 for all, kept for future)
                if row < 5:
                    seat_total += flight.Seat_Pricing.get("high", 0)
                elif row < 15:
                    seat_total += flight.Seat_Pricing.get("low", 0)
                else:
                    seat_total += flight.Seat_Pricing.get("free", 0)

        # column-based pricing
                if col in ("A", "F"):
                    seat_total += 400
                elif col in ("C", "D"):
                    seat_total += 250


        # ---------------------------
        # BAGGAGE PRICING
        # ---------------------------
        baggage_total = max(0, extra_baggage_kg) * 300

        # ---------------------------
        # FINAL TOTAL
        # ---------------------------
        total_amount = base_total + seat_total + baggage_total
        total_amount_paise = int(total_amount * 100)

        # ---------------------------
        # CREATE BOOKING
        # ---------------------------
        booking = Booking(
            Customer_ID=customer_id,
            Flight_ID=flight_id,
            Seats=seats,
            Status=BookingStatus.CREATED
        )

        session.add(booking)
        session.commit()
        session.refresh(booking)

        # ---------------------------
        # CREATE PAYMENT ORDER
        # ---------------------------
        order = PaymentService.create_order(
            amount_paise=total_amount_paise,
            currency=currency,
            notes={
                "booking_id": str(booking.Booking_ID),
                "customer_id": str(customer_id),
                "flight_id": str(flight_id),
                "seats": str(seats)
            }
        )

        payment = Payment(
            Customer_ID=customer_id,
            Booking_ID=booking.Booking_ID,
            Company_ID=flight.Company_ID,
            Amount=total_amount,
            Tax=0.0,
            Gateway_Provider=_fake_gateway() if USE_FAKE_PAYMENTS else "razorpay",
            Gateway_Txn_ID=order["order_id"],
            Status="authorized" if USE_FAKE_PAYMENTS else "created",
            Created_At=datetime.utcnow()
        )

        booking.Razorpay_Order_ID = order["order_id"]

        try:
            session.add(payment)
            session.add(booking)
            session.commit()
            session.refresh(payment)
        except SQLAlchemyError:
            session.rollback()
            raise

        return {
            "booking_id": booking.Booking_ID,
            "order_id": order["order_id"],
            "amount": order["amount"],
            "currency": order["currency"]
        }

    # ============================
    # FINALIZE PAYMENT (WEBHOOK)
    # ============================
    @staticmethod
    def finalize_on_payment_captured(
        session: Session,
        payment_id: str,
        order_id: str
    ):
        stmt = select(Payment).where(Payment.Gateway_Txn_ID == order_id)
        payment = session.exec(stmt).first()

        if not payment:
            raise ValueError("Local payment record not found")

        if payment.Status == "captured":
            return payment

        booking = session.get(Booking, payment.Booking_ID)
        if not booking:
            raise ValueError("Booking not found")

        if booking.Status == BookingStatus.CANCELLED:
            return payment

        flight = session.get(Flight, booking.Flight_ID)
        if not flight:
            raise ValueError("Flight not found")

        if USE_FAKE_PAYMENTS and _simulate_failure():
            payment.Status = "failed"
            session.add(payment)
            session.commit()
            return payment

        payment.Status = "captured"
        payment.Gateway_Txn_ID = payment_id
        payment.Captured_At = datetime.utcnow()

        booking.Status = BookingStatus.PAID
        flight.Available_Seats -= booking.Seats

        try:
            session.add(payment)
            session.add(booking)
            session.add(flight)
            session.commit()
            session.refresh(payment)
            return payment
        except SQLAlchemyError:
            session.rollback()
            raise
