"""DI container — the composition root.

All objects are constructed here and injected. Routers obtain services via
``get_container().<factory>(session)``. Request-scoped collaborators (DB
session, user) come from FastAPI; long-lived collaborators (repositories,
services) are built per-request from the same factories. This keeps the
object graph explicit and testable: tests swap factories for fakes.
"""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.conversation_repository import ConversationRepository, MessageRepository
from app.repositories.history_repository import HistoryRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import RefreshTokenRepository, UserRepository
from app.services.auth_service import AuthService
from app.services.conversation_service import ConversationService
from app.services.history_service import HistoryService
from app.services.notification_service import NotificationService
from app.services.user_service import UserService

# Repositories are cheap, session-bound adapters; build on demand.
_REPO_FACTORIES = {
    "users": lambda s: UserRepository(s),
    "refresh_tokens": lambda s: RefreshTokenRepository(s),
    "notifications": lambda s: NotificationRepository(s),
    "conversations": lambda s: ConversationRepository(s),
    "messages": lambda s: MessageRepository(s),
    "history": lambda s: HistoryRepository(s),
}


def _build_inventory_service(session: AsyncSession) -> object:
    from app.agents.inventory.agent import InventoryAgent
    from app.agents.inventory.mcp_tools import SheetsMcpGateway
    from app.agents.inventory.repository import HistorySinkAdapter
    from app.agents.inventory.service import InventoryService
    from app.shared.agents.registry import register
    from app.shared.llm.groq import GroqProvider

    gateway = SheetsMcpGateway()
    llm = GroqProvider()
    history = HistorySinkAdapter(HistoryService(HistoryRepository(session)))
    agent = InventoryAgent(llm=llm, gateway=gateway, history=history)
    register(agent.name, agent.description, lambda: agent)

    notification_service = NotificationService(
        notifications=NotificationRepository(session)
    )
    return InventoryService(
        agent=agent,
        gateway=gateway,
        notification_service=notification_service,
    )


class Container:
    def user_repository(self, session: AsyncSession) -> UserRepository:
        return _REPO_FACTORIES["users"](session)

    def refresh_token_repository(self, session: AsyncSession) -> RefreshTokenRepository:
        return _REPO_FACTORIES["refresh_tokens"](session)

    def notification_repository(self, session: AsyncSession) -> NotificationRepository:
        return _REPO_FACTORIES["notifications"](session)

    def conversation_repository(self, session: AsyncSession) -> ConversationRepository:
        return _REPO_FACTORIES["conversations"](session)

    def message_repository(self, session: AsyncSession) -> MessageRepository:
        return _REPO_FACTORIES["messages"](session)

    def history_repository(self, session: AsyncSession) -> HistoryRepository:
        return _REPO_FACTORIES["history"](session)

    def auth_service(self, session: AsyncSession) -> AuthService:
        return AuthService(
            users=self.user_repository(session),
            refresh_tokens=self.refresh_token_repository(session),
        )

    def user_service(self, session: AsyncSession) -> UserService:
        return UserService(users=self.user_repository(session))

    def notification_service(self, session: AsyncSession) -> NotificationService:
        return NotificationService(notifications=self.notification_repository(session))

    def conversation_service(self, session: AsyncSession) -> ConversationService:
        return ConversationService(
            conversations=self.conversation_repository(session),
            messages=self.message_repository(session),
        )

    def history_service(self, session: AsyncSession) -> HistoryService:
        return HistoryService(history=self.history_repository(session))

    def inventory_service(self, session: AsyncSession) -> object:
        return _build_inventory_service(session)


@lru_cache
def get_container() -> Container:
    return Container()
