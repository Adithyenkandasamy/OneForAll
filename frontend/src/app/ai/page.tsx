"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Send, Bot, User, BrainCircuit } from "lucide-react";
import api from "@/lib/api";

interface ChatMessage {
  id: string;
  role: "user" | "ai";
  content: string;
  timestamp?: Date;
}

export default function CentralAIPage() {
  const [chatQuery, setChatQuery] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: "intro",
      role: "ai",
      content: "Hello! I am OneForAll Copilot. I combine validated inventory, quality, maintenance, and production insights into clear recommendations. How can I help?",
      timestamp: new Date()
    }
  ]);
  const [chatLoading, setChatLoading] = useState(false);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [chatMessages, chatLoading]);

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatQuery.trim() || chatLoading) return;

    const userQuery = chatQuery.trim();
    setChatQuery("");
    setChatMessages((prev) => [...prev, { id: Date.now().toString(), role: "user", content: userQuery, timestamp: new Date() }]);
    setChatLoading(true);

    try {
      const response = await api.post<{
        content: string;
        conversation_id?: string | null;
      }>("/api/v1/agents/executive/chat", {
        query: userQuery,
        conversation_id: "oneforall-copilot",
      });
      setChatMessages((prev) => [
        ...prev,
        { id: (Date.now() + 1).toString(), role: "ai", content: response.data.content },
      ]);
    } catch {
      setChatMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "ai",
          content:
            "I could not reach the verified data service. No estimate or demonstration data was shown. Please try again after the backend is available.",
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="space-y-6 pb-12 w-full animate-in fade-in duration-500 h-full max-h-screen flex flex-col pt-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">OneForAll Copilot</h1>
          <p className="text-muted-foreground mt-1">Cross-domain operational insights and recommended actions.</p>
        </div>
        <Badge variant="outline" className="bg-indigo-500/10 text-indigo-500 border-indigo-500/20 px-3 py-1">
          <BrainCircuit className="w-3 h-3 mr-2 animate-pulse" />
          Verified data only
        </Badge>
      </div>

      <div className="flex-1 min-h-[500px]">
        <Card className="w-full h-full flex flex-col shadow-lg border-indigo-500/20 bg-gradient-to-b from-card to-indigo-950/5">
          <CardHeader className="py-4 border-b border-border/50 bg-indigo-500/5">
            <CardTitle className="text-md flex items-center gap-2">
              <div className="p-1.5 rounded-md bg-indigo-500/20 text-indigo-500">
                <Bot className="h-5 w-5" />
              </div>
              OneForAll Operations Copilot
            </CardTitle>
            <CardDescription className="text-xs">
              Combines domain results; deterministic services remain the source of operational facts.
            </CardDescription>
          </CardHeader>

          <CardContent className="flex-1 overflow-y-auto p-6 space-y-6 max-h-[60vh]" ref={chatScrollRef}>
            <AnimatePresence initial={false}>
              {chatMessages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  className={`flex items-start gap-4 max-w-[85%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
                >
                  <div className={`shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-primary text-primary-foreground shadow-sm' : 'bg-indigo-500/20 text-indigo-500 shadow-sm'}`}>
                    {msg.role === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                  </div>
                  <div className={`flex flex-col gap-1 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                    <div className={`text-sm px-4 py-3 shadow-md ${msg.role === 'user' ? 'bg-primary text-primary-foreground rounded-2xl rounded-tr-sm' : 'bg-card rounded-2xl rounded-tl-sm border border-border leading-relaxed text-card-foreground'}`}>
                      {msg.content}
                    </div>
                    {msg.timestamp && (
                      <span className="text-[10px] text-muted-foreground/60 px-1">
                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {chatLoading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-start gap-4">
                <div className="shrink-0 h-8 w-8 rounded-full bg-indigo-500/20 text-indigo-500 flex items-center justify-center shadow-sm">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="bg-card px-5 py-4 shadow-md rounded-2xl rounded-tl-sm border border-border flex gap-1.5 items-center">
                  <motion.div className="w-1.5 h-1.5 bg-indigo-500 rounded-full" animate={{ y: [0, -4, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0 }} />
                  <motion.div className="w-1.5 h-1.5 bg-indigo-500 rounded-full" animate={{ y: [0, -4, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }} />
                  <motion.div className="w-1.5 h-1.5 bg-indigo-500 rounded-full" animate={{ y: [0, -4, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }} />
                </div>
              </motion.div>
            )}
          </CardContent>

          <CardFooter className="p-4 border-t border-border/50 bg-background/50">
            <form onSubmit={handleChatSubmit} className="flex w-full gap-3 relative">
              <Input
                className="pr-12 bg-muted/30 border-border focus-visible:ring-indigo-500 h-12 shadow-sm rounded-xl text-md"
                placeholder="Ask about connected inventory or monitored machines..."
                value={chatQuery}
                onChange={(e) => setChatQuery(e.target.value)}
                disabled={chatLoading}
              />
              <Button type="submit" size="icon" className="absolute right-1.5 top-1.5 h-9 w-9 bg-indigo-500 hover:bg-indigo-600 rounded-lg shadow-sm" disabled={!chatQuery.trim() || chatLoading}>
                <Send className="h-4 w-4 text-white ml-0.5" />
              </Button>
            </form>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
