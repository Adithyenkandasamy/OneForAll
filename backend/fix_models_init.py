with open("/home/adhi/Adhii/OneForAll/backend/app/models/__init__.py", "r") as f:
    text = f.read()

import_line = "from app.agents.quality.models import SensorData, MachineStatus\n"
if "SensorData" not in text:
    text = text.replace("from app.models.user import User\n", "from app.models.user import User\n" + import_line)
    
if "SensorData" not in text:
    # If the replace failed for some reason
    pass
else:
    text = text.replace('"AuditLog",', '"AuditLog",\n    "SensorData",\n    "MachineStatus",')

with open("/home/adhi/Adhii/OneForAll/backend/app/models/__init__.py", "w") as f:
    f.write(text)

print("Updated __init__.py")
