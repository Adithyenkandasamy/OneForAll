"use client";

import React, { useState, useEffect } from "react";
import api from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { FloatingInventoryChat } from "@/components/inventory/FloatingInventoryChat";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Package, AlertCircle, Loader2, Sparkles, ServerCrash, Edit2 } from "lucide-react";

interface InventoryItem {
  sku: string;
  name: string;
  current_stock: number;
  minimum_stock: number;
  risk_level: string;
  supplier: string;
}

export default function EditableInventoryPage() {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Track inline editing
  const [editingCell, setEditingCell] = useState<{ sku: string, column: string } | null>(null);
  const [editValue, setEditValue] = useState("");
  const [updating, setUpdating] = useState(false);

  // Fetch Inventory Data
  const loadInventory = async (isSilent = false) => {
    try {
      if (!isSilent) setLoading(true);
      setError(null);
      // Valid minimum length query string that matches actual Material IDs to prevent 422
      const res = await api.get("/api/v1/agents/inventory/materials");
      setInventory(res.data || []);
    } catch (err: any) {
      console.error("Failed to load inventory:", err);
      if (!isSilent) setError("Failed to stream Google Sheets MCP data.");
    } finally {
      if (!isSilent) setLoading(false);
    }
  };

  useEffect(() => {
    loadInventory();

    // Ultra real-time sync polling every 2 seconds
    const intervalId = setInterval(() => {
      loadInventory(true);
    }, 1000);

    return () => clearInterval(intervalId);
  }, []);

  const startEdit = (item: InventoryItem, column: string, currentValue: any) => {
    setEditingCell({ sku: item.sku, column });
    setEditValue(String(currentValue));
  };

  const handleUpdate = async (sku: string) => {
    if (!editingCell) return;
    setUpdating(true);

    try {
      // Send update payload to backend MCP tunnel
      await api.post("/api/v1/agents/inventory/update", {
        sku: sku,
        column: editingCell.column,
        value: editValue
      });

      // Optimistic update in UI
      setInventory(prev => prev.map(item => {
        if (item.sku === sku) {
          if (editingCell.column === 'current_stock') {
            return { ...item, current_stock: Number(editValue) };
          }
          if (editingCell.column === 'ai_risk_level') {
            return { ...item, risk_level: editValue };
          }
        }
        return item;
      }));
      setEditingCell(null);
    } catch (err: any) {
      console.error("Update failed:", err);
      if (err.response?.status === 403) {
        alert("Permission Denied: Only Admin users can modify the Google Sheet.");
      } else {
        alert("Failed to update inventory. Is the Google Sheets MCP connected?");
      }
    } finally {
      setUpdating(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent, sku: string) => {
    if (e.key === "Enter") {
      handleUpdate(sku);
    } else if (e.key === "Escape") {
      setEditingCell(null);
    }
  };

  const getStatusColor = (status: string) => {
    const s = (status || "").toLowerCase();
    if (s.includes("low") || s.includes("healthy") || s.includes("in stock")) return "bg-green-500/10 text-green-700 border-green-500/20";
    if (s.includes("medium")) return "bg-amber-500/10 text-amber-700 border-amber-500/20";
    if (s.includes("high") || s.includes("critical") || s.includes("out")) return "bg-red-500/10 text-red-700 border-red-500/20";
    return "bg-gray-500/10 text-gray-700 border-gray-500/20";
  };

  const criticalItems = inventory.filter(i => {
    const s = (i.risk_level || "").toLowerCase();
    return s.includes("critical") || s.includes("high") || i.current_stock <= i.minimum_stock;
  });

  return (
    <div className="space-y-6 pb-12 w-full animate-in fade-in duration-500">

      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Inventory Data Management</h1>
          <p className="text-muted-foreground mt-1">Direct read/write access to Google Sheets via MCP.</p>
        </div>

      </div>

      {error && (
        <div className="p-4 rounded-lg border border-destructive/20 bg-destructive/10 flex items-start gap-3 w-full">
          <ServerCrash className="h-5 w-5 text-destructive shrink-0" />
          <div>
            <p className="text-sm font-semibold text-destructive">Connection Error</p>
            <p className="text-xs text-destructive/80 mt-1">{error}</p>
          </div>
        </div>
      )}

      {criticalItems.length > 0 && (
        <Card className="border-red-900/20 bg-red-500/5 shadow-sm">
          <CardHeader className="py-4">
            <CardTitle className="text-lg flex items-center gap-2 text-red-500">
              <AlertCircle className="h-5 w-5" />
              Critical Stock Alerts
            </CardTitle>
          </CardHeader>
          <CardContent className="flex overflow-x-auto gap-4 pb-4 snap-x hide-scrollbar">
            {criticalItems.map((item) => (
              <div key={item.sku} className="min-w-[220px] flex-shrink-0 flex justify-between items-center p-3 rounded-lg border border-red-500/20 bg-background/50 snap-start">
                <div>
                  <p className="text-sm font-medium leading-tight">{item.name}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">SKU: {item.sku}</p>
                </div>
                <div className="text-right">
                  <span className="text-lg font-bold text-red-500">{item.current_stock}</span>
                  <p className="text-[10px] uppercase tracking-wider text-red-500/70 font-semibold">{item.risk_level}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card className="shadow-md w-full">
        <div className="p-4 border-b border-border bg-muted/30 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Package className="h-4 w-4 text-muted-foreground" />
            <span className="font-semibold text-sm">Real-time Data Grid</span>
          </div>
          <p className="text-xs text-muted-foreground flex items-center gap-1">
            <Edit2 className="w-3 h-3" /> Double-click row cells to edit
          </p>
        </div>

        <div className="overflow-x-auto min-h-[400px]">
          {loading && inventory.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-16 text-muted-foreground">
              <Loader2 className="h-8 w-8 animate-spin mb-4" />
              <p className="text-sm">Fetching structural mapping from MCP server...</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/10 hover:bg-muted/10">
                  <TableHead className="font-semibold w-[120px]">SKU</TableHead>
                  <TableHead className="font-semibold w-[250px]">Part Name</TableHead>
                  <TableHead className="font-semibold">Supplier</TableHead>
                  <TableHead className="font-semibold w-[150px]">Quantity</TableHead>
                  <TableHead className="font-semibold w-[150px]">Threshold</TableHead>
                  <TableHead className="font-semibold w-[150px]">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {inventory.map((item) => (
                  <TableRow key={item.sku} className="transition-colors hover:bg-muted/20 group">
                    <TableCell className="font-medium font-mono text-xs text-muted-foreground align-middle">
                      {item.sku}
                    </TableCell>
                    <TableCell className="font-medium whitespace-nowrap align-middle">
                      {item.name}
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm align-middle">
                      {item.supplier || "Unknown"}
                    </TableCell>

                    {/* Editable Quantity */}
                    <TableCell
                      className="align-middle cursor-pointer hover:bg-muted/40 transition-colors"
                      onDoubleClick={() => startEdit(item, "current_stock", item.current_stock)}
                    >
                      {editingCell?.sku === item.sku && editingCell.column === "current_stock" ? (
                        <div className="flex items-center gap-2">
                          <Input
                            autoFocus
                            type="number"
                            size={5}
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            onKeyDown={(e) => handleKeyDown(e, item.sku)}
                            disabled={updating}
                            className="h-8 py-1 px-2 w-20"
                            onBlur={() => handleUpdate(item.sku)}
                          />
                          {updating && <Loader2 className="w-3 h-3 animate-spin text-muted-foreground" />}
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <span className={`font-semibold ${item.current_stock <= item.minimum_stock ? 'text-red-500' : ''}`}>
                            {item.current_stock}
                          </span>
                          <Edit2 className="w-3 h-3 text-transparent group-hover:text-muted-foreground/30 transition-colors" />
                        </div>
                      )}
                    </TableCell>

                    <TableCell className="text-muted-foreground align-middle">
                      {item.minimum_stock}
                    </TableCell>

                    {/* Editable Status */}
                    <TableCell
                      className="align-middle cursor-pointer hover:bg-muted/40 transition-colors"
                      onDoubleClick={() => startEdit(item, "ai_risk_level", item.risk_level)}
                    >
                      {editingCell?.sku === item.sku && editingCell.column === "ai_risk_level" ? (
                        <div className="flex items-center gap-2">
                          <Input
                            autoFocus
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            onKeyDown={(e) => handleKeyDown(e, item.sku)}
                            disabled={updating}
                            className="h-8 py-1 px-2 text-xs"
                            onBlur={() => handleUpdate(item.sku)}
                          />
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <Button
                            onClick={() => loadInventory(false)}
                            variant="outline" className={getStatusColor(item.risk_level)}>
                            {item.risk_level}
                          </Button>
                          <Edit2 className="w-3 h-3 text-transparent group-hover:text-muted-foreground/30 transition-colors" />
                        </div>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                {inventory.length === 0 && !error && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center p-8 text-muted-foreground">
                      No inventory items found matching global MCP constraints.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </div>
      </Card>
      <FloatingInventoryChat />
    </div>
  );
}
