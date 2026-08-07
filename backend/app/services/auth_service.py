"""Authentication use-cases: register, login, token refresh, logout."""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.user_repository import RefreshTokenRepository, UserRepository
from app.utils.ids import new_id


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        refresh_tokens: RefreshTokenRepository,
    ) -> None:
        self._users = users
        self._tokens = refresh_tokens

    async def register(self, *, email: str, full_name: str, password: str) -> User:
        email = email.lower()
        if await self._users.get_by_email(email):
            raise ConflictError("An account with this email already exists")
        user = User(
            id=new_id(),
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            role="viewer",
        )
        return await self._users.add(user)

    async def login(self, *, email: str, password: str) -> tuple[str, str]:
        print(f"LOGIN ATTEMPT: {email=} / {password=}", flush=True)
        user = await self._users.get_by_email(email.lower())
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")
        return await self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        payload = decode_token(refresh_token, settings.secret_key)
        if payload.get("token_type") != "refresh":
            raise UnauthorizedError("Invalid refresh token")
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        stored = await self._tokens.get_active(token_hash)
        if stored is None:
            raise UnauthorizedError("Refresh token expired or revoked")
        user = await self._users.get(stored.user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("Account not found or disabled")
        return await self._issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        stored = await self._tokens.get_active(token_hash)
        if stored is not None:
            await self._tokens.delete(stored)

    async def _issue_tokens(self, user: User) -> tuple[str, str]:
        access = create_access_token(
            user.id, settings.secret_key, settings.access_token_expire_minutes, role=user.role
        )
        refresh = create_refresh_token(
            user.id, settings.secret_key, settings.refresh_token_expire_days
        )
        await self._tokens.add(
            RefreshToken(
                id=new_id(),
                user_id=user.id,
                token_hash=hashlib.sha256(refresh.encode()).hexdigest(),
                expires_at=datetime.now(timezone.utc)
                + timedelta(days=settings.refresh_token_expire_days),
            )
        )
        return access, refresh
