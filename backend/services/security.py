import hmac
import hashlib
import time
from fastapi import Request, HTTPException, status
from backend.config import HMAC_SECRET, MAX_DRIFT

# Demo-only nonce store (use Redis in production)
USED_NONCES = set()

def verify_hmac(req: Request):
    sig = req.headers.get("X-Signature")
    ts = req.headers.get("X-Timestamp")
    nonce = req.headers.get("X-Nonce")

    # Header check
    if not sig or not ts or not nonce:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing HMAC headers"
        )

    # Timestamp freshness check
    try:
        ts = int(ts)
    except ValueError:
        raise HTTPException(401, "Invalid timestamp")

    if abs(time.time() - ts) > MAX_DRIFT:
        raise HTTPException(401, "Expired request")

    # Replay protection
    if nonce in USED_NONCES:
        raise HTTPException(401, "Replay attack detected")
    USED_NONCES.add(nonce)

    # Read raw body
    body = req.scope.get("body", b"")

    # Signature verification
    message = f"{ts}{nonce}".encode() + body

    expected_sig = hmac.new(
        HMAC_SECRET.encode(),
        message,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid HMAC signature"
        )
