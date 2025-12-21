import random
from datetime import datetime, timedelta
from sqlmodel import Session, select
from backend.db import engine
from backend.model import Payment, Booking, Flight, Company

CARD_BRANDS = [
    "Visa",
    "Mastercard",
    "Amex",
]

PAYMENT_TYPES = ["Card", "UPI", "NetBanking"]

with Session(engine) as session:
    bookings = session.exec(select(Booking)).all()

    if not bookings:
        print("Error: Seed bookings first!")
        exit()

    for b in bookings:
        flight = session.get(Flight, b.Flight_ID)
        company = session.get(Company, flight.Company_ID) if flight else None
        if not flight or not company:
            continue

        # 💰 realistic pricing
        base = flight.Price_Per_Seat * b.Seats
        surge = random.uniform(0.9, 1.15)              # demand variation
        base = round(base * surge, 2)

        tax = round(base * 0.05, 2)                     # 5% GST
        total = round(base + tax, 2)

        paid_at = b.Created_At + timedelta(
            minutes=random.randint(2, 30)
        )

        payment = Payment(
            Customer_ID=b.Customer_ID,
            Company_ID=company.Company_ID,
            Amount=total,
            Tax=tax,
            Payment_Date=paid_at,
            Payment_Type=random.choice(PAYMENT_TYPES),
            Card_Last4=str(random.randint(1000, 9999)),
            Card_Brand=random.choice(CARD_BRANDS),
            Gateway_Provider=random.choice(
                ["Razorpay", "Stripe", "PayU"]
            ),
            Gateway_Txn_ID=f"TXN{random.randint(100000000,999999999)}",
            Captured_At=paid_at,
            Status="captured",
        )

        session.add(payment)

    session.commit()

print("Inserted realistic payment data.")
