"""Auth routes: register, login, refresh, logout."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.common import ApiMessage
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_auth_service(session: DbSession) -> AuthService:
    from app.core.container import get_container

    return get_container().auth_service(session)


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    payload: RegisterRequest, service: AuthService = Depends(_get_auth_service)
) -> object:
    return await service.register(
        email=payload.email, full_name=payload.full_name, password=payload.password
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest, service: AuthService = Depends(_get_auth_service)
) -> dict[str, str]:
    access, refresh = await service.login(email=payload.email, password=payload.password)
    return {"access_token": access, "refresh_token": refresh}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest, service: AuthService = Depends(_get_auth_service)
) -> dict[str, str]:
    access, refresh_token = await service.refresh(payload.refresh_token)
    return {"access_token": access, "refresh_token": refresh_token}


@router.post("/logout", response_model=ApiMessage)
async def logout(
    payload: RefreshRequest, service: AuthService = Depends(_get_auth_service)
) -> ApiMessage:
    await service.logout(payload.refresh_token)
    return ApiMessage(message="Logged out")


@router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUser) -> object:
    return current_user
