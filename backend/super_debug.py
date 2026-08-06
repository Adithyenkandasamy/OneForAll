import asyncio
import sys
from app.agents.quality.services.service import QualityService

async def main():
    print("Initializing QualityService...", flush=True)
    try:
        service = QualityService()
        print("Fetching state...", flush=True)
        data = await service.get_dashboard_state()
        print(f"Data: {data}", flush=True)
    except Exception as e:
        print(f"FAILED WITH Exception: {e}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    print("Starting super_debug.py", flush=True)
    asyncio.run(main())
    print("Done super_debug.py", flush=True)
