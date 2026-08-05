"""Integration tests for the inventory HTTP API (auth + fakes wired in)."""

from __future__ import annotations

import pytest

from app.agents.inventory.dependencies import get_inventory_service
from app.agents.inventory.exceptions import UnauthorizedToolError
from app.api.deps import get_current_user


class FakeInventoryService:
    async def answer(self, query, *, user_id, role, conversation_id):
        return {
            "content": f"answer for: {query}",
            "tool_calls_used": 1,
            "model": "fake-llm",
            "risk_flags": [],
            "conversation_id": conversation_id,
        }

    async def search(self, query, *, limit=25):
        return []

    async def update(self, *, sku, column, value, role):
        if role not in ("operator", "admin"):
            raise UnauthorizedToolError("requires operator/admin")
        return {"message": f"updated {sku}", "sku": sku, "column": column, "value": value}


@pytest.fixture
def override_inventory(client):
    client.app.dependency_overrides[get_inventory_service] = lambda: FakeInventoryService()


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_agents_catalog(client):
    response = await client.get("/api/v1/agents")
    assert response.status_code == 200
    assert any(agent["name"] == "inventory" for agent in response.json()["agents"])


@pytest.mark.asyncio
async def test_chat_requires_auth(client, override_inventory):
    response = await client.post("/api/v1/agents/inventory/chat", json={"query": "hello"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_works_for_authenticated_user(client, override_inventory, override_auth):
    response = await client.post(
        "/api/v1/agents/inventory/chat", json={"query": "What is below safety stock?"}
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["content"] == "answer for: What is below safety stock?"
    assert payload["tool_calls_used"] == 1


@pytest.mark.asyncio
async def test_search_requires_auth(client, override_inventory):
    response = await client.get("/api/v1/agents/inventory/search", params={"q": "steel"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_forbidden_for_viewer(client, override_inventory, override_auth):
    response = await client.post(
        "/api/v1/agents/inventory/update",
        json={"sku": "BOLT", "column": "qty", "value": "120"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_ok_for_admin(client, admin_user):
    async def _fake_current_user():
        return admin_user

    client.app.dependency_overrides[get_current_user] = _fake_current_user
    client.app.dependency_overrides[get_inventory_service] = lambda: FakeInventoryService()

    response = await client.post(
        "/api/v1/agents/inventory/update",
        json={"sku": "BOLT", "column": "qty", "value": "120"},
    )
    assert response.status_code == 200
    assert response.json()["sku"] == "BOLT"
