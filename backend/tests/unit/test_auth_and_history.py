"""Auth + history service tests against in-memory SQLite."""

from __future__ import annotations

import pytest

from app.core.exceptions import ConflictError, UnauthorizedError
from app.repositories.history_repository import HistoryRepository
from app.repositories.user_repository import RefreshTokenRepository, UserRepository
from app.services.auth_service import AuthService
from app.services.history_service import HistoryService


@pytest.mark.asyncio
async def test_register_login_refresh_flow(db_session):
    service = AuthService(UserRepository(db_session), RefreshTokenRepository(db_session))
    user = await service.register(email="bob@factory.test", full_name="Bob", password="password123")
    assert user.role == "viewer"

    with pytest.raises(ConflictError):
        await service.register(email="bob@factory.test", full_name="Bob", password="password123")

    access, refresh = await service.login(email="bob@factory.test", password="password123")
    assert access and refresh

    new_access, new_refresh = await service.refresh(refresh)
    assert new_access and new_refresh

    with pytest.raises(UnauthorizedError):
        await service.login(email="bob@factory.test", password="wrong")


@pytest.mark.asyncio
async def test_history_records_and_lists(db_session):
    history = HistoryService(HistoryRepository(db_session))
    await history.record(
        user_id="u1",
        agent_name="inventory",
        query="low stock?",
        response="2 items low",
        model="llama",
        tool_calls_used=2,
        risk_flags=["low-stock"],
    )
    records = await history.list_for_user("u1", agent_name="inventory")
    assert len(records) == 1
    assert records[0].response == "2 items low"
    assert records[0].risk_flags == ["low-stock"]
