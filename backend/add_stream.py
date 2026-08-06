import os
import sys

with open("/home/adhi/Adhii/OneForAll/backend/app/agents/inventory/router.py", "r") as f:
    text = f.read()

header = """from sse_starlette.sse import EventSourceResponse
import json
import asyncio
"""

if "EventSourceResponse" not in text:
    text = text.replace("from fastapi import APIRouter, Depends, Query", header + "from fastapi import APIRouter, Depends, Query")

stream_route = """
@router.get("/stream")
async def stream_inventory(
    service: InventoryService = Depends(get_inventory_service),
):
    async def event_generator():
        last_data = ""
        while True:
            try:
                materials = await service.get_enriched_materials()
                risks = sum(1 for m in materials if dict(m).get("risk_level", "").upper() == "HIGH")
                payload = json.dumps({"materials": [dict(m) for m in materials], "risks": risks})
                if payload != last_data:
                    last_data = payload
                    yield {"event": "inventory_update", "data": payload}
            except Exception as e:
                pass # suppress stream drop logs
            await asyncio.sleep(15)
            
    return EventSourceResponse(event_generator())
"""

if "@router.get(\"/stream\")" not in text:
    text += stream_route

with open("/home/adhi/Adhii/OneForAll/backend/app/agents/inventory/router.py", "w") as f:
    f.write(text)
