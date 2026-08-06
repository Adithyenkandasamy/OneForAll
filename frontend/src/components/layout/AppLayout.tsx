"use client";

import { usePathname, useRouter } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { useAuth } from "@/contexts/AuthContext";
import { useEffect } from "react";

export function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();

  const isLoginPage = pathname?.includes("/login") || false;

  useEffect(() => {
    if (!loading && !isAuthenticated && !isLoginPage) {
      router.push("/login");
    }
  }, [loading, isAuthenticated, isLoginPage, router]);

  if (loading) {
    return <div className="flex items-center justify-center h-screen w-full bg-zinc-950 text-white">Loading application...</div>;
  }

  if (isLoginPage) {
    return <>{children}</>;
  }

  return (
    <div className="flex h-screen bg-[#F5F5F5] font-sans text-[#111111] overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
