"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { ShieldAlert, Server, Loader2, ArrowLeft } from "lucide-react";

export default function AdminLoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const router = useRouter();
    const { login } = useAuth();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError("");

        try {
            const res = await api.post("/api/v1/auth/login", { email, password });

            const meRes = await api.get("/api/v1/auth/me", {
                headers: { Authorization: `Bearer ${res.data.access_token}` }
            });

            if (meRes.data.role !== "admin") {
                setError("AUTHENTICATION FAILED: Insufficient privileges for this portal.");
                setIsSubmitting(false);
                return;
            }

            await login(res.data.access_token, res.data.refresh_token);
            router.push("/dashboard");
        } catch (err: any) {
            if (err.response?.status === 401) {
                setError("Invalid secure credentials provided.");
            } else {
                setError("System offline. Please contact IT support.");
            }
            setIsSubmitting(false);
        }
    };

    return (
        <div className="flex min-h-screen w-full flex-col items-center justify-center p-4">
            {/* Background patterns */}
            <div className="absolute inset-0 z-[-1] bg-background">
                <div className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80">
                    <div className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-destructive/20 to-destructive/5 opacity-30 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]" />
                </div>
                <div className="absolute inset-0 bg-[linear-gradient(to_right,#80000010_1px,transparent_1px),linear-gradient(to_bottom,#80000010_1px,transparent_1px)] bg-[size:4rem_4rem]"></div>
            </div>

            <div className="flex flex-col space-y-6 w-full max-w-[420px]">
                {/* Admin Login Terminal Card */}
                <Card className="w-full shadow-2xl border-destructive/30 bg-card overflow-hidden">

                    {/* Top warning bar */}
                    <div className="h-1.5 w-full bg-destructive" />

                    <CardHeader className="space-y-4 pt-8 text-center pb-4">
                        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-xl bg-destructive/10 border border-destructive/20 text-destructive">
                            <ShieldAlert className="w-7 h-7" />
                        </div>
                        <div>
                            <CardTitle className="text-2xl font-bold tracking-widest uppercase">
                                Nexus <span className="text-destructive">Admin</span>
                            </CardTitle>
                            <CardDescription className="text-muted-foreground font-mono mt-2 text-xs tracking-widest uppercase">
                                Restricted clearance level required
                            </CardDescription>
                        </div>
                    </CardHeader>

                    <CardContent className="px-8 pb-8 pt-2">
                        <form onSubmit={handleLogin} className="space-y-5">
                            <div className="space-y-2">
                                <label className="flex items-center justify-between text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground ml-1" htmlFor="email">
                                    <span>Identification</span>
                                    <Server className="w-3 h-3 text-destructive/70" />
                                </label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="admin@oneforall.ai"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    className="font-mono focus-visible:ring-destructive"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="block text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground ml-1" htmlFor="password">
                                    Security Passkey
                                </label>
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="••••••••••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    className="font-mono tracking-widest focus-visible:ring-destructive"
                                />
                            </div>

                            {error && (
                                <div className="text-[11px] font-mono tracking-wide p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-md flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-destructive animate-ping shrink-0" />
                                    <span>{error}</span>
                                </div>
                            )}

                            <Button
                                type="submit"
                                variant="destructive"
                                className="w-full h-10 tracking-widest text-xs font-bold uppercase"
                                disabled={isSubmitting}
                            >
                                {isSubmitting ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Decrypting...
                                    </>
                                ) : (
                                    "Initialize Connection"
                                )}
                            </Button>
                        </form>
                    </CardContent>

                    <CardFooter className="flex justify-between border-t border-border bg-muted/30 py-4 px-8">
                        <p className="text-[10px] text-muted-foreground font-mono tracking-widest">SECURE_NODE</p>
                        <a href="/login" className="flex items-center text-[10px] text-muted-foreground hover:text-foreground font-mono tracking-wider uppercase transition-colors">
                            <ArrowLeft className="w-3 h-3 mr-1" />
                            Exit
                        </a>
                    </CardFooter>
                </Card>
            </div>
        </div>
    );
}
