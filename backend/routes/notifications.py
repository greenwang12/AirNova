# backend/routes/notifications.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..model import Notification
from pydantic import BaseModel
from datetime import datetime
import json
from ..routes.realtime import ws_mgr   # reuse websocket manager

router = APIRouter(prefix="/notifications", tags=["notifications"])


# basic inbox
@router.get("/inbox/{customer_id}")
def inbox(customer_id: int, session: Session = Depends(get_session)):
    stmt = select(Notification).where(Notification.Customer_ID == customer_id).order_by(Notification.Created_At.desc())
    return session.exec(stmt).all()


# mark a single notification as sent
@router.post("/mark-sent/{notification_id}")
def mark_sent(notification_id: int, session: Session = Depends(get_session)):
    n = session.get(Notification, notification_id)
    if not n:
        raise HTTPException(status_code=404, detail="notification not found")
    n.Sent = True
    session.add(n)
    session.commit()
    session.refresh(n)
    return n


# test/create notification (tries WS delivery immediately)
class TestNotifyIn(BaseModel):
    customer_id: int
    kind: str = "test"
    payload: dict = {}
    simulate_delivery: bool = True


@router.post("/test")
async def create_test_notification(payload: TestNotifyIn, session: Session = Depends(get_session)):
    # persist notification
    n = Notification(
        Customer_ID=payload.customer_id,
        Kind=payload.kind,
        Payload=payload.payload,
        Sent=False,
        Created_At=datetime.utcnow()
    )
    session.add(n)
    session.commit()
    session.refresh(n)

    # attempt WS delivery
    delivered = False
    try:
        data = {
            "type": "notification",
            "notification_id": n.Notification_ID,
            "customer_id": n.Customer_ID,
            "kind": n.Kind,
            "payload": n.Payload,
            "created_at": n.Created_At.isoformat() if n.Created_At else None
        }
        delivered = await ws_mgr.send(n.Customer_ID, data)
    except Exception:
        delivered = False

    if delivered:
        n.Sent = True
        session.add(n)
        session.commit()
        session.refresh(n)

    return {"status": "sent" if delivered else "created", "notification_id": n.Notification_ID, "sent": n.Sent}

@router.post("/send-pending")
async def send_pending(limit: int = 200, session: Session = Depends(get_session)):
    stmt = (
        select(Notification)
        .where(Notification.Sent == False)
        .order_by(Notification.Created_At.asc())
        .limit(limit)
    )

    pending = session.exec(stmt).all()
    total = len(pending)
    delivered_count = 0

    for n in pending:
        try:
            data = {
                "type": "notification",
                "notification_id": n.Notification_ID,
                "customer_id": n.Customer_ID,
                "kind": n.Kind,
                "payload": n.Payload,
                "created_at": n.Created_At.isoformat() if n.Created_At else None,
            }

            sent = await ws_mgr.send(n.Customer_ID, data)

            if sent:
                n.Sent = True
                session.add(n)
                session.commit()
                session.refresh(n)
                delivered_count += 1

        except Exception:
            print("send-pending: error sending notification", n.Notification_ID)

    # -------- FIXED COUNT --------
    from sqlalchemy import func
    result = session.exec(
        select(func.count()).select_from(Notification).where(Notification.Sent == False)
    ).one()

    remaining_pending = result[0] if isinstance(result, tuple) else result
    remaining_pending = int(remaining_pending)

    return {
        "total_checked": total,
        "delivered": delivered_count,
        "remaining_pending": remaining_pending,
    }
