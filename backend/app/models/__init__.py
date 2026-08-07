"""ORM model registry — import all models so metadata.create_all sees them."""

from app.models.ai_history import AIHistory
from app.models.conversation import Conversation, Message
from app.models.notification import Notification
from app.models.refresh_token import RefreshToken
from app.models.settings import AuditLog, Setting
from app.models.user import User
from app.agents.quality.models import SensorHistory, MachineState, QualityAlerts, QualityReports, MaintenancePredictions

__all__ = [
    "User",
    "RefreshToken",
    "Conversation",
    "Message",
    "AIHistory",
    "Notification",
    "SensorHistory",
    "MachineState",
    "QualityAlerts",
    "QualityReports",
    "MaintenancePredictions",
]
