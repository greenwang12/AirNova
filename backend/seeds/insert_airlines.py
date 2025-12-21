from sqlmodel import Session, select
from backend.db import engine
from backend.model import Company

airlines = [
    ("IndiGo","Domestic","India's largest airline","https://logo.clearbit.com/goindigo.in"),
    ("Air India","International","Flag carrier of India","https://logo.clearbit.com/airindia.com"),
    ("Vistara","Domestic","TATA + SIA JV","https://logo.clearbit.com/airvistara.com"),
    ("AirAsia India","Domestic","Low cost","https://logo.clearbit.com/airasia.com"),
    ("SpiceJet","Domestic","Budget airline","https://logo.clearbit.com/spicejet.com"),
    ("Go First","Domestic","Low cost","https://logo.clearbit.com/flygofirst.com"),
    ("Akasa Air","Domestic","New airline","https://logo.clearbit.com/akasaair.com"),
    ("Emirates","International","UAE flag carrier","https://logo.clearbit.com/emirates.com"),
    ("Qatar Airways","International","Qatar carrier","https://logo.clearbit.com/qatarairways.com"),
    ("Singapore Airlines","International","Premium airline","https://logo.clearbit.com/singaporeair.com"),
    ("British Airways","International","UK carrier","https://logo.clearbit.com/britishairways.com"),
    ("Lufthansa","International","Germany airline","https://logo.clearbit.com/lufthansa.com"),
]

with Session(engine) as s:
    for n,t,h,l in airlines:
        if s.exec(select(Company).where(Company.Name==n)).first():
            continue
        s.add(Company(Name=n,Type=t,History=h,Logo_URL=l))
    s.commit()

print("Companies seeded")
