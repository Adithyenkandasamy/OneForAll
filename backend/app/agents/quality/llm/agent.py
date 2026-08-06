import json
from groq import AsyncGroq
from app.core.config import settings
from app.agents.quality.llm.prompt import build_system_prompt
from app.core.logging import get_logger

logger = get_logger(__name__)

class QualityAgent:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.groq_central_api_key)
        self.system_prompt = build_system_prompt()
        self.model = "llama-3.3-70b-versatile"
        
    async def chat(self, user_query: str, structured_context: dict) -> str:
        # Prevent data dumping logic internally via prepended structured_context
        context_str = json.dumps(structured_context, indent=2)
        enriched_message = (
            f"[STRUCTURED LIVE QUALITY DATA]\n{context_str}\n\n"
            f"[USER QUERY]\n{user_query}"
        )
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": enriched_message}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Quality AI Inference failed: {e}")
            return "I am currently unable to run causal diagnostics due to an inference error."
