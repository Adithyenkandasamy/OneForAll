import React, { useState, useEffect } from "react";
import { Search, Menu } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import api from "@/lib/api";
import { NotificationDropdown } from "./NotificationDropdown";

export function Header() {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const checkUnread = async () => {
      try {
        const res = await api.get("/api/v1/notifications", {
          params: { unread_only: true, limit: 100 },
        });
        setUnreadCount((res.data || []).length);
      } catch (err) {
        // Silent fail for background poller
      }
    };

    checkUnread();
    const interval = setInterval(checkUnread, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 border-b bg-white flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-4">
        <button className="md:hidden">
          <Menu className="h-5 w-5" />
        </button>
        <div className="relative hidden sm:block w-96">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
          <Input
            type="search"
            placeholder="Search commands, machines, or alerts... (Ctrl+K)"
            className="pl-9 bg-gray-50/50 border-gray-200 focus-visible:ring-black h-9"
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <NotificationDropdown unreadCount={unreadCount} onCountChange={setUnreadCount} />
        <div className="h-8 w-px bg-gray-200 mx-1" />
        <Avatar className="h-8 w-8 cursor-pointer">
          <AvatarImage src="https://github.com/shadcn.png" />
          <AvatarFallback>AD</AvatarFallback>
        </Avatar>
      </div>
    </header>
  );
}
