with open("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/scheduler/polling_service.py", "r") as f:
    text = f.read()

text = text.replace(
    'db_sensor = SensorData(**dto.model_dump())',
    '''dumped = dto.model_dump()
                dumped.pop("id", None)
                db_sensor = SensorData(**dumped)'''
)

with open("/home/adhi/Adhii/OneForAll/backend/app/agents/quality/scheduler/polling_service.py", "w") as f:
    f.write(text)
