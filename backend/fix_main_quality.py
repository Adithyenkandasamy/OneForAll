with open("/home/adhi/Adhii/OneForAll/backend/app/main.py", "r") as f:
    text = f.read()

# Make sure to import the router and polling_service
imports = """
from app.agents.quality.api.router import quality_router
from app.agents.quality.scheduler.polling_service import polling_service
import asyncio
"""

if "from app.agents.quality.api.router import quality_router" not in text:
    text = text.replace("import asyncio", imports)

# Add the lifecycle hooks for the polling scheduler
if "polling_service_task = asyncio.create_task(polling_service.run())" not in text:
    text = text.replace("yield", "polling_service_task = asyncio.create_task(polling_service.run())\n    yield\n    await polling_service.stop()")
    
# Add the router
if 'app.include_router(quality_router, prefix="/api/v1/agents/quality")' not in text:
    text = text.replace("app.include_router(inventory_router, prefix=\"/api/v1\")", "app.include_router(inventory_router, prefix=\"/api/v1\")\n    app.include_router(quality_router, prefix=\"/api/v1/agents/quality\")")

with open("/home/adhi/Adhii/OneForAll/backend/app/main.py", "w") as f:
    f.write(text)
