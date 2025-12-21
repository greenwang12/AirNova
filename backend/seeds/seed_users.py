from sqlmodel import Session, select
from backend.db import engine
from backend.model import Customer, UserRole
from passlib.context import CryptContext

# ✅ Argon2id ONLY
pwd = CryptContext(schemes=["argon2"], deprecated="auto")

users = [
    ("Rahul Sharma","rahul@example.com","9876543210"),
    ("Neha Patel","neha@example.com","9876501234"),
    ("Aarav Mehta","aarav@example.com","9876512345"),
    ("Bonika M","bonika@example.com","9876523456"),
    ("John Mathew","john@example.com","9876534567"),
    ("Kriti Roy","kriti@example.com","9876545678"),
    ("Siddharth S","sid@example.com","9876556789"),
    ("Levi Wang","levi@example.com","9876567890"),
    ("Jusie Yumnam","jusie@example.com","9876578901"),
    ("Supriya Tensubam","supriya@example.com","9876589012"),
]

with Session(engine) as s:
    for n,e,p in users:
        if s.exec(select(Customer).where(Customer.Email == e)).first():
            continue
        s.add(Customer(
            Name=n,
            Email=e,
            Phone=p,
            Password=pwd.hash("pass123"),  # 🔐 Argon2id hash
            Role=UserRole.CUSTOMER
        ))
    s.commit()

print("10 users seeded with Argon2id")
