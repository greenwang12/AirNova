import random
from datetime import datetime, timedelta
from sqlmodel import Session
from backend.db import engine
from backend.model import Flight, FlightStatus

COMPANIES = {
    "IndiGo": 1,
    "Air India": 2,
    "Vistara": 3,
    "AirAsia India": 4,
    "SpiceJet": 5,
    "Go First": 6,
    "Akasa Air": 7,
    "Emirates": 8,
    "Qatar Airways": 9,
    "Singapore Airlines": 10,
    "British Airways": 11,
    "Lufthansa": 12,
}

# =========================
# EXTENDED ROUTE POOL
# =========================
ROUTES = [
    # 🇮🇳 INDIA
    ("DEL","BLR"),("BLR","DEL"),("DEL","BOM"),("BOM","DEL"),
    ("DEL","MAA"),("MAA","DEL"),("DEL","HYD"),("HYD","DEL"),
    ("DEL","CCU"),("CCU","DEL"),("DEL","GOA"),("GOA","DEL"),
    ("BOM","GOA"),("GOA","BOM"),("BLR","HYD"),("HYD","BLR"),
    ("MAA","COK"),("COK","MAA"),("BLR","COK"),("COK","BLR"),
    ("DEL","PNQ"),("PNQ","DEL"),("BOM","PNQ"),("PNQ","BOM"),
    ("DEL","JAI"),("JAI","DEL"),("DEL","LKO"),("LKO","DEL"),

    # 🌍 MIDDLE EAST
    ("DEL","DXB"),("DXB","DEL"),("BOM","DXB"),("DXB","BOM"),
    ("DEL","DOH"),("DOH","DEL"),("DEL","AUH"),("AUH","DEL"),
    ("MAA","DXB"),("DXB","MAA"),

    # 🌏 SOUTH EAST ASIA
    ("DEL","SIN"),("SIN","DEL"),("MAA","SIN"),("SIN","MAA"),
    ("BLR","SIN"),("SIN","BLR"),("DEL","BKK"),("BKK","DEL"),
    ("DEL","KUL"),("KUL","DEL"),("DEL","HKT"),("HKT","DEL"),

    # 🌏 EAST ASIA
    ("DEL","HKG"),("HKG","DEL"),("DEL","NRT"),("NRT","DEL"),
    ("DEL","ICN"),("ICN","DEL"),

    # 🌍 EUROPE
    ("DEL","LHR"),("LHR","DEL"),("BOM","LHR"),("LHR","BOM"),
    ("DEL","CDG"),("CDG","DEL"),("DEL","FRA"),("FRA","DEL"),
    ("DEL","AMS"),("AMS","DEL"),

    # 🌎 NORTH AMERICA
    ("DEL","JFK"),("JFK","DEL"),("DEL","SFO"),("SFO","DEL"),
    ("DEL","ORD"),("ORD","DEL"),("BOM","JFK"),("JFK","BOM"),
    ("DEL","YYZ"),("YYZ","DEL"),

    # 🌏 AUSTRALIA
    ("DEL","SYD"),("SYD","DEL"),("DEL","MEL"),("MEL","DEL"),
]

def pick_company(dept, arr):
    domestic = ("DEL","BLR","BOM","MAA","GOA","HYD","CCU","PNQ","COK","JAI","LKO")
    if dept in domestic and arr in domestic:
        return random.choice([1,3,4,5,6,7])
    return random.choice([2,8,9,10,11,12])

base_date = datetime.utcnow() + timedelta(days=7)

def estimate_duration(dept, arr):
    dom = {
        ("DEL","BLR"):120,("BLR","DEL"):120,
        ("DEL","BOM"):120,("BOM","DEL"):120,
        ("DEL","MAA"):150,("MAA","DEL"):150,
        ("DEL","HYD"):110,("HYD","DEL"):110,
    }
    return dom.get((dept,arr), random.randint(180, 900))

def random_times(duration):
    dep = base_date + timedelta(
        days=random.randint(0, 60),
        hours=random.randint(0, 23),
        minutes=random.choice([0,15,30,45])
    )
    return dep, dep + timedelta(minutes=duration)

def seat_count(dept, arr):
    if arr in ("LHR","JFK","SFO","CDG","SYD","MEL"):
        return random.choice([250,270,300])
    if arr in ("DXB","SIN","BKK","HKG","NRT","ICN"):
        return random.choice([200,220,240])
    return random.choice([150,180,200])

with Session(engine) as session:
    for _ in range(100):
        dept, arr = random.choice(ROUTES)
        duration = estimate_duration(dept, arr)
        depart, arrive = random_times(duration)
        seats = seat_count(dept, arr)

        flight = Flight(
            Company_ID=pick_company(dept, arr),
            Flight_Code=f"{dept}{arr}-{random.randint(100,999)}",
            Dept_Location=dept,
            Arr_Location=arr,
            Departure_Time=depart,
            Arrival_Time=arrive,
            Total_Seats=seats,
            Available_Seats=seats,
            Price_Per_Seat=random.randint(3500, 25000),
            Stops=0,
            Status=FlightStatus.ON_TIME,
        )

        session.add(flight)

    session.commit()

print("Inserted 100 flights safely.")
