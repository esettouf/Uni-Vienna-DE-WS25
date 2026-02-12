import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

ALGORITHM = "HS256"
DEFAULT_TTL_HOURS = 24


def _secret() -> str:
    return os.getenv("SECRET_KEY", "dev-secret")


def create_access_token(user_id: str, role: Optional[str] = None, ttl_hours: int = DEFAULT_TTL_HOURS) -> str:
    """Create a signed JWT with user id and role."""
    now = datetime.utcnow()
    payload = {
        "sub": user_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=ttl_hours),
    }
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT, raising jwt exceptions on failure."""
    return jwt.decode(token, _secret(), algorithms=[ALGORITHM])
