"""Aggregates all v1 routers (app layer + AI agent routers)."""

from __future__ import annotations

from fastapi import APIRouter
from app.agents.quality.api.router import quality_router

from app.api.v1 import auth, conversations, dashboard, health, history, notifications, users
from app.api.ws.router import router as ws_router

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(ws_router, prefix="/ws")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(notifications.router)
api_router.include_router(conversations.router)
api_router.include_router(history.router)
api_router.include_router(dashboard.router)


def include_agent_routers(root: APIRouter, prefix: str) -> None:
    """Mount every registered AI agent router under the API prefix.

    Imported lazily inside the function so agent packages (which depend on
    ``app/shared``) are wired only when the app is assembled.
    """
    from app.agents.inventory.router import router as inventory_router
    from app.agents.executive.router import router as executive_router

    root.include_router(inventory_router, prefix=prefix)
    root.include_router(executive_router, prefix=prefix)
    root.include_router(quality_router, prefix=f"{prefix}/agents/quality")


def include_agents_catalog(root: APIRouter, prefix: str) -> None:
    """Expose the agent catalog for the frontend."""

    from fastapi import APIRouter as _Router

    from app.agents import inventory as _inventory  # noqa: F401
    from app.agents import executive as _executive  # noqa: F401
    from app.shared.agents.registry import list_agents

    catalog = _Router(prefix="/agents", tags=["agents"])

    @catalog.get("")
    async def agents_catalog() -> dict[str, list[dict[str, str]]]:
        return {"agents": list_agents()}

    root.include_router(catalog, prefix=prefix)
