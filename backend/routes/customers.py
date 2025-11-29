from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..db import get_session
from ..model import Customer

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("/add")
def add_customer(customer: Customer, session: Session = Depends(get_session)):
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer

@router.get("/all")
def get_all_customers(session: Session = Depends(get_session)):
    return session.exec(select(Customer)).all()
