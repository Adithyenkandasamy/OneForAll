import re
import os

print("Updating inventory service...")
with open("/home/adhi/Adhii/OneForAll/backend/app/agents/inventory/service.py", "r") as f:
    service = f.read()

# Add event bus import
if "from app.shared.events import bus" not in service:
    service = service.replace("from app.agents.inventory.services.health_engine import HealthEngine", "from app.agents.inventory.services.health_engine import HealthEngine\nfrom app.shared.events import bus")

# Remove InventoryNotificationService dependency
service = re.sub(r'from app\.agents\.inventory\.services\.notification_service import InventoryNotificationService\n', '', service)
# Update constructor
service = re.sub(r'notification_service: InventoryNotificationService \| None = None,\n\s*', '', service)
service = re.sub(r'self\._notification_service = notification_service or InventoryNotificationService\(\)\n\s*', '', service)

# Replace the notification call with an Event Bus publish
old_call = '''        # Step 4: Emit notifications for critical events (not the AI's job)
        try:
            await self._notification_service.check_and_notify(analyses, user_id=user_id)
        except Exception as exc:
            logger.warning("Notification emission failed", extra={"error": str(exc)})'''

new_call = '''        # Step 4: Publish domain event to the Internal Event Bus
        await bus.publish(
            "inventory:analyzed", 
            {"analyses": analyses, "user_id": user_id}
        )'''

service = service.replace(old_call, new_call)

with open("/home/adhi/Adhii/OneForAll/backend/app/agents/inventory/service.py", "w") as f:
    f.write(service)

print("Updating notification service to subscribe...")
with open("/home/adhi/Adhii/OneForAll/backend/app/agents/inventory/services/notification_service.py", "r") as f:
    notif = f.read()

if "from app.shared.events import bus" not in notif:
    header_block = "from app.shared.events import bus\nfrom typing import Any\n"
    notif = header_block + notif

# Add the listener hook at the bottom of the notification service
hook = """
async def _on_inventory_analyzed(payload: Any) -> None:
    analyses = payload.get("analyses", [])
    user_id = payload.get("user_id")
    if analyses and user_id:
        svc = InventoryNotificationService()
        await svc.check_and_notify(analyses, user_id=user_id)

bus.subscribe("inventory:analyzed", _on_inventory_analyzed)
"""
if "_on_inventory_analyzed" not in notif:
    notif += hook

with open("/home/adhi/Adhii/OneForAll/backend/app/agents/inventory/services/notification_service.py", "w") as f:
    f.write(notif)

# The hook needs to be loaded into the registry. The best place is app.main startup.
print("Done")
