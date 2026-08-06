with open("/home/adhi/Adhii/OneForAll/frontend/src/app/inventory/page.tsx", "r") as f:
    page = f.read()

page = page.replace('EventSource("http://localhost:8001/stream")', 'EventSource("http://localhost:8000/api/v1/agents/inventory/stream")')

with open("/home/adhi/Adhii/OneForAll/frontend/src/app/inventory/page.tsx", "w") as f:
    f.write(page)

with open("/home/adhi/Adhii/OneForAll/frontend/src/components/layout/Header.tsx", "r") as f:
    header = f.read()

header = header.replace('EventSource("http://localhost:8001/stream")', 'EventSource("http://localhost:8000/api/v1/agents/inventory/stream")')

with open("/home/adhi/Adhii/OneForAll/frontend/src/components/layout/Header.tsx", "w") as f:
    f.write(header)
