from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..model import Notification

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/inbox/{customer_id}")
def inbox(customer_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Notification).where(Notification.Customer_ID == customer_id)).all()

@router.post("/mark-sent/{notification_id}")
def mark_sent(notification_id: int, session: Session = Depends(get_session)):
    n = session.get(Notification, notification_id)
    if not n:
        raise HTTPException(status_code=404, detail="notification not found")
    n.Sent = True
    session.add(n); session.commit(); session.refresh(n)
    return n
