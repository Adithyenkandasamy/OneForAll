"""Conversation and message use-cases."""

from __future__ import annotations

from datetime import datetime, timezone

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.conversation import Conversation, Message
from app.repositories.conversation_repository import ConversationRepository, MessageRepository
from app.utils.ids import new_id


class ConversationService:
    def __init__(self, conversations: ConversationRepository, messages: MessageRepository) -> None:
        self._conversations = conversations
        self._messages = messages

    async def create(self, *, user_id: str, agent_name: str, title: str) -> Conversation:
        return await self._conversations.add(
            Conversation(id=new_id(), user_id=user_id, agent_name=agent_name, title=title)
        )

    async def list_for_user(
        self, user_id: str, *, limit: int = 50, offset: int = 0
    ) -> list[Conversation]:
        return await self._conversations.list_for_user(user_id, limit=limit, offset=offset)

    async def _get_owned(self, user_id: str, conversation_id: str) -> Conversation:
        conversation = await self._conversations.get(conversation_id)
        if conversation is None:
            raise NotFoundError("Conversation not found")
        if conversation.user_id != user_id:
            raise ForbiddenError("Not your conversation")
        return conversation

    async def list_messages(self, user_id: str, conversation_id: str) -> list[Message]:
        await self._get_owned(user_id, conversation_id)
        return await self._messages.list_for_conversation(conversation_id)

    async def add_message(
        self,
        *,
        user_id: str,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: list | None = None,
    ) -> Message:
        await self._get_owned(user_id, conversation_id)
        return await self._messages.add(
            Message(
                id=new_id(),
                conversation_id=conversation_id,
                role=role,
                content=content,
                tool_calls=tool_calls,
                created_at=datetime.now(timezone.utc),
            )
        )
