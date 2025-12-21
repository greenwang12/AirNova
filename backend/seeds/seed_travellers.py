import random
from sqlmodel import Session, select
from backend.db import engine
from backend.model import Traveller, Booking

# -----------------------------
# Random name and gender lists
# -----------------------------
FIRST_NAMES = ["Alex", "John", "Priya", "Amit", "Sara", "Rohan", "Anjali", "Michael", "Emily", "Arjun"]
LAST_NAMES = ["Sharma", "Patel", "Singh", "Kumar", "Verma", "Mehta", "Gupta", "Smith", "Doe", "Johnson"]
GENDERS = ["M", "F"]

# -----------------------------
# Start session
# -----------------------------
with Session(engine) as session:
    bookings = session.exec(select(Booking)).all()

    if not bookings:
        print("Error: Seed bookings first!")
        exit()

    for b in bookings:
        for i in range(b.Seats):
            full_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            age = random.randint(18, 60)
            gender = random.choice(GENDERS)

            traveller = Traveller(
                Booking_ID=b.Booking_ID,
                Full_Name=full_name,
                Age=age,
                Gender=gender
            )
            session.add(traveller)

    session.commit()

print("✅ Travellers seeded successfully")
