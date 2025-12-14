import os, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_B64 = os.getenv("PAYMENT_AES_KEY")
if not KEY_B64:
    raise RuntimeError("PAYMENT_AES_KEY not set")

KEY = base64.b64decode(KEY_B64)

def encrypt(plain: str) -> dict:
    aes = AESGCM(KEY)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plain.encode(), None)
    return {
        "cipher": base64.b64encode(ct).decode(),
        "nonce": base64.b64encode(nonce).decode()
    }

def decrypt(cipher: str, nonce: str) -> str:
    aes = AESGCM(KEY)
    return aes.decrypt(
        base64.b64decode(nonce),
        base64.b64decode(cipher),
        None
    ).decode()
