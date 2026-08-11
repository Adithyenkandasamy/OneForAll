import React, { useState, useRef, useEffect } from "react";
import { MessageSquare, X, Send, Bot, User, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import api from "@/lib/api";

interface Message {
  role: "user" | "bot";
  content: string;
  timestamp?: Date;
}

export function FloatingInventoryChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", content: "Hi! I am the localized Inventory AI. I only have access to explain warehouse metrics and stock alerts. How can I help you today?", timestamp: new Date() }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage, timestamp: new Date() }]);
    setLoading(true);

    try {
      const res = await api.post("/api/v1/agents/inventory/chat", {
        query: userMessage,
        conversation_id: "inventory-local-123"
      });
      
      setMessages((prev) => [
        ...prev, 
        { role: "bot", content: res.data.content || "I couldn't generate a response.", timestamp: new Date() }
      ]);
    } catch (error: any) {
      console.error("Chat error:", error);
      const is503 = error?.response?.status === 503;
      setMessages((prev) => [
        ...prev, 
        { 
          role: "bot", 
          content: is503
            ? "The Inventory MCP Service is currently initializing or unavailable (503). Please verify backend Google Sheets connectivity."
            : "Sorry, I lost connection to the inventory backend.", 
          timestamp: new Date() 
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 h-14 w-14 rounded-full bg-black text-white shadow-xl flex items-center justify-center hover:scale-105 transition-transform z-50"
        >
          <MessageSquare className="h-6 w-6" />
        </button>
      )}

      {isOpen && (
        <div className="fixed bottom-6 right-6 w-[400px] h-[550px] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col z-50 overflow-hidden animate-in slide-in-from-bottom-5">
          {/* Header */}
          <div className="h-14 bg-black text-white flex items-center justify-between px-4 shrink-0">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              <span className="font-semibold text-sm">Inventory AI Copilot</span>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-gray-300 hover:text-white transition-colors">
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex gap-2 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                <div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === "user" ? "bg-gray-200" : "bg-purple-100 text-purple-600"}`}>
                  {msg.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>
                <div className={`flex flex-col gap-1 max-w-[75%] ${msg.role === "user" ? "items-end" : "items-start"}`}>
                  <div className={`px-4 py-2 rounded-2xl text-sm ${msg.role === "user" ? "bg-black text-white rounded-tr-sm" : "bg-white border shadow-sm rounded-tl-sm text-gray-800"}`}>
                    {msg.content}
                  </div>
                  {msg.timestamp && (
                    <span className="text-[10px] text-gray-400 px-1">
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-2 flex-row">
                <div className="h-8 w-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center shrink-0">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="px-4 py-2 rounded-2xl bg-white border shadow-sm rounded-tl-sm text-gray-800 flex items-center h-[38px]">
                  <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="p-4 bg-white border-t">
            <form 
              onSubmit={(e) => { e.preventDefault(); handleSend(); }}
              className="flex gap-2 relative"
            >
              <Input 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about materials..." 
                className="pr-10 h-10 rounded-full"
                disabled={loading}
              />
              <button 
                type="submit"
                disabled={!input.trim() || loading}
                className="absolute right-1 top-1 h-8 w-8 rounded-full bg-black flex items-center justify-center text-white disabled:opacity-50 disabled:bg-gray-300"
              >
                <Send className="h-4 w-4 ml-0.5" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
