import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# -----------------------------
# Database
# -----------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

# -----------------------------
# JWT Auth
# -----------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set")

JWT_ALGO = "HS256"
JWT_EXP_HOURS = 24
JWT_ISSUER = "airnova-api"

# -----------------------------
# HMAC API Security
# -----------------------------
HMAC_SECRET = os.getenv("HMAC_SECRET")
if not HMAC_SECRET:
    raise RuntimeError("HMAC_SECRET not set")

MAX_DRIFT = 300  # 5 minutes

# -----------------------------
# Payment Encryption
# -----------------------------
PAYMENT_AES_KEY = os.getenv("PAYMENT_AES_KEY")
if not PAYMENT_AES_KEY:
    raise RuntimeError("PAYMENT_AES_KEY not set")

# -----------------------------
# Optional Gateway Flags
# -----------------------------
USE_FAKE_PAYMENTS = os.getenv("USE_FAKE_PAYMENTS", "false").lower() in ("1", "true", "yes")

# -----------------------------
# Razorpay (optional / demo)
# -----------------------------
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")
