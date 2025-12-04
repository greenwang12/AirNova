# backend/services/payment_service.py
from typing import Dict, Optional
from datetime import datetime
import os
from ..config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET, USE_FAKE_PAYMENTS

# only import razorpay if real mode
client = None
if not USE_FAKE_PAYMENTS:
    import razorpay
    client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# In-memory store to keep fake order -> notes mapping (only for fake mode)
_fake_store: Dict[str, dict] = {}

def _fake_order(amount_cents:int, currency:str, notes: Optional[dict] = None):
    ts = int(datetime.utcnow().timestamp())
    order_id = f"order_local_{ts}_{str(len(_fake_store)+1)}"
    # store notes so fetch_payment can return them later
    _fake_store[order_id] = notes or {}
    return {
        "order_id": order_id,
        "amount": amount_cents,
        "currency": currency,
        "order": {"id": order_id, "amount": amount_cents, "currency": currency, "notes": notes or {}}
    }

def _fake_payment(payment_id:str, order_id: Optional[str] = None, notes:Optional[dict]=None):
    # Return a fake payment record with notes derived from provided order_id or notes param
    ret_notes = {}
    if order_id and order_id in _fake_store:
        ret_notes = _fake_store.get(order_id, {})
    elif notes:
        ret_notes = notes
    return {"id": payment_id, "method": "card", "notes": ret_notes}

class PaymentService:

    @staticmethod
    def create_order(amount_cents: int, currency: str = "INR", receipt: Optional[str] = None, notes: Optional[dict] = None) -> Dict:
        """
        Create an order. In fake mode we persist notes in-memory so later fetch_payment can return them.
        """
        if USE_FAKE_PAYMENTS:
            return _fake_order(amount_cents, currency, notes=notes)

        payload = {
            "amount": amount_cents,
            "currency": currency,
            "receipt": receipt or "",
            "payment_capture": 1,
            "notes": notes or {}
        }
        order = client.order.create(payload)
        return {"order_id": order["id"], "amount": order["amount"], "currency": order["currency"], "order": order}

    @staticmethod
    def fetch_payment(payment_id: str, order_id: Optional[str] = None):
        """
        Fetch payment details.
        In fake mode, if order_id provided we return the notes saved earlier.
        """
        if USE_FAKE_PAYMENTS:
            return _fake_payment(payment_id, order_id=order_id)
        return client.payment.fetch(payment_id)

    @staticmethod
    def refund(payment_id: str, amount: Optional[int] = None):
        if USE_FAKE_PAYMENTS:
            return {"status":"refunded","payment_id":payment_id,"amount":amount}
        payload = {}
        if amount:
            payload["amount"] = amount
        return client.payment.refund(payment_id, payload)

    @staticmethod
    def verify_webhook_signature(body: bytes, signature: str, secret: str = RAZORPAY_WEBHOOK_SECRET) -> bool:
        if USE_FAKE_PAYMENTS:
            return True
        try:
            razorpay.utils.verify_webhook_signature(body, signature, secret)
            return True
        except Exception:
            return False
