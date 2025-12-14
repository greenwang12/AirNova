# backend/routes/auth_dependency.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

# Bearer auth (Swagger + runtime)
security = HTTPBearer()

# Config
SECRET = os.getenv("SECRET_KEY", "change-me")
ALGO = "HS256"

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security)
):
    # No Authorization header
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token missing"
        )

    token = creds.credentials

    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Safety check
    if "id" not in payload or "role" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token"
        )

    return {
        "user_id": payload["id"],
        "role": payload["role"]
    }
