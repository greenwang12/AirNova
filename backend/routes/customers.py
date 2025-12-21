# backend/routes/customers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..model import Customer, Booking, Flight, Payment
from passlib.context import CryptContext
import hashlib

router = APIRouter(prefix="/customers", tags=["customers"])

# Same Argon2 settings as auth
pwd = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=8192,
    argon2__parallelism=1
)

# =========================
# HELPERS
# =========================
def is_hex_sha256(s: str) -> bool:
    if not s or len(s) != 64:
        return False
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


# =========================
# ADD CUSTOMER
# =========================
@router.post("/add")
def add_customer(customer: Customer, session: Session = Depends(get_session)):
    data = customer.dict(exclude_unset=True)
    data.pop("Customer_ID", None)

    raw = (data.get("Password") or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="Password required")

    # Preserve existing hashes
    if raw.startswith("$argon2") or raw.startswith("$2"):
        data["Password"] = raw
    elif is_hex_sha256(raw):
        data["Password"] = raw
    else:
        data["Password"] = pwd.hash(raw)

    new_customer = Customer(**data)
    session.add(new_customer)
    session.commit()
    session.refresh(new_customer)

    return new_customer


# =========================
# GET ALL CUSTOMERS
# =========================
@router.get("/all")
def get_all_customers(session: Session = Depends(get_session)):
    return session.exec(select(Customer)).all()


# =========================
# TRAVEL HISTORY (FIXED)
# =========================
@router.get("/{customer_id}/history")
def travel_history(customer_id: int, session: Session = Depends(get_session)):
    bookings = session.exec(
        select(Booking).where(Booking.Customer_ID == customer_id)
    ).all()

    history = []

    for b in bookings:
        flight = session.get(Flight, b.Flight_ID)

        payment = session.exec(
            select(Payment).where(Payment.Booking_ID == b.Booking_ID)
        ).first()

        history.append({
            "booking_id": b.Booking_ID,
            "route": f"{flight.Dept_Location} → {flight.Arr_Location}" if flight else None,
            "company": flight.company.Name if flight and flight.company else None,
            "departure": flight.Departure_Time if flight else None,
            "arrival": flight.Arrival_Time if flight else None,
            "seats": b.Seats,
            "status": b.Status,
            "payment_amount": payment.Amount if payment else None,
            "payment_status": payment.Status if payment else None,
            "booking_date": b.Created_At,
        })

    return history
