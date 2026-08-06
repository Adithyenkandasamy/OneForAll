import asyncio
from app.agents.quality.services.service import QualityService

async def main():
    service = QualityService()
    try:
        data = await service.get_dashboard_state()
        print("SUCCESS:", data)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
