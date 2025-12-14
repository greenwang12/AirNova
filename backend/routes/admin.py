from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from backend.db import get_session
from backend.model import Customer, UserRole
from passlib.context import CryptContext
import jwt
from backend.config import SECRET_KEY
from datetime import datetime, timedelta
from backend.services.crypto import decrypt


router = APIRouter(prefix="/admin", tags=["admin"])

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login")
def admin_login(email: str, password: str, session: Session = Depends(get_session)):
    user = session.exec(select(Customer).where(Customer.Email == email)).first()

    if not user or not pwd.verify(password, user.Password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.Role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access only")

    token = jwt.encode({
        "id": user.Customer_ID,
        "role": "admin",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")

    return {"token": token, "role": "admin"}

def reveal(meta: dict):
    return {
        "card": decrypt(meta["card_cipher"], meta["card_nonce"]),
        "cvv": decrypt(meta["cvv_cipher"], meta["cvv_nonce"]),
    }
