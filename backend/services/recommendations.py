# backend/services/recommendations.py
from sqlmodel import Session, select
from ..model import Booking, Flight
from collections import Counter

class Recommender:
    @staticmethod
    def top_routes_for_customer(session: Session, customer_id: int, top_n: int = 5):
        rows = session.exec(select(Booking).where(Booking.Customer_ID == customer_id)).all()
        route_counts = Counter()
        for b in rows:
            f = session.get(Flight, b.Flight_ID)
            if not f: continue
            route = f.Dept_Location + "-" + f.Arr_Location
            route_counts[route] += 1
        return route_counts.most_common(top_n)
