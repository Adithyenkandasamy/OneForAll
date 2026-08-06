with open("/home/adhi/Adhii/OneForAll/backend/app/api/router.py", "r") as f:
    text = f.read()

# Add to include_agent_routers
if "quality_router" not in text or "root.include_router(quality_router" not in text:
    if "root.include_router(executive_router, prefix=prefix)" in text:
        text = text.replace(
            "root.include_router(executive_router, prefix=prefix)",
            "root.include_router(executive_router, prefix=prefix)\n    root.include_router(quality_router, prefix=f\"{prefix}/agents/quality\")"
        )
        
with open("/home/adhi/Adhii/OneForAll/backend/app/api/router.py", "w") as f:
    f.write(text)
