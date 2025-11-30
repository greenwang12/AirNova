# backend/seeds/seed_flights.py
import random
from datetime import datetime, timedelta
from sqlmodel import Session
from backend.db import engine
from backend.model import Flight

# Map of company IDs from your DB (from your output)
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

# route pool (domestic + international pairs)
ROUTES = [
    ("DEL","BLR"),("BLR","DEL"),("DEL","BOM"),("BOM","DEL"),("DEL","MAA"),
    ("MAA","DEL"),("DEL","GOA"),("GOA","DEL"),("HYD","DEL"),("DEL","HYD"),
    ("DEL","DXB"),("DEL","SIN"),("DEL","BKK"),("BOM","DXB"),("MAA","SIN"),
    ("DEL","LHR"),("BOM","LHR"),("DEL","CDG"),("DEL","JFK"),("DEL","SFO"),
]

# helper to pick a company suitable for route (prefer domestic carriers for domestic routes)
def pick_company(dept, arr):
    if dept in ("DEL","BLR","BOM","MAA","GOA","HYD"):
        # 70% domestic carriers, 30% international
        if random.random() < 0.7:
            return random.choice([COMPANIES["IndiGo"], COMPANIES["Vistara"], COMPANIES["SpiceJet"], COMPANIES["AirAsia India"], COMPANIES["Akasa Air"], COMPANIES["Go First"]])
        else:
            return random.choice([COMPANIES["Emirates"], COMPANIES["Qatar Airways"], COMPANIES["Singapore Airlines"], COMPANIES["British Airways"], COMPANIES["Lufthansa"], COMPANIES["Air India"]])
    else:
        # international origin -> pick an international carrier mostly
        return random.choice([COMPANIES["Emirates"], COMPANIES["Qatar Airways"], COMPANIES["Singapore Airlines"], COMPANIES["British Airways"], COMPANIES["Lufthansa"], COMPANIES["Air India"]])

def random_depart_arrival(duration_min):
    # helper to build ISO datetimes given depart and duration (minutes)
    dep = base_date + timedelta(days=random.randint(0,60), hours=random.randint(0,23), minutes=random.choice([0,15,30,45]))
    arr = dep + timedelta(minutes=duration_min)
    return dep, arr

# base start date for schedule
base_date = datetime.utcnow() + timedelta(days=7)  # start one week from today

def estimate_duration(dept, arr):
    # rough durations in minutes (domestic shorter)
    dom_pairs = {("DEL","BLR"):120,("BLR","DEL"):120,("DEL","BOM"):120,("BOM","DEL"):120,("DEL","MAA"):150,("MAA","DEL"):150,("DEL","GOA"):150,("GOA","DEL"):150,("HYD","DEL"):110,("DEL","HYD"):110}
    if (dept,arr) in dom_pairs:
        return dom_pairs[(dept,arr)]
    # international roughs
    if (dept,arr) == ("DEL","DXB"): return 210
    if (dept,arr) == ("BOM","DXB"): return 210
    if (dept,arr) == ("DEL","SIN"): return 360
    if (dept,arr) == ("MAA","SIN"): return 330
    if (dept,arr) == ("DEL","BKK"): return 270
    if (dept,arr) == ("DEL","LHR"): return 510
    if (dept,arr) == ("BOM","LHR"): return 540
    if (dept,arr) == ("DEL","CDG"): return 520
    if (dept,arr) == ("DEL","JFK"): return 900
    if (dept,arr) == ("DEL","SFO"): return 930
    # fallback
    return 180

def seat_count_for_route(dept,arr):
    # larger planes for international
    if dept in ("DEL","BOM") and arr in ("LHR","JFK","SFO","CDG"):
        return random.choice([250,270,300])
    if dept in ("DEL","BOM","MAA") and arr in ("DXB","SIN","BKK"):
        return random.choice([200,220,240])
    return random.choice([150,160,180,200])

# create 100 flights
flights = []
for i in range(100):
    dept, arr = random.choice(ROUTES)
    duration = estimate_duration(dept, arr)
    depart, arrive = random_depart_arrival(duration)
    comp = pick_company(dept, arr)
    seats = seat_count_for_route(dept, arr)
    status = "ON_TIME"
    f = Flight(
        Company_ID=comp,
        Dept_Location=dept,
        Arr_Location=arr,
        Departure_Time=depart,
        Arrival_Time=arrive,
        Seats=seats,
        Status=status
    )
    flights.append(f)

# insert into DB
with Session(engine) as s:
    for f in flights:
        s.add(f)
    s.commit()

print("Inserted", len(flights), "flights.")
