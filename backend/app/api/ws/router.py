import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.shared.events import bus
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.websocket("/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    await websocket.accept()
    logger.info("New Dashboard WebSocket connection established.")
    
    queue = asyncio.Queue()

    async def event_listener(payload: dict):
        await queue.put(payload)

    # Subscribe strictly to the internal memory bus topic published by the MQTT Consumer
    bus.subscribe("quality:updated", event_listener)

    try:
        while True:
            # Await the next telemetry item off the Fast queue
            payload = await queue.get()
            # Push block directly to React frontend
            await websocket.send_json(payload)
    except WebSocketDisconnect:
        logger.info("Dashboard WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket fatal error: {e}")
    finally:
        # Cleanup memory leak risk on UI tab closures
        try:
            bus._subscribers["quality:updated"].remove(event_listener)
        except ValueError:
            pass
