"""Agent registry: name -> agent factory.

Agents are request-scoped (their history sink needs a DB session), so the
registry stores factories. The composition root registers each agent once;
the API catalog reads from here; future microservices register on the same
key.
"""

from __future__ import annotations

from collections.abc import Callable

from app.core.exceptions import NotFoundError
from app.shared.agents.base_agent import Agent

AgentFactory = Callable[[], Agent]

_registry: dict[str, tuple[str, AgentFactory]] = {}


def register(name: str, description: str, factory: AgentFactory) -> None:
    _registry[name] = (description, factory)


def get_agent(name: str) -> Agent:
    try:
        _, factory = _registry[name]
    except KeyError:
        raise NotFoundError(f"Agent {name!r} is not registered") from None
    if factory is None:
        raise NotFoundError(f"Agent {name!r} has no live instance yet")
    return factory()


def list_agents() -> list[dict[str, str]]:
    return [
        {"name": name, "description": description} for name, (description, _) in _registry.items()
    ]
