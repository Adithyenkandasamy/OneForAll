"""Security primitives: JWT access/refresh tokens and password hashing.

Uses python-jose for JWT and bcrypt directly for password hashing
(passlib is incompatible with bcrypt>=4; bcrypt's 72-byte limit is applied
explicitly since bcrypt>=5 raises instead of truncating).
Secrets come from configuration only — never hardcoded.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import bcrypt
from jose import JWTError, jwt

from app.core.exceptions import UnauthorizedError

ALGORITHM = "HS256"


def _truncate(pw: str) -> bytes:
    return pw.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_truncate(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_truncate(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _create_token(subject: str, expires_delta: timedelta, secret: str, **claims: Any) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "jti": uuid4().hex,
        "iat": now,
        "exp": now + expires_delta,
    }
    payload.update(claims)
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def create_access_token(
    subject: str, secret: str, expires_minutes: int, *, role: str | None = None
) -> str:
    claims = {"role": role} if role else {}
    return _create_token(subject, timedelta(minutes=expires_minutes), secret, **claims)


def create_refresh_token(subject: str, secret: str, expires_days: int) -> str:
    return _create_token(subject, timedelta(days=expires_days), secret, token_type="refresh")


def decode_token(token: str, secret: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc
