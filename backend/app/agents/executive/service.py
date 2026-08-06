"""Executive Orchestrator service layer."""

from __future__ import annotations

from app.core.logging import get_logger
from app.api.deps import DbSession

logger = get_logger(__name__)

class ExecutiveService:
    def __init__(self) -> None:
        pass

    async def answer(
        self, query: str, *, user_id: str, role: str, conversation_id: str | None
    ) -> dict:
        from app.core.config import settings
        from groq import AsyncGroq
        
        # Using GROQ_CENTRAL_API_KEY for the top-level orchestration
        client = AsyncGroq(api_key=settings.groq_central_api_key)
        
        system_prompt = (
            "You are the Orvixo Central AI Orchestrator. You manage the manufacturing ecosystem. "
            "You can answer queries on production, inventory, maintenance, and personnel. "
            "Address the user professionally as a high-level centralized intelligence entity."
        )

        response = await client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=1024,
            temperature=0.1
        )
        
        content = response.choices[0].message.content or "No content returned."
        
        return {
            "content": content,
            "tool_calls_used": 0,
            "model": settings.groq_model,
            "risk_flags": [],
            "conversation_id": conversation_id,
        }
