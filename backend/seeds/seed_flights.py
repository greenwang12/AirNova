import random
from datetime import datetime, timedelta
from sqlmodel import Session
from backend.db import engine
from backend.model import Flight, FlightStatus

# =========================
# VALID COMPANY IDS ONLY
# =========================
DOMESTIC_COMPANIES = [1, 3, 4, 5]        # IndiGo, Vistara, SpiceJet, Akasa
INTERNATIONAL_COMPANIES = [2, 6, 7, 8, 9, 10, 11, 12, 13]  # Added Gulf Air (13)

# =========================
# AIRLINE CODES (for realistic flight numbers)
# =========================
AIRLINE_CODES = {
    1: "6E",   # IndiGo
    2: "AI",   # Air India
    3: "UK",   # Vistara
    4: "SG",   # SpiceJet
    5: "QP",   # Akasa Air
    6: "EK",   # Emirates
    7: "QR",   # Qatar Airways
    8: "SQ",   # Singapore Airlines
    9: "BA",   # British Airways
    10: "LH",  # Lufthansa
    11: "AA",  # American Airlines
    12: "BW",  # Caribbean Airlines
    13: "GF",  # Gulf Air
}

# =========================
# ROUTES
# =========================
ROUTES = [
    # ==============================
    # 🇮🇳 DOMESTIC ROUTES (India)
    # ==============================
    ("DEL","BOM"),("BOM","DEL"),
    ("DEL","BLR"),("BLR","DEL"),
    ("DEL","MAA"),("MAA","DEL"),
    ("DEL","HYD"),("HYD","DEL"),
    ("DEL","CCU"),("CCU","DEL"),
    ("DEL","PNQ"),("PNQ","DEL"),
    ("DEL","AMD"),("AMD","DEL"),
    ("DEL","JAI"),("JAI","DEL"),
    ("DEL","IXC"),("IXC","DEL"),

    ("BOM","BLR"),("BLR","BOM"),
    ("BOM","MAA"),("MAA","BOM"),
    ("BOM","HYD"),("HYD","BOM"),
    ("BOM","GOA"),("GOA","BOM"),
    ("BOM","CCU"),("CCU","BOM"),

    ("BLR","MAA"),("MAA","BLR"),
    ("BLR","HYD"),("HYD","BLR"),
    ("BLR","GOA"),("GOA","BLR"),
    ("BLR","COK"),("COK","BLR"),

    ("MAA","COK"),("COK","MAA"),
    ("MAA","TRV"),("TRV","MAA"),

    # ==============================
    # 🌍 MIDDLE EAST ROUTES
    # ==============================
    ("DEL","DXB"),("DXB","DEL"),
    ("DEL","DOH"),("DOH","DEL"),
    ("DEL","AUH"),("AUH","DEL"),
    ("DEL","BAH"),("BAH","DEL"),

    ("BOM","DXB"),("DXB","BOM"),
    ("BOM","DOH"),("DOH","BOM"),
    ("BOM","AUH"),("AUH","BOM"),
    ("BOM","BAH"),("BAH","BOM"),

    ("BLR","DXB"),("DXB","BLR"),
    ("BLR","DOH"),("DOH","BLR"),

    ("HYD","DXB"),("DXB","HYD"),
    ("HYD","DOH"),("DOH","HYD"),

    ("MAA","DXB"),("DXB","MAA"),
    ("CCU","DXB"),("DXB","CCU"),

    # ==============================
    # 🌏 SOUTH & SOUTHEAST ASIA
    # ==============================
    ("DEL","SIN"),("SIN","DEL"),
    ("DEL","BKK"),("BKK","DEL"),
    ("DEL","KUL"),("KUL","DEL"),
    ("DEL","CMB"),("CMB","DEL"),
    ("DEL","DAC"),("DAC","DEL"),

    ("BOM","SIN"),("SIN","BOM"),
    ("BOM","BKK"),("BKK","BOM"),
    ("BOM","CMB"),("CMB","BOM"),

    ("BLR","SIN"),("SIN","BLR"),
    ("MAA","SIN"),("SIN","MAA"),
    ("CCU","DAC"),("DAC","CCU")
]

DOMESTIC = {"DEL","BLR","BOM","MAA","GOA","HYD"}

# ==============================
# HELPER FUNCTIONS
# ==============================
def pick_company(dept, arr):
    if dept in DOMESTIC and arr in DOMESTIC:
        return random.choice(DOMESTIC_COMPANIES)
    return random.choice(INTERNATIONAL_COMPANIES)

def generate_flight_code(company_id):
    prefix = AIRLINE_CODES.get(company_id, "XX")
    return f"{prefix}{random.randint(100, 9999)}"

base_date = datetime.utcnow() + timedelta(days=5)

def estimate_duration(dept, arr):
    if dept in DOMESTIC and arr in DOMESTIC:
        return random.randint(90, 160)
    return random.randint(240, 900)

def random_times(duration):
    dep = base_date + timedelta(
        days=random.randint(0, 60),
        hours=random.randint(0, 23),
        minutes=random.choice([0, 15, 30, 45])
    )
    return dep, dep + timedelta(minutes=duration)

def seat_count(dept, arr):
    if dept in DOMESTIC and arr in DOMESTIC:
        return random.choice([150, 180, 200])
    return random.choice([220, 250, 300])

# ==============================
# INSERT 100 FLIGHTS
# ==============================
with Session(engine) as session:
    for _ in range(100):
        dept, arr = random.choice(ROUTES)
        company_id = pick_company(dept, arr)
        duration = estimate_duration(dept, arr)
        depart, arrive = random_times(duration)
        seats = seat_count(dept, arr)

        flight = Flight(
            Company_ID=company_id,
            Flight_Code=generate_flight_code(company_id),
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

print("✅ 100 flights inserted successfully")
