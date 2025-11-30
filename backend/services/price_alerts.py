# backend/services/price_alerts.py
from sqlmodel import Session, select
from ..model import PriceAlert, Notification, Flight
from datetime import datetime
from typing import List, Dict

class PriceAlertsService:
    @staticmethod
    def create_alert(session: Session, customer_id: int, route: str, target_price: float) -> PriceAlert:
        pa = PriceAlert(Customer_ID=customer_id, Route=route, Target_Price=target_price, Created_At=datetime.utcnow())
        session.add(pa); session.commit(); session.refresh(pa)
        return pa

    @staticmethod
    def list_alerts(session: Session, customer_id: int) -> List[PriceAlert]:
        return session.exec(select(PriceAlert).where(PriceAlert.Customer_ID == customer_id)).all()

    @staticmethod
    def cancel_alert(session: Session, alert_id: int, customer_id: int) -> bool:
        pa = session.get(PriceAlert, alert_id)
        if not pa or pa.Customer_ID != customer_id:
            return False
        pa.Active = False
        session.add(pa); session.commit()
        return True

    @staticmethod
    def check_alerts_for_route(session: Session, route: str, current_price: float) -> List[Notification]:
        # find active alerts for route and create notifications for matches
        alerts = session.exec(select(PriceAlert).where(PriceAlert.Route == route, PriceAlert.Active == True)).all()
        created = []
        for a in alerts:
            if current_price <= a.Target_Price:
                n = Notification(Customer_ID=a.Customer_ID, Kind="price_alert", Payload={"route": route, "price": current_price, "target": a.Target_Price}, Sent=False, Created_At=datetime.utcnow())
                session.add(n)
                a.Active = False  # deactivate after firing
                created.append(n)
        if created:
            session.commit()
            for n in created: session.refresh(n)
        return created
