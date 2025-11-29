# backend/services/payment_service.py
import razorpay
from typing import Dict, Optional
from ..config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

class PaymentService:
    @staticmethod
    def create_order(amount_cents: int, currency: str = "INR", receipt: str | None = None, notes: Optional[dict] = None, idempotency_key: Optional[str] = None) -> Dict:
        """
        Create Razorpay order.
        amount_cents: integer in paise (e.g. 20000 for ₹200.00)
        """
        payload = {
            "amount": amount_cents,   # in paise
            "currency": currency,
            "receipt": receipt or "",
            "payment_capture": 1,     # auto-capture
            "notes": notes or {},
        }
        # razorpay python client doesn't accept idempotency_key param directly; you can pass headers if needed
        order = client.order.create(payload)
        return {"order_id": order["id"], "amount": order["amount"], "currency": order["currency"], "order": order}

    @staticmethod
    def fetch_payment(payment_id: str):
        return client.payment.fetch(payment_id)

    @staticmethod
    def refund(payment_id: str, amount: Optional[int] = None):
        params = {}
        if amount:
            params["amount"] = amount
        return client.payment.refund(payment_id, params)

    @staticmethod
    def verify_webhook_signature(body: bytes, signature: str, secret: str = RAZORPAY_WEBHOOK_SECRET) -> bool:
        try:
            razorpay.utils.verify_webhook_signature(body, signature, secret)
            return True
        except Exception:
            return False
