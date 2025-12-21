import random
from datetime import timedelta
from sqlmodel import Session, select
from backend.db import engine
from backend.model import Payment, Booking, Flight, Company

# -----------------------------
# Payment settings
# -----------------------------
CARD_BRANDS = ["Visa", "Mastercard", "Amex"]
PAYMENT_TYPES = ["Card", "UPI", "NetBanking"]

# -----------------------------
# Start session
# -----------------------------
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

        # -----------------------------
        # Calculate realistic payment amounts
        # -----------------------------
        base_amount = flight.Price_Per_Seat * b.Seats
        surge_multiplier = random.uniform(0.9, 1.15)  # simulate demand variations
        base_amount = round(base_amount * surge_multiplier, 2)
        tax = round(base_amount * 0.05, 2)            # 5% GST
        total_amount = round(base_amount + tax, 2)

        # Payment timestamp shortly after booking
        paid_at = b.Created_At + timedelta(minutes=random.randint(2, 30))

        # Random payment type
        payment_type = random.choice(PAYMENT_TYPES)

        # -----------------------------
        # Create payment record
        # -----------------------------
        payment = Payment(
            Customer_ID=b.Customer_ID,
            Booking_ID=b.Booking_ID,  # ✅ include Booking_ID to avoid NULL error
            Company_ID=company.Company_ID,
            Amount=total_amount,
            Tax=tax,
            Payment_Date=paid_at,
            Payment_Type=payment_type,
            Card_Last4=str(random.randint(1000, 9999)) if payment_type == "Card" else None,
            Card_Brand=random.choice(CARD_BRANDS) if payment_type == "Card" else None,
            Gateway_Provider=random.choice(["Razorpay", "Stripe", "PayU"]),
            Gateway_Txn_ID=f"{company.Name[:2].upper()}{random.randint(100000000, 999999999)}",
            Captured_At=paid_at,
            Status="captured",
        )

        session.add(payment)

    session.commit()

print("✅ Payments seeded successfully")
