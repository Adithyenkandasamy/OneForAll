with open("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/scheduler/polling_service.py", "r") as f:
    text = f.read()

text = text.replace(
    'await session.commit()',
    'print("Committing DB...", flush=True); await session.commit(); print("DB COMMITTED", flush=True)'
)
text = text.replace(
    'status_obj = await session.get(MachineStatus, m_id)',
    'print("Getting machine...", flush=True); status_obj = await session.get(MachineStatus, m_id)'
)

with open("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/scheduler/polling_service.py", "w") as f:
    f.write(text)
