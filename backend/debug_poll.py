import asyncio
import httpx
from app.agents.quality.scheduler.polling_service import QualityPollingService

async def main():
    s = QualityPollingService()
    async with httpx.AsyncClient() as client:
        await s._cycle(client)
    
if __name__ == "__main__":
    asyncio.run(main())
