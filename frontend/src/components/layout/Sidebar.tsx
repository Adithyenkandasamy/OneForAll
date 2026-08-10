"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Factory,
  Cpu,
  Activity,
  AlertTriangle,
  Boxes,
  LineChart,
  Users,
  LogOut,
  UserCircle,
  BrainCircuit
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";

const navItems = [
  { name: "Central AI", href: "/ai", icon: BrainCircuit },
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Plants", href: "/plants", icon: Factory },
  { name: "Machines", href: "/machines", icon: Cpu },
  { name: "Monitoring", href: "/monitoring", icon: Activity },
  { name: "Predictive Maint.", href: "/maintenance", icon: AlertTriangle },
  { name: "Inventory", href: "/inventory", icon: Boxes },
  { name: "Analytics", href: "/analytics", icon: LineChart },
  { name: "Team", href: "/team", icon: Users },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="w-64 border-r bg-white h-screen sticky top-0 flex flex-col hidden md:flex shrink-0">
      <div className="h-16 flex items-center px-6 border-b">
        <div className="font-bold text-lg tracking-tight">OneForAll  AI</div>
      </div>
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (pathname.startsWith(item.href) && item.href !== "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive
                  ? "bg-black text-white"
                  : "text-gray-600 hover:bg-gray-100 hover:text-black"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* User Profile & Logout section */}
      {user && (
        <div className="p-4 border-t flex flex-col space-y-3">
          <div className="flex items-center gap-3 px-2">
            <div className="bg-zinc-100 p-2 rounded-full">
              <UserCircle className="h-5 w-5 text-zinc-600" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold truncate max-w-[140px] text-zinc-800">{user.full_name}</span>
              <span className="text-xs text-zinc-500 uppercase tracking-wider">{user.role}</span>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="w-full justify-start text-zinc-600 hover:text-black hover:bg-zinc-100 transition-colors"
            onClick={() => logout()}
          >
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      )}

      <div className="p-4 border-t text-xs text-gray-500 text-center">
        © 2026 OneForAll  Corp.
      </div>
    </aside>
  );
}
