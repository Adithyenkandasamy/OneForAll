"""Conversation and message routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.conversation import (
    ConversationCreate,
    ConversationRead,
    MessageRead,
    MessageSend,
)
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _get_conversation_service(session: DbSession) -> ConversationService:
    from app.core.container import get_container

    return get_container().conversation_service(session)


@router.post("", response_model=ConversationRead, status_code=201)
async def create_conversation(
    payload: ConversationCreate,
    current_user: CurrentUser,
    service: ConversationService = Depends(_get_conversation_service),
) -> object:
    return await service.create(
        user_id=current_user.id, agent_name=payload.agent_name, title=payload.title
    )


@router.get("", response_model=list[ConversationRead])
async def list_conversations(
    current_user: CurrentUser,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: ConversationService = Depends(_get_conversation_service),
) -> object:
    return await service.list_for_user(current_user.id, limit=limit, offset=offset)


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
async def list_messages(
    conversation_id: str,
    current_user: CurrentUser,
    service: ConversationService = Depends(_get_conversation_service),
) -> object:
    return await service.list_messages(current_user.id, conversation_id)


@router.post("/{conversation_id}/messages", response_model=MessageRead)
async def send_message(
    conversation_id: str,
    payload: MessageSend,
    current_user: CurrentUser,
    service: ConversationService = Depends(_get_conversation_service),
) -> object:
    return await service.add_message(
        user_id=current_user.id,
        conversation_id=conversation_id,
        role="user",
        content=payload.content,
    )
