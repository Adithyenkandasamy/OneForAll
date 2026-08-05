"""FastAPI wiring for the inventory agent.

Routers depend on these functions; the container builds the real service.
In tests, these are overridden with fakes via dependency_overrides.
"""

from __future__ import annotations

from fastapi import Depends

from app.api.deps import DbSession
from app.core.container import get_container


def get_inventory_service(session: DbSession) -> object:
    return get_container().inventory_service(session)


InventoryServiceDep = Depends(get_inventory_service)
