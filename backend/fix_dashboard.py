import re
import os

print("Updating Sidebar.tsx...")
sidebar_path = "/home/adhi/Adhii/OneForAll/frontend/src/components/layout/Sidebar.tsx"
with open(sidebar_path, "r") as f:
    sidebar = f.read()

# Change the Central AI to be above Dashboard
old_nav = '''const navItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Plants", href: "/plants", icon: Factory },
  { name: "Machines", href: "/machines", icon: Cpu },
  { name: "Monitoring", href: "/monitoring", icon: Activity },
  { name: "Predictive Maint.", href: "/maintenance", icon: AlertTriangle },
  { name: "Inventory", href: "/inventory", icon: Boxes },
  { name: "Central AI", href: "/ai", icon: BrainCircuit },
  { name: "Analytics", href: "/analytics", icon: LineChart },
  { name: "Team", href: "/team", icon: Users },
  { name: "Settings", href: "/settings", icon: Settings },
];'''

new_nav = '''const navItems = [
  { name: "Central AI", href: "/ai", icon: BrainCircuit },
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Plants", href: "/plants", icon: Factory },
  { name: "Machines", href: "/machines", icon: Cpu },
  { name: "Monitoring", href: "/monitoring", icon: Activity },
  { name: "Predictive Maint.", href: "/maintenance", icon: AlertTriangle },
  { name: "Inventory", href: "/inventory", icon: Boxes },
  { name: "Analytics", href: "/analytics", icon: LineChart },
  { name: "Team", href: "/team", icon: Users },
  { name: "Settings", href: "/settings", icon: Settings },
];'''

sidebar = sidebar.replace(old_nav, new_nav)
with open(sidebar_path, "w") as f:
    f.write(sidebar)

print("Updating Dashboard page.tsx...")
page_path = "/home/adhi/Adhii/OneForAll/frontend/src/app/page.tsx"
with open(page_path, "r") as f:
    page = f.read()

# Make the Dashboard functional with a 10s polling interval for Inventory
if "import { useEffect, useState } from \"react\";" not in page:
    page = page.replace("import { motion } from \"framer-motion\";", "import { useEffect, useState } from \"react\";\nimport { motion } from \"framer-motion\";\nimport api from \"@/lib/api\";")

# Add state and effect inside Dashboard
old_component = "export default function Dashboard() {"
new_component = '''export default function Dashboard() {
  const [criticalStock, setCriticalStock] = useState<any[]>([]);

  useEffect(() => {
    const fetchInventory = async () => {
      try {
        const res = await api.get("/api/v1/agents/inventory/materials");
        const highRisk = (res.data || []).filter((item: any) => 
          (item.risk_level || "").toLowerCase() === "high"
        );
        setCriticalStock(highRisk);
      } catch (err) {}
    };
    
    fetchInventory();
    const interval = setInterval(fetchInventory, 10000); // 10s auto-sync
    return () => clearInterval(interval);
  }, []);
'''

if "const [criticalStock" not in page:
    page = page.replace(old_component, new_component)


# Find the Active Alerts card and insert the Critical Stock alerts underneath it or inside it
alerts_block = '''            <CardContent className="p-0">
              {alerts.map((alert, index) => (
                <div 
                  key={alert.id}
                  className={cn(
                    "p-4 flex gap-4 items-start transition-colors hover:bg-gray-50",
                    index !== alerts.length - 1 && "border-b border-gray-100"
                  )}
                >
                  <div className={cn(
                    "mt-0.5 p-2 rounded-full shrink-0",
                    alert.type === "critical" ? "bg-red-50 text-red-600" :
                    alert.type === "warning" ? "bg-amber-50 text-amber-600" :
                    "bg-blue-50 text-blue-600"
                  )}>
                    {alert.type === "critical" && <AlertTriangle className="h-4 w-4" />}
                    {alert.type === "warning" && <Activity className="h-4 w-4" />}
                    {alert.type === "info" && <CheckCircle2 className="h-4 w-4" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                    <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>'''

import_cn = "import { cn } from \"@/lib/utils\";\n"
if "import { cn }" not in page:
    page = page.replace("import { motion }", import_cn + "import { motion }")
    # Also add Package to lucide-react if needed:
    page = page.replace("CheckCircle2,", "CheckCircle2,\n  Package,")

new_alerts_block = '''            <CardContent className="p-0">
              {alerts.map((alert, index) => (
                <div 
                  key={alert.id}
                  className={cn(
                    "p-4 flex gap-4 items-start transition-colors hover:bg-gray-50",
                    index !== alerts.length - 1 && "border-b border-gray-100"
                  )}
                >
                  <div className={cn(
                    "mt-0.5 p-2 rounded-full shrink-0",
                    alert.type === "critical" ? "bg-red-50 text-red-600" :
                    alert.type === "warning" ? "bg-amber-50 text-amber-600" :
                    "bg-blue-50 text-blue-600"
                  )}>
                    {alert.type === "critical" && <AlertTriangle className="h-4 w-4" />}
                    {alert.type === "warning" && <Activity className="h-4 w-4" />}
                    {alert.type === "info" && <CheckCircle2 className="h-4 w-4" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                    <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
                  </div>
                </div>
              ))}
              
              {/* Dynamic Inventory Risk Overrides */}
              {criticalStock.map((stock, idx) => (
                <div 
                  key={`stock-${idx}`}
                  className="p-4 flex gap-4 items-start transition-colors hover:bg-red-50 border-t border-gray-100 bg-red-50/30"
                >
                  <div className="mt-0.5 p-2 rounded-full shrink-0 bg-red-100 text-red-600">
                    <Package className="h-4 w-4" />
                  </div>
                  <div className="w-full">
                    <div className="flex justify-between w-full">
                      <p className="text-sm font-medium text-red-900">{stock.material} Stockout Risk</p>
                      <Badge variant="destructive">HIGH</Badge>
                    </div>
                    <p className="text-xs text-red-600 mt-1">
                      Current Stock: {stock.current_stock} | Min: {stock.minimum_stock}
                    </p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>'''

page = page.replace(alerts_block, new_alerts_block)

with open(page_path, "w") as f:
    f.write(page)

print("Done")
