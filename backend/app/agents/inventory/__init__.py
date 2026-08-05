"""Register the inventory agent catalog entry when this package is imported."""

from app.agents.inventory.agent import InventoryAgent
from app.shared.agents.registry import register

register(InventoryAgent.name, InventoryAgent.description, lambda: None)
