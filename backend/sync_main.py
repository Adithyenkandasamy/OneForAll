"""Standalone Microservice for Zero-Latency SSE Inventory Propagation."""
import asyncio
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from app.agents.inventory.mcp_tools import SheetsMcpGateway
from app.agents.inventory.services.rule_engine import RuleEngine

app = FastAPI(title="Inventory Sync Microservice")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gateway = SheetsMcpGateway()
rule_engine = RuleEngine()

# Global state for latest cached data string to prevent redundant network spam
LATEST_DATA_JSON = ""
LATEST_RISK_COUNT = 0

async def sse_format():
    global LATEST_DATA_JSON
    while True:
        if LATEST_DATA_JSON:
            yield {"event": "inventory_update", "data": LATEST_DATA_JSON}
        await asyncio.sleep(2)

@app.get("/stream")
async def stream():
    """EventSource endpoint for infinite Server-Sent Events."""
    return EventSourceResponse(sse_format())

@app.on_event("startup")
async def startup_event():
    """Start the background daemon loop."""
    asyncio.create_task(sync_worker())

async def sync_worker():
    global LATEST_DATA_JSON
    global LATEST_RISK_COUNT
    while True:
        try:
            # Bypass the cache in the service layer and hit MCP directly
            raw_data = await gateway.call_tool("query_inventory", {"limit": 1000})
            if not isinstance(raw_data, list):
                raw_data = [raw_data] if isinstance(raw_data, dict) else []
            
            analyzed = rule_engine.analyze_all(raw_data)
            risks = sum(1 for m in analyzed if m.risk_level == "HIGH")
            
            new_json = json.dumps({
                "materials": [m.__dict__ for m in analyzed],
                "risks": risks
            })
            
            if new_json != LATEST_DATA_JSON:
                LATEST_DATA_JSON = new_json
                
        except Exception as e:
            print(f"Sync Worker Error: {e}")
        
        # Super aggressive tight polling for low-latency
        await asyncio.sleep(1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("sync_main:app", host="0.0.0.1", port=8001, reload=True)
