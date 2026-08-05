"""Shared FastAPI dependencies: DB session and authenticated user resolution."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.database.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

_bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    session: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    if credentials is None:
        raise UnauthorizedError("Authentication required")
    payload = decode_token(credentials.credentials, settings.secret_key)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")
    user = await UserRepository(session).get(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("Account not found or disabled")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: str) -> object:
    def _dep(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise ForbiddenError(f"Requires one of roles: {', '.join(roles)}")
        return current_user

    return _dep
