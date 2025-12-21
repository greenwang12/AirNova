import os
import base64
from typing import Dict
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# =========================
# KEY MANAGEMENT
# =========================
# AES-256 requires 32-byte key (base64-encoded in env)

KEY_B64 = os.getenv("PAYMENT_AES_KEY")
if not KEY_B64:
    raise RuntimeError("PAYMENT_AES_KEY not set")

try:
    KEY = base64.b64decode(KEY_B64)
except Exception:
    raise RuntimeError("Invalid base64 PAYMENT_AES_KEY")

if len(KEY) != 32:
    raise RuntimeError("PAYMENT_AES_KEY must decode to 32 bytes (AES-256)")

# =========================
# ENCRYPTION
# =========================

def encrypt(plaintext: str) -> Dict[str, str]:
    """
    Encrypts sensitive payment data using AES-256-GCM.

    Returns:
      {
        cipher: base64(ciphertext + auth_tag),
        nonce: base64(nonce)
      }
    """
    if not isinstance(plaintext, str):
        raise TypeError("Plaintext must be a string")

    aes = AESGCM(KEY)
    nonce = os.urandom(12)  # 96-bit nonce (NIST recommended)

    ciphertext = aes.encrypt(
        nonce,
        plaintext.encode("utf-8"),
        None   # no associated data
    )

    return {
        "cipher": base64.b64encode(ciphertext).decode(),
        "nonce": base64.b64encode(nonce).decode()
    }

# =========================
# DECRYPTION
# =========================

def decrypt(cipher: str, nonce: str) -> str:
    """
    Decrypts AES-256-GCM encrypted data.
    Used only by authorized backend components.
    """
    if not cipher or not nonce:
        raise ValueError("Ciphertext and nonce required")

    aes = AESGCM(KEY)

    try:
        plaintext = aes.decrypt(
            base64.b64decode(nonce),
            base64.b64decode(cipher),
            None
        )
    except Exception:
        raise ValueError("Decryption failed or data tampered")

    return plaintext.decode("utf-8")
