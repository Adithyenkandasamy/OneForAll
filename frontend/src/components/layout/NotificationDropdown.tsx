"use client";

import React, { useState, useEffect, useRef } from "react";
import { Bell, Check, X } from "lucide-react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

interface Notification {
  id: string;
  kind: string;
  title: string;
  body: string;
  payload?: { link?: string; [key: string]: any } | null;
  is_read: boolean;
  created_at: string;
}

interface NotificationDropdownProps {
  unreadCount: number;
  onCountChange: (count: number) => void;
}

export function NotificationDropdown({ unreadCount, onCountChange }: NotificationDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen]);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const res = await api.get("/api/v1/notifications", { params: { limit: 20 } });
      setNotifications(res.data || []);
    } catch (err) {
      console.error("Failed to fetch notifications", err);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (ids: string[]) => {
    try {
      await api.post("/api/v1/notifications/read", { ids });
      setNotifications((prev) =>
        prev.map((n) => (ids.includes(n.id) ? { ...n, is_read: true } : n))
      );
      onCountChange(Math.max(0, unreadCount - ids.length));
    } catch (err) {
      console.error("Failed to mark as read", err);
    }
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.is_read) {
      markAsRead([notification.id]);
    }
    const link = notification.payload?.link;
    if (link) {
      router.push(link);
    }
    setIsOpen(false);
  };

  const getKindColor = (kind: string) => {
    switch (kind.toLowerCase()) {
      case "critical":
      case "stockout":
        return "bg-red-100 text-red-600";
      case "warning":
      case "low_stock":
        return "bg-yellow-100 text-yellow-600";
      case "info":
      default:
        return "bg-blue-100 text-blue-600";
    }
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`relative p-2 rounded-lg transition-colors ${
          unreadCount > 0
            ? "text-red-500 hover:bg-red-50"
            : "text-gray-500 hover:bg-gray-100"
        }`}
      >
        <Bell className={`h-5 w-5 ${unreadCount > 0 ? "animate-pulse" : ""}`} />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white border border-gray-200 rounded-xl shadow-2xl z-50 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50">
            <h3 className="font-semibold text-gray-900 text-sm">Notifications</h3>
            {unreadCount > 0 && (
              <button
                onClick={() => {
                  const unreadIds = notifications.filter((n) => !n.is_read).map((n) => n.id);
                  if (unreadIds.length > 0) markAsRead(unreadIds);
                }}
                className="text-xs text-blue-600 hover:text-blue-800 font-medium"
              >
                Mark all read
              </button>
            )}
          </div>

          <div className="max-h-80 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-gray-500 text-sm">Loading...</div>
            ) : notifications.length === 0 ? (
              <div className="p-6 text-center text-gray-400">
                <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No notifications yet</p>
              </div>
            ) : (
              notifications.map((notification) => (
                <button
                  key={notification.id}
                  onClick={() => handleNotificationClick(notification)}
                  className={`w-full text-left px-4 py-3 border-b border-gray-50 hover:bg-gray-50 transition-colors ${
                    !notification.is_read ? "bg-blue-50/50" : ""
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`mt-0.5 p-1.5 rounded-full ${getKindColor(notification.kind)}`}>
                      <Bell className="h-3 w-3" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {notification.title}
                        </p>
                        {!notification.is_read && (
                          <span className="h-2 w-2 rounded-full bg-blue-500 shrink-0" />
                        )}
                      </div>
                      {notification.body && (
                        <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                          {notification.body}
                        </p>
                      )}
                      <p className="text-xs text-gray-400 mt-1">
                        {formatTime(notification.created_at)}
                      </p>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>

          {notifications.length > 0 && (
            <div className="px-4 py-2 border-t border-gray-100 bg-gray-50">
              <button
                onClick={() => {
                  setIsOpen(false);
                  router.push("/settings");
                }}
                className="w-full text-center text-xs text-blue-600 hover:text-blue-800 font-medium"
              >
                View all notifications
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
