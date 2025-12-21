from sqlmodel import Session, select
from backend.db import engine
from backend.model import Company

airlines = [
    (1, "IndiGo", "Domestic", "India’s largest airline", "https://logo.clearbit.com/goindigo.in"),
    (2, "Air India", "International", "Flag carrier of India", "https://logo.clearbit.com/airindia.com"),
    (3, "Vistara", "Domestic", "TATA + Singapore Airlines JV", "https://logo.clearbit.com/airvistara.com"),
    (4, "SpiceJet", "Domestic", "Budget airline", "https://logo.clearbit.com/spicejet.com"),
    (5, "Akasa Air", "Domestic", "New low-cost airline", "https://logo.clearbit.com/akasaair.com"),
    (6, "Emirates", "International", "UAE flag carrier", "https://logo.clearbit.com/emirates.com"),
    (7, "Qatar Airways", "International", "Qatar flag carrier", "https://logo.clearbit.com/qatarairways.com"),
    (8, "Singapore Airlines", "International", "Premium airline", "https://logo.clearbit.com/singaporeair.com"),
    (9, "British Airways", "International", "UK flag carrier", "https://logo.clearbit.com/britishairways.com"),
    (10, "Lufthansa", "International", "Germany flag carrier", "https://logo.clearbit.com/lufthansa.com"),
    (11, "American Airlines", "International", "Major US airline", "https://logo.clearbit.com/aa.com"),
    (12, "Caribbean Airlines", "International", "Trinidad & Tobago flag carrier", "https://logo.clearbit.com/caribbean-airlines.com"),
    (13, "Gulf Air", "International", "Flag carrier of Bahrain", "https://logo.clearbit.com/gulfair.com"),
    
]

with Session(engine) as session:
    for cid, name, typ, hist, logo in airlines:
        exists = session.exec(
            select(Company).where(Company.Company_ID == cid)
        ).first()
        if exists:
            continue

        session.add(
            Company(
                Company_ID=cid,
                Name=name,
                Type=typ,
                History=hist,
                Logo_URL=logo,
            )
        )

    session.commit()

print("✅ Companies inserted correctly")
