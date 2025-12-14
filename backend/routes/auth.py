from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from backend.db import get_session
from backend.model import Customer, UserRole
from passlib.context import CryptContext
from pydantic import BaseModel
import hashlib, jwt, os
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=8192,
    argon2__parallelism=1
)

SECRET = os.getenv("SECRET_KEY", "change-me")
JWT_ALGO = "HS256"
JWT_EXP_HOURS = 24


# -------- Schemas --------
class RegisterIn(BaseModel):
    name: str
    email: str
    phone: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str


# -------- Helpers --------
def sha256_hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# -------- Register (Argon2 only) --------
@router.post("/register")
def register(payload: RegisterIn, session: Session = Depends(get_session)):
    if session.exec(select(Customer).where(Customer.Email == payload.email)).first():
        raise HTTPException(400, "Email already registered")

    user = Customer(
        Name=payload.name,
        Email=payload.email,
        Phone=payload.phone,
        Password=pwd.hash(payload.password),   # Argon2
        Role=UserRole.CUSTOMER
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return {"message": "Registered successfully"}


# -------- Login (Argon2 + SHA256 fallback) --------
@router.post("/login")
def login(payload: LoginIn, session: Session = Depends(get_session)):
    user = session.exec(
        select(Customer).where(Customer.Email == payload.email)
    ).first()

    if not user:
        raise HTTPException(401, "Invalid credentials")

    valid = False

    # 1️⃣ Argon2 verification (new users)
    try:
        if pwd.verify(payload.password, user.Password):
            valid = True
    except Exception:
        pass

    # 2️⃣ SHA256 fallback (legacy users)
    if not valid and sha256_hash(payload.password) == user.Password:
        valid = True
        # OPTIONAL auto-upgrade to Argon2
        user.Password = pwd.hash(payload.password)
        session.add(user)
        session.commit()

    if not valid:
        raise HTTPException(401, "Invalid credentials")

    token = jwt.encode(
        {
            "id": user.Customer_ID,
            "role": user.Role.value,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXP_HOURS)
        },
        SECRET,
        algorithm=JWT_ALGO
    )

    return {"access_token": token, "role": user.Role.value}
