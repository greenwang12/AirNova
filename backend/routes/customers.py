# backend/routes/customers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..model import Customer, Booking, Flight, Payment
from passlib.context import CryptContext
import hashlib

router = APIRouter(prefix="/customers", tags=["customers"])

# same Argon2 settings as auth (low memory ~8 MiB)
pwd = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=8192,
    argon2__parallelism=1
)

def is_hex_sha256(s: str) -> bool:
    if not s or len(s) != 64:
        return False
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

@router.post("/add")
def add_customer(customer: Customer, session: Session = Depends(get_session)):
    """
    Add a customer:
    - If provided password already looks like argon2/bcrypt/sha256, keep as-is.
    - Otherwise hash plaintext with Argon2 (pwd.hash).
    """
    raw = (customer.Password or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="Password required")

    # preserve existing hash formats
    if raw.startswith("$argon2") or raw.startswith("$2"):
        customer.Password = raw
    elif is_hex_sha256(raw):
        customer.Password = raw
    else:
        # plaintext -> hash with Argon2 (configured above)
        customer.Password = pwd.hash(raw)

    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer

@router.get("/all")
def get_all_customers(session: Session = Depends(get_session)):
    return session.exec(select(Customer)).all()

@router.get("/{customer_id}/history")
def travel_history(customer_id: int, session: Session = Depends(get_session)):
    # fetch bookings
    bookings = session.exec(select(Booking).where(Booking.Customer_ID == customer_id)).all()

    history = []
    # prefetch payments for this customer to match by date
    payments = session.exec(select(Payment).where(Payment.Customer_ID == customer_id)).all()

    for b in bookings:
        f = session.get(Flight, b.Flight_ID) if getattr(b, "Flight_ID", None) is not None else None

        # find a payment matching booking date (best-effort)
        p_match = None
        for pay in payments:
            pd = getattr(pay, "Payment_Date", None)
            if pd is None:
                continue
            pay_date = pd.date() if hasattr(pd, "date") else pd
            try:
                booking_date = b.Created_At.date() if hasattr(b.Created_At, "date") else b.Created_At
            except Exception:
                booking_date = None
            if booking_date and pay_date == booking_date:
                p_match = pay
                break

        history.append({
            "booking_id": getattr(b, "Booking_ID", None),
            "route": f"{getattr(f, 'Dept_Location', None)} → {getattr(f, 'Arr_Location', None)}" if f else None,
            "company": getattr(f.company, "Name", None) if f else None,
            "departure": getattr(f, "Departure_Time", None),
            "arrival": getattr(f, "Arrival_Time", None),
            "seats": getattr(b, "Seats", None),
            "status": getattr(b, "Status", None),
            "payment_amount": getattr(p_match, "Amount", None) if p_match else None,
            "payment_status": getattr(p_match, "Status", None) if p_match else None,
            "booking_date": getattr(b, "Created_At", None),
        })

    return history
