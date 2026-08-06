with open("/home/adhi/Adhii/OneForAll/backend/app/api/router.py", "r") as f:
    text = f.read()

import_line = "from app.agents.quality.api.router import quality_router\n"
if "quality_router" not in text:
    text = import_line + text

hook_line = '    app.include_router(quality_router, prefix=f"{prefix}/agents/quality")\n'
if "agents/quality" not in text:
    text = text.replace("app.include_router(inventory_router", hook_line + "    app.include_router(inventory_router")

with open("/home/adhi/Adhii/OneForAll/backend/app/api/router.py", "w") as f:
    f.write(text)
