import re
print("Fixing page.tsx...")
with open("/home/adhi/Adhii/OneForAll/frontend/src/app/inventory/page.tsx", "r") as f:
    page = f.read()

# Replace EVERYTHING in the useEffect block accurately
page = re.sub(r'  useEffect\(\(\) => \{\n.*?return \(\) => sse\.close\(\);\n  \}, \[\]\);', '''  useEffect(() => {
    loadInventory();
    const interval = setInterval(() => {
      loadInventory(true);
    }, 10000);
    return () => clearInterval(interval);
  }, []);''', page, flags=re.DOTALL)

with open("/home/adhi/Adhii/OneForAll/frontend/src/app/inventory/page.tsx", "w") as f:
    f.write(page)


print("Fixing Header.tsx...")
with open("/home/adhi/Adhii/OneForAll/frontend/src/components/layout/Header.tsx", "r") as f:
    header = f.read()

header = re.sub(r'  useEffect\(\(\) => \{\n.*?return \(\) => sse\.close\(\);\n  \}, \[\]\);', '''  useEffect(() => {
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
    const interval = setInterval(checkRisks, 10000);
    return () => clearInterval(interval);
  }, []);''', header, flags=re.DOTALL)

with open("/home/adhi/Adhii/OneForAll/frontend/src/components/layout/Header.tsx", "w") as f:
    f.write(header)

print("Done")
