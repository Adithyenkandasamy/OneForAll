"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Fingerprint, Loader2, KeyRound } from "lucide-react";

export default function UserLoginPage() {
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
            await login(res.data.access_token, res.data.refresh_token);
            router.push("/");
        } catch (err: any) {
            if (err.response?.status === 401) {
                setError("Invalid email or password");
            } else {
                setError("Failed to login. Please try again.");
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="flex min-h-screen w-full flex-col items-center justify-center p-4">
            {/* Background patterns */}
            <div className="absolute inset-0 z-[-1] bg-background">
                <div className="absolute inset-x-0 -top-40 -z-10 transform-gpu overflow-hidden blur-3xl sm:-top-80">
                    <div className="relative left-[calc(50%-11rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 rotate-[30deg] bg-gradient-to-tr from-primary/20 to-primary/5 opacity-30 sm:left-[calc(50%-30rem)] sm:w-[72.1875rem]" />
                </div>
            </div>

            <div className="flex flex-col space-y-6 w-full max-w-[400px]">

                {/* Branding header */}
                <div className="flex items-center justify-center space-x-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold">
                        O
                    </div>
                    <span className="text-xl font-semibold tracking-tight">OneForAll  AI</span>
                </div>

                <Card className="w-full shadow-lg border-border bg-card">
                    <CardHeader className="space-y-2 text-center pb-6">
                        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 mb-2">
                            <Fingerprint className="h-6 w-6 text-primary" />
                        </div>
                        <CardTitle className="text-2xl font-semibold tracking-tight">
                            Welcome back
                        </CardTitle>
                        <CardDescription className="text-muted-foreground text-sm mx-auto max-w-xs">
                            Securely authenticate to access your enterprise dashboard.
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="px-6 pb-6">
                        <form onSubmit={handleLogin} className="space-y-4">
                            <div className="space-y-2 text-left">
                                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground" htmlFor="email">
                                    Email Address
                                </label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="operator@company.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    autoComplete="email"
                                />
                            </div>
                            <div className="space-y-2 text-left">
                                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground" htmlFor="password">
                                    Password
                                </label>
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="••••••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    autoComplete="current-password"
                                />
                            </div>

                            {error && (
                                <div className="rounded-md bg-destructive/15 border border-destructive/20 p-3 text-sm text-destructive font-medium text-center">
                                    {error}
                                </div>
                            )}

                            <Button
                                type="submit"
                                className="w-full h-10 mt-2"
                                disabled={isSubmitting}
                            >
                                {isSubmitting ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Authenticating
                                    </>
                                ) : (
                                    "Sign In"
                                )}
                            </Button>
                        </form>
                    </CardContent>

                    <CardFooter className="flex justify-center border-t border-border bg-muted/20 px-6 py-4">
                        <p className="text-xs text-muted-foreground flex gap-1 items-center">
                            Administrative personnel?
                            <a href="/admin/login" className="text-primary hover:underline transition-colors flex items-center font-medium ml-1">
                                Go to Admin Portal
                                <KeyRound className="w-3 h-3 ml-1" />
                            </a>
                        </p>
                    </CardFooter>
                </Card>
            </div>

        </div>
    );
}
