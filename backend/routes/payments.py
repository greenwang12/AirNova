from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel

from backend.db import get_session
from backend.model import Payment
from backend.services.crypto import encrypt
from backend.routes.auth_dependency import get_current_user , security

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
    dependencies=[Depends(get_current_user)]

)

class PayIn(BaseModel):
    amount: float
    card_number: str
    cvv: str

@router.post("/create")
def create_payment(
    p: PayIn,
    user: dict = Depends(get_current_user),  # 🔥 THIS is enough
    session: Session = Depends(get_session),
):
    enc_card = encrypt(p.card_number)
    enc_cvv = encrypt(p.cvv)

    pay = Payment(
        Customer_ID=user["user_id"],
        Amount=p.amount,
        Card_Last4=p.card_number[-4:],
        Gateway_Provider="AESGCM",
        Status="encrypted",
    )

    session.add(pay)
    session.commit()
    session.refresh(pay)

    return {"payment_id": pay.Payment_ID}
