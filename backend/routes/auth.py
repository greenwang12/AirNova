# backend/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from backend.db import get_session
from backend.model import Customer
from passlib.context import CryptContext
import hashlib, jwt, os
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])

# CryptContext: prefer argon2 but allow bcrypt as fallback.
# Argon2 params tuned low to avoid high memory usage (memory_cost in KiB).
# memory_cost=8192 -> ~8 MiB memory per hash (very light)
pwd = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=8192,
    argon2__parallelism=1
)

SECRET = os.getenv("SECRET_KEY", "change-me")
JWT_ALGO = "HS256"
JWT_EXP_HOURS = 24

def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

@router.post("/login")
def login(email: str, password: str, session: Session = Depends(get_session)):
    user = session.exec(select(Customer).where(Customer.Email == email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    ok = False
    # 1) try passlib verify (argon2 or bcrypt). won't use persistent memory, only momentarily for hashing.
    try:
        if pwd.verify(password, user.Password):
            ok = True
    except Exception:
        ok = False

    # 2) fallback: seeded/test users hashed with sha256
    if not ok:
        if sha256_hash(password) == user.Password:
            ok = True

    if not ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    role_val = user.Role.value if hasattr(user.Role, "value") else str(user.Role)
    token = jwt.encode({
        "id": user.Customer_ID,
        "role": role_val,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXP_HOURS)
    }, SECRET, algorithm=JWT_ALGO)

    return {"token": token, "role": role_val}
