import random
from datetime import datetime
from sqlmodel import Session, select
from backend.db import engine
from backend.model import Payment, Booking, Company

with Session(engine) as session:
    bookings = session.exec(select(Booking)).all()
    companies = session.exec(select(Company)).all()

    if not bookings or not companies:
        print("Error: Seed bookings + flights + airlines first!")
        exit()

    for b in bookings:
        company = next((c for c in companies if c.Company_ID), None)
        amount = random.choice([3000, 4500, 5500, 7000, 9000])

        payment = Payment(
            Customer_ID=b.Customer_ID,
            Company_ID=company.Company_ID if company else None,
            Amount=amount,
            Tax=amount * 0.05,
            Payment_Date=datetime.utcnow(),
            Payment_Type="Card",
            Card_Last4=str(random.randint(1000, 9999)),
            Card_Brand=random.choice(["Visa", "Mastercard", "Amex"]),
            Gateway_Provider="TestSeeder",
            Gateway_Txn_ID=f"SEEDPAY{random.randint(10000,99999)}",
            Captured_At=datetime.utcnow(),
            Status="captured"
        )
        session.add(payment)

    session.commit()

print("Inserted payments for all bookings.")
