from sqlmodel import Session, select
from datetime import datetime
from typing import List

from ..model import PriceAlert, Notification


class PriceAlertsService:
    @staticmethod
    def create_alert(
        session: Session,
        customer_id: int,
        route: str,
        target_price: float,
    ) -> PriceAlert:
        alert = PriceAlert(
            Customer_ID=customer_id,
            Route=route,              # e.g. BLR-DEL
            Target_Price=target_price,
            Active=True,
            Created_At=datetime.utcnow(),
        )
        session.add(alert)
        session.commit()
        session.refresh(alert)
        return alert

    @staticmethod
    def list_alerts(
        session: Session, customer_id: int
    ) -> List[PriceAlert]:
        return session.exec(
            select(PriceAlert).where(
                PriceAlert.Customer_ID == customer_id
            )
        ).all()

    @staticmethod
    def cancel_alert(
        session: Session, alert_id: int, customer_id: int
    ) -> bool:
        alert = session.get(PriceAlert, alert_id)
        if not alert or alert.Customer_ID != customer_id:
            return False

        alert.Active = False
        session.add(alert)
        session.commit()
        return True

    @staticmethod
    def check_alerts_for_route(
        session: Session,
        route: str,
        current_price: float,
    ) -> List[Notification]:
        alerts = session.exec(
            select(PriceAlert).where(
                PriceAlert.Route == route,
                PriceAlert.Active == True,
            )
        ).all()

        created: List[Notification] = []

        for alert in alerts:
            if current_price <= alert.Target_Price:
                n = Notification(
                    Customer_ID=alert.Customer_ID,
                    Kind="price_alert",
                    Payload={
                        "route": route,
                        "price": current_price,
                        "target": alert.Target_Price,
                    },
                    Sent=False,
                    Created_At=datetime.utcnow(),
                )
                session.add(n)
                alert.Active = False
                created.append(n)

        if created:
            session.commit()
            for n in created:
                session.refresh(n)

        return created
