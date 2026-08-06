import re
import os

print("Reverting page.tsx...")
# 1. page.tsx
with open("/home/adhi/Adhii/OneForAll/frontend/src/app/inventory/page.tsx", "r") as f:
    page = f.read()

# Replace SSE block with simple load
sse_effect = '''  useEffect(() => {
    // Initial fetch
    loadInventory();

    // Zero-latency Server-Sent Events from Sync Microservice
    const sse = new EventSource("http://localhost:8000/api/v1/agents/inventory/stream");
    
    sse.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data);
        if (payload.materials && payload.materials.length > 0) {
          setInventory(payload.materials);
        }
      } catch (err) { }
    };
    
    return () => sse.close();
  }, []);'''
  
normal_effect = '''  useEffect(() => {
    loadInventory();
  }, []);'''
page = page.replace(sse_effect, normal_effect)

# Put the Sync Button back
button_target = '''        <div className="flex gap-4">
          <div className="relative">'''
restore_button = '''        <div className="flex gap-4">
          <Button variant="outline" onClick={() => loadInventory(false)} disabled={loading || updating}>
            {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Sparkles className="h-4 w-4 mr-2 text-indigo-500" />}
            Sync Master Sheet
          </Button>
          <div className="relative">'''
if restore_button not in page:
    page = page.replace(button_target, restore_button)
          
with open("/home/adhi/Adhii/OneForAll/frontend/src/app/inventory/page.tsx", "w") as f:
    f.write(page)

print("Reverting Header.tsx...")
# 2. Header.tsx
with open("/home/adhi/Adhii/OneForAll/frontend/src/components/layout/Header.tsx", "r") as f:
    header = f.read()

header_sse = '''  useEffect(() => {
    const sse = new EventSource("http://localhost:8000/api/v1/agents/inventory/stream");
    sse.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data);
        if (payload.risks !== undefined) {
          setRiskCount(payload.risks);
        }
      } catch (err) { }
    };
    return () => sse.close();
  }, []);'''

header_normal = '''  useEffect(() => {
    const checkRisks = async () => {
      try {
        const res = await api.get("/api/v1/agents/inventory/materials");
        const highRisk = (res.data || []).filter((item: any) => 
          (item.risk_level || "").toLowerCase() === "high"
        );
        setRiskCount(highRisk.length);
      } catch (err) {}
    };
    checkRisks();
  }, []);'''

header = header.replace(header_sse, header_normal)
with open("/home/adhi/Adhii/OneForAll/frontend/src/components/layout/Header.tsx", "w") as f:
    f.write(header)

print("Reverting Backend Router...")
# 3. backend router
with open("/home/adhi/Adhii/OneForAll/backend/app/agents/inventory/router.py", "r") as f:
    router = f.read()

# using regex to yank out the stream_inventory block and imports
import re
router = re.sub(r'from sse_starlette\.sse import EventSourceResponse\nimport json\nimport asyncio\n', '', router)
router = re.sub(r'@router\.get\("/stream"\)[\s\S]*?return EventSourceResponse\(event_generator\(\)\)\n', '', router)

with open("/home/adhi/Adhii/OneForAll/backend/app/agents/inventory/router.py", "w") as f:
    f.write(router)

print("Done")
