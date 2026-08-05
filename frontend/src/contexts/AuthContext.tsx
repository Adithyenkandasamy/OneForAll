"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

interface User {
    id: string;
    email: string;
    full_name: string;
    role: string;
    is_active: boolean;
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (access: string, refresh: string) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const initAuth = async () => {
            const token = Cookies.get("access_token");
            if (token) {
                try {
                    const res = await api.get("/api/v1/auth/me");
                    setUser(res.data);
                } catch (err) {
                    console.error("Failed to load user session", err);
                    Cookies.remove("access_token");
                    Cookies.remove("refresh_token");
                }
            }
            setLoading(false);
        };

        initAuth();
    }, []);

    const login = async (access: string, refresh: string) => {
        Cookies.set("access_token", access, { expires: 1 });
        Cookies.set("refresh_token", refresh, { expires: 7 });

        try {
            const res = await api.get("/api/v1/auth/me");
            setUser(res.data);
        } catch (err) {
            console.error("Failed to fetch user immediately after login", err);
        }
    };

    const logout = () => {
        Cookies.remove("access_token");
        Cookies.remove("refresh_token");
        setUser(null);
        router.push("/login"); // default redirect, admin might be redirected to /admin/login though
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, isAuthenticated: !!user }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
