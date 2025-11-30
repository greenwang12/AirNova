# backend/services/disruption_assistant.py
from sqlmodel import select
from ..model import Flight, Notification
from sqlmodel import Session
from datetime import datetime, timedelta

class DisruptionAssistant:
    @staticmethod
    def suggest_alternatives(session: Session, flight_id: int, max_suggestions: int = 3):
        # fetch original
        f = session.get(Flight, flight_id)
        if not f:
            return []
        d0 = f.Departure_Time
        window_start = d0 - timedelta(days=1)
        window_end = d0 + timedelta(days=1)
        q = select(Flight).where(
            Flight.Dept_Location == f.Dept_Location,
            Flight.Arr_Location == f.Arr_Location,
            Flight.Departure_Time >= window_start,
            Flight.Departure_Time <= window_end,
            Flight.Flight_ID != flight_id
        )
        cand = session.exec(q).all()
        # simple sort by closest time
        cand.sort(key=lambda x: abs((x.Departure_Time - d0).total_seconds()))
        return cand[:max_suggestions]

    @staticmethod
    def notify_customers_of_disruption(session: Session, flight_id: int, reason: str):
        # create notifications for customers who booked this flight
        q = select(Notification)  # placeholder - real implementation should fetch bookings and customers
        # implement per your booking model
        return True
