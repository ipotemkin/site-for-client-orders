"""Password hashing and JWT helpers."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

ALGORITHM = "HS256"
DEFAULT_EXPIRE_MINUTES = 1440


def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET", "").strip()
    if not secret:
        raise RuntimeError(
            "JWT_SECRET environment variable is required",
        )
    return secret


def _expire_minutes() -> int:
    raw = os.getenv("JWT_EXPIRE_MINUTES", str(DEFAULT_EXPIRE_MINUTES))
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    )
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def create_access_token(
    *,
    subject: str,
    admin_id: int,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=_expire_minutes(),
    )
    payload = {
        "sub": subject,
        "admin_id": admin_id,
        "exp": expire,
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        _jwt_secret(),
        algorithms=[ALGORITHM],
    )
