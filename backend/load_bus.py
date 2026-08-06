with open("/home/adhi/Adhii/OneForAll/backend/app/main.py", "r") as f:
    main_code = f.read()

import_hook = '''
# Import domain services that execute background hooks on the generic event bus
try:
    import app.agents.inventory.services.notification_service  # registers itself on the bus
except ImportError as e:
    pass
'''

if "app.agents.inventory.services.notification_service" not in main_code:
    # Just inject it after the routers
    main_code = main_code.replace('app.include_router(inventory_router, prefix="/api/v1")', 'app.include_router(inventory_router, prefix="/api/v1")\n' + import_hook)
    
    with open("/home/adhi/Adhii/OneForAll/backend/app/main.py", "w") as f:
        f.write(main_code)
