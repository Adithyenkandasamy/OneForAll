import asyncio
from app.agents.inventory.service import InventoryService
from app.agents.inventory.agent import InventoryAgent
async def run():
    agent = InventoryAgent()
    svc = InventoryService(agent=agent, gateway=None)
    # mock gateway so we don't need real google sheets for this test
    # wait, get_health calls fetch_all_rows which uses gateway, I need real gateway.
    from app.agents.inventory.mcp_tools import SheetsMcpGateway
    svc = InventoryService(agent=agent, gateway=SheetsMcpGateway())
    res = await svc.answer("Hello", user_id="123", role="admin", conversation_id=None)
    print("AI RESPONSE:", res["content"])
asyncio.run(run())
