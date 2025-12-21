from typing import Dict, Optional
from datetime import datetime
from ..config import USE_FAKE_PAYMENTS

_fake_store: Dict[str, dict] = {}


def _fake_order(amount_paise: int, currency: str, notes: Optional[dict]):
    oid = f"order_fake_{int(datetime.utcnow().timestamp())}"
    _fake_store[oid] = notes or {}
    return {
        "order_id": oid,
        "amount": amount_paise,
        "currency": currency,
        "notes": notes or {}
    }


def _fake_payment(order_id: str):
    return {
        "payment_id": f"pay_fake_{int(datetime.utcnow().timestamp())}",
        "order_id": order_id,
        "notes": _fake_store.get(order_id, {})
    }


class PaymentService:

    @staticmethod
    def create_order(amount_paise: int, currency: str = "INR", notes: Optional[dict] = None):
        if USE_FAKE_PAYMENTS:
            return _fake_order(amount_paise, currency, notes)

        raise RuntimeError("Real Razorpay disabled")

    @staticmethod
    def capture_payment(order_id: str):
        if USE_FAKE_PAYMENTS:
            return _fake_payment(order_id)

        raise RuntimeError("Real Razorpay disabled")
