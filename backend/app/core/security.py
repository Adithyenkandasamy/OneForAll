"""Security primitives: JWT access/refresh tokens and password hashing.

Uses python-jose for JWT and passlib(bcrypt) for password hashing.
Secrets come from configuration only — never hardcoded.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.exceptions import UnauthorizedError

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def _create_token(subject: str, expires_delta: timedelta, secret: str, **claims: Any) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
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
