import os
import time
import hmac
import jwt
import hashlib
from typing import Dict
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# =========================
# CONFIG
# =========================

JWT_SECRET = os.getenv("SECRET_KEY", "change-me")
JWT_ALGO = "HS256"

HMAC_SECRET = os.getenv("HMAC_SECRET", "hmac-secret")
MAX_DRIFT = int(os.getenv("MAX_DRIFT", 60))  # seconds

security = HTTPBearer()

# Demo-only nonce store (use Redis in production)
USED_NONCES = set()


# =========================
# JWT AUTH
# =========================

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Verifies JWT token and extracts user identity
    """
    token = creds.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "user_id": payload["user_id"],
        "role": payload.get("role")
    }


# =========================
# HMAC ANOMALY DETECTION
# =========================

async def verify_hmac(req: Request):
    """
    Verifies HMAC-SHA256 signature, timestamp freshness,
    and nonce replay protection
    """

    sig = req.headers.get("X-Signature")
    ts = req.headers.get("X-Timestamp")
    nonce = req.headers.get("X-Nonce")

    # --- Header check ---
    if not sig or not ts or not nonce:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing HMAC headers"
        )

    # --- Timestamp validation ---
    try:
        ts = int(ts)
    except ValueError:
        raise HTTPException(401, "Invalid timestamp")

    if abs(time.time() - ts) > MAX_DRIFT:
        raise HTTPException(401, "Expired request")

    # --- Replay protection ---
    if nonce in USED_NONCES:
        raise HTTPException(401, "Replay attack detected")
    USED_NONCES.add(nonce)

    # --- Read raw body safely ---
    body = await req.body()

    # --- Signature computation ---
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


# =========================
# COMBINED DEPENDENCY
# =========================

def jwt_and_hmac(
    user: Dict = Depends(get_current_user),
    _: None = Depends(verify_hmac)
) -> Dict:
    """
    Use this for sensitive endpoints (payments)
    """
    return user
