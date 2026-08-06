import asyncio
from app.agents.executive.service import ExecutiveService
async def run():
    svc = ExecutiveService()
    res = await svc.answer("Can you tell me about the risk having stocks in the inventory?", user_id="123", role="admin", conversation_id=None)
    print(res["content"])
asyncio.run(run())
