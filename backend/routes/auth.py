from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
import hashlib
import jwt
import os

from backend.db import get_session
from backend.model import Customer, UserRole

# =========================
# CONFIG
# =========================

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET = os.getenv("SECRET_KEY", "change-me")
JWT_ALGO = "HS256"
JWT_EXP_HOURS = 24

pwd = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=8192,
    argon2__parallelism=1
)

# =========================
# SCHEMAS
# =========================

class RegisterIn(BaseModel):
    name: str
    email: str
    phone: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str

# =========================
# HELPERS
# =========================

def sha256_hash(pw: str) -> str:
    """Legacy password hash (migration support only)."""
    return hashlib.sha256(pw.encode()).hexdigest()


def create_jwt(user: Customer) -> str:
    """Create signed JWT token."""
    return jwt.encode(
        {
            "id": user.Customer_ID,
            "role": user.Role.value,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXP_HOURS),
        },
        SECRET,
        algorithm=JWT_ALGO,
    )

# =========================
# ROUTES
# =========================

@router.post("/register")
def register(payload: RegisterIn, session: Session = Depends(get_session)):
    if session.exec(
        select(Customer).where(Customer.Email == payload.email)
    ).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = Customer(
        Name=payload.name,
        Email=payload.email,
        Phone=payload.phone,
        Password=pwd.hash(payload.password),   # Argon2
        Role=UserRole.CUSTOMER,
    )

    session.add(user)
    session.commit()

    return {"message": "Registered successfully"}


@router.post("/login")
def login(payload: LoginIn, session: Session = Depends(get_session)):
    user = session.exec(
        select(Customer).where(Customer.Email == payload.email)
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    valid = False

    # Argon2 verification
    try:
        valid = pwd.verify(payload.password, user.Password)
    except Exception:
        valid = False

    # Legacy SHA256 fallback + auto-upgrade
    if not valid and sha256_hash(payload.password) == user.Password:
        valid = True
        user.Password = pwd.hash(payload.password)
        session.add(user)
        session.commit()

    if not valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt(user)

    return {
    "access_token": token,
    "customer_id": user.Customer_ID,
    "name": user.Name,
    "email": user.Email,
    "role": user.Role.value
}

