"""User management use-cases."""

from __future__ import annotations

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.user import USER_ROLES, User
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def get(self, user_id: str) -> User:
        user = await self._users.get(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[User]:
        return await self._users.list(limit=limit, offset=offset)

    async def update(
        self, actor: User, user_id: str, *, full_name: str | None = None, role: str | None = None
    ) -> User:
        if actor.role not in ("admin",):
            raise ForbiddenError("Only admins can update users")
        if role is not None and role not in USER_ROLES:
            raise NotFoundError(f"Unknown role: {role}")
        user = await self.get(user_id)
        if full_name is not None:
            user.full_name = full_name
        if role is not None:
            user.role = role
        return await self._users.update(user)
