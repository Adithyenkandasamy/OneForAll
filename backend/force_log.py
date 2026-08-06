with open("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/scheduler/polling_service.py", "r") as f:
    text = f.read()

text = text.replace(
    'logger.error(f"Polling cycle failed: {e}")',
    'logger.error(f"Polling cycle failed: {e}"); import traceback; open("poll_crash.log", "w").write(traceback.format_exc())'
)

with open("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/scheduler/polling_service.py", "w") as f:
    f.write(text)
