with open("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/scheduler/polling_service.py", "r") as f:
    text = f.read()

text = text.replace(
    'logger.debug(f"Polled {len(raw_rows)} telemetry frames successfully.")',
    'logger.debug(f"Polled {len(raw_rows)} telemetry frames successfully."); open("I_RAN.txt", "w").write("YES " + str(len(raw_rows)))'
)

with open("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/scheduler/polling_service.py", "w") as f:
    f.write(text)
