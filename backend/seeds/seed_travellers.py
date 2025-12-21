from sqlmodel import Session, select
from backend.db import engine
from backend.model import Traveller, Booking

with Session(engine) as session:
    bookings = session.exec(select(Booking)).all()

    if not bookings:
        print("Seed bookings first!")
        exit()

    for b in bookings:
        for i in range(b.Seats):
            session.add(Traveller(
                Booking_ID=b.Booking_ID,
                Full_Name=f"Passenger {i+1}",
                Age=25 + i,
                Gender="M"
            ))

    session.commit()

print("Travellers seeded")
