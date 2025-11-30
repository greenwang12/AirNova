from sqlmodel import Session
from backend.db import engine
from backend.model import Company

airlines = [
    ("IndiGo", "Domestic Airline", "India's largest airline by passengers."),
    ("Air India", "International Airline", "Flag carrier of India."),
    ("Vistara", "Domestic Airline", "TATA & Singapore Airlines JV."),
    ("AirAsia India", "Domestic Airline", "Low-cost carrier by AirAsia group."),
    ("SpiceJet", "Domestic Airline", "Popular Indian budget airline."),
    ("Go First", "Domestic Airline", "Low-cost airline."),
    ("Akasa Air", "Domestic Airline", "Newest Indian carrier."),
    ("Emirates", "International Airline", "UAE flag carrier."),
    ("Qatar Airways", "International Airline", "Qatar’s national carrier."),
    ("Singapore Airlines", "International Airline", "Premium full-service airline."),
    ("British Airways", "International Airline", "Flag carrier of the UK."),
    ("Lufthansa", "International Airline", "Germany's main airline."),
]

with Session(engine) as session:
    for name, t, hist in airlines:
        c = Company(Name=name, Type=t, History=hist)
        session.add(c)

    session.commit()
    print("Inserted airlines successfully!")
