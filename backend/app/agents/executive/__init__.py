"""Executive Orchestrator package."""

from app.shared.agents.registry import register

register(
    "executive",
    "Global central intelligence orchestration across all microservices.",
    lambda: None
)
