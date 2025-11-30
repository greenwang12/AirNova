import hashlib
from sqlmodel import Session
from backend.db import engine
from backend.model import Customer, UserRole

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()


users = [
    ("Rahul Sharma", "rahul@example.com", "9876543210", "pass123"),
    ("Neha Patel", "neha@example.com", "9876501234", "pass123"),
    ("Aarav Mehta", "aarav@example.com", "9876512345", "pass123"),
    ("Bonika M", "bonika@example.com", "9876523456", "pass123"),
    ("John Mathew", "john@example.com", "9876534567", "pass123"),
    ("Kriti Roy", "kriti@example.com", "9876545678", "pass123"),
    ("Siddharth S", "sid@example.com", "9876556789", "pass123"),
    ("Levi Wang", "levi@example.com", "9876567890", "pass123"),
    ("Jusie Yumnam", "jusie@example.com", "9876578901", "pass123"),
    ("Supriya Tensubam", "supriya@example.com", "9876589012", "pass123"),
]

with Session(engine) as session:
    for name, email, phone, password in users:
        session.add(Customer(
            Name=name,
            Email=email,
            Phone=phone,
            Password=hash_pw(password),
            Role=UserRole.CUSTOMER
        ))
    session.commit()

print("Inserted users!")
