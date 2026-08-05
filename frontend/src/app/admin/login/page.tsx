"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { ServerIcon } from "lucide-react";

export default function AdminLoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const router = useRouter();
    const { login, logout } = useAuth();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError("");

        try {
            const res = await api.post("/api/v1/auth/login", { email, password });

            // Before setting global context, verify role manually
            const meRes = await api.get("/api/v1/auth/me", {
                headers: { Authorization: `Bearer ${res.data.access_token}` }
            });

            if (meRes.data.role !== "admin") {
                setError("Unauthorized: Administrator privileges required.");
                setIsSubmitting(false);
                return;
            }

            await login(res.data.access_token, res.data.refresh_token);
            router.push("/settings"); // Example admin route, adjust as needed
        } catch (err: any) {
            if (err.response?.status === 401) {
                setError("Invalid email or password");
            } else {
                setError("Failed to login to admin portal.");
            }
            setIsSubmitting(false);
        }
    };

    return (
        <div className="flex h-screen w-full items-center justify-center bg-black p-4">
            <Card className="w-full max-w-md bg-zinc-950 border-zinc-800 text-zinc-100 shadow-2xl relative overflow-hidden">
                {/* Decorative elements for admin feel */}
                <div className="absolute top-0 w-full h-1 bg-gradient-to-r from-red-600 to-orange-500" />

                <CardHeader className="space-y-2 flex flex-col items-center pt-8">
                    <div className="p-3 bg-red-500/10 rounded-full mb-2 text-red-500">
                        <ServerIcon className="w-8 h-8" />
                    </div>
                    <CardTitle className="text-2xl font-bold tracking-tight text-center">System Administration</CardTitle>
                    <CardDescription className="text-zinc-500 text-center">
                        Restricted access. Authorized personnel only.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleLogin} className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400" htmlFor="email">
                                Admin Email
                            </label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="admin@internal.systems"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                className="bg-black border-zinc-carbon border-zinc-800 focus-visible:ring-red-500"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400" htmlFor="password">
                                Security Passkey
                            </label>
                            <Input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="bg-black border-zinc-800 focus-visible:ring-red-500"
                            />
                        </div>
                        {error && <div className="text-sm p-3 bg-red-950/50 border border-red-900 text-red-400 font-medium rounded-md text-center">{error}</div>}
                        <Button type="submit" className="w-full bg-red-600 hover:bg-red-700 text-white shadow-lg shadow-red-900/20" disabled={isSubmitting}>
                            {isSubmitting ? "Authenticating..." : "Authorize Access"}
                        </Button>
                    </form>
                </CardContent>
                <CardFooter className="flex justify-center border-t border-zinc-900 pt-4 mt-4">
                    <p className="text-xs text-zinc-600">
                        Not an admin? <a href="/login" className="text-zinc-400 hover:text-zinc-200 transition-colors">Return to standard login</a>
                    </p>
                </CardFooter>
            </Card>
        </div>
    );
}
