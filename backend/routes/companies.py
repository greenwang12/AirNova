from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from backend.db import get_session
from backend.model import Company

router = APIRouter(prefix="/companies", tags=["companies"])

@router.post("/add")
def add_company(company: Company, session: Session = Depends(get_session)):
    session.add(company)
    session.commit()
    session.refresh(company)
    return company

@router.get("/all")
def get_companies(session: Session = Depends(get_session)):
    return session.exec(select(Company)).all()
