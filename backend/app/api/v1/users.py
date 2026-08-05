"""User management routes (admin)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, DbSession, require_roles
from app.schemas.user import UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

AdminOnly = Depends(require_roles("admin"))


def _get_user_service(session: DbSession) -> UserService:
    from app.core.container import get_container

    return get_container().user_service(session)


@router.get("", response_model=list[UserRead])
async def list_users(
    _: CurrentUser, __: object = AdminOnly, service: UserService = Depends(_get_user_service)
) -> object:
    return await service.list()


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    actor: CurrentUser,
    __: object = AdminOnly,
    service: UserService = Depends(_get_user_service),
) -> object:
    return await service.update(actor, user_id, full_name=payload.full_name, role=payload.role)
