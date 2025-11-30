import random
from datetime import datetime
from sqlmodel import Session, select
from backend.db import engine
from backend.model import Booking, Customer, Flight, BookingStatus

with Session(engine) as session:
    users = session.exec(select(Customer)).all()
    flights = session.exec(select(Flight)).all()

    if not users or not flights:
        print("Error: Seed users + flights first!")
        exit()

    bookings_to_create = 50

    for _ in range(bookings_to_create):
        user = random.choice(users)
        flight = random.choice(flights)
        seats = random.choice([1, 1, 2])  # 70% 1 seat, 30% 2 seats

        booking = Booking(
            Customer_ID=user.Customer_ID,
            Flight_ID=flight.Flight_ID,
            Seats=seats,
            Status=BookingStatus.CONFIRMED,
            Created_At=datetime.utcnow()
        )
        session.add(booking)

    session.commit()

print("Inserted 50 bookings.")
