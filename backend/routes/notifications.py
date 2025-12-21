# backend/routes/notifications.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from pydantic import BaseModel

from ..db import get_session
from ..model import Notification
from .auth_dependency import get_current_user
from ..routes.realtime import ws_mgr

router = APIRouter(prefix="/notifications", tags=["notifications"])


# inbox (JWT-based)
@router.get("/inbox")
def inbox(
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    stmt = (
        select(Notification)
        .where(Notification.Customer_ID == user["user_id"])
        .order_by(Notification.Created_At.desc())
    )
    return session.exec(stmt).all()


class TestNotifyIn(BaseModel):
    kind: str = "test"
    payload: dict = {}
    simulate_delivery: bool = True


@router.post("/test")
async def create_test_notification(
    payload: TestNotifyIn,
    session: Session = Depends(get_session),
    user=Depends(get_current_user),
):
    # ✅ always valid FK
    n = Notification(
        Customer_ID=user["user_id"],
        Kind=payload.kind,
        Payload=payload.payload,
        Sent=False,
        Created_At=datetime.utcnow(),
    )

    session.add(n)
    session.commit()
    session.refresh(n)

    delivered = False
    if payload.simulate_delivery:
        data = {
            "type": "notification",
            "notification_id": n.Notification_ID,
            "customer_id": n.Customer_ID,
            "kind": n.Kind,
            "payload": n.Payload,
            "created_at": n.Created_At.isoformat(),
        }

        delivered = await ws_mgr.send(n.Customer_ID, data)

        if delivered:
            n.Sent = True
            session.add(n)
            session.commit()

    return {
        "status": "sent" if delivered else "created",
        "notification_id": n.Notification_ID,
        "sent": n.Sent,
    }
