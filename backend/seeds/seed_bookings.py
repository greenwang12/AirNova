import random
from datetime import datetime
from sqlmodel import Session, select
from backend.db import engine
from backend.model import Booking, Customer, Flight, BookingStatus

with Session(engine) as session:
    users = session.exec(select(Customer)).all()
    flights = session.exec(select(Flight)).all()

    if not users or not flights:
        print("Seed users + flights first!")
        exit()

    for _ in range(50):
        user = random.choice(users)
        flight = random.choice(flights)
        seats = random.choice([1, 1, 2])

        if flight.Available_Seats < seats:
            continue

        booking = Booking(
            Customer_ID=user.Customer_ID,
            Flight_ID=flight.Flight_ID,
            Seats=seats,
            Status=BookingStatus.CONFIRMED,
            Razorpay_Order_ID=f"order_{random.randint(100000,999999)}",
            Razorpay_Payment_ID=f"pay_{random.randint(100000,999999)}",
            Created_At=datetime.utcnow()
        )

        flight.Available_Seats -= seats

        session.add(booking)
        session.add(flight)

    session.commit()

print("Bookings seeded with Razorpay IDs")
