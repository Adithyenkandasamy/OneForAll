"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Package, AlertCircle } from "lucide-react";

const inventoryData = [
  { id: "INV-102", name: "Steel Bearings (50mm)", stock: 1200, threshold: 500, status: "Healthy" },
  { id: "INV-103", name: "Hydraulic Fluid (Liters)", stock: 45, threshold: 100, status: "Low Stock" },
  { id: "INV-104", name: "Copper Wire Spools", stock: 18, threshold: 20, status: "Critical" },
  { id: "INV-105", name: "Conveyor Belts", stock: 4, threshold: 2, status: "Healthy" },
  { id: "INV-106", name: "Robot Arm Servos", stock: 2, threshold: 10, status: "Critical" },
];

export default function InventoryPage() {
  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Inventory Intelligence</h1>
          <p className="text-gray-500 mt-1">Real-time stock levels and automated replenishment.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg">Stock Alerts</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {inventoryData.filter(i => i.status !== "Healthy").map((item) => (
              <div key={item.id} className="flex items-start gap-3 p-3 rounded-lg border border-red-100 bg-red-50/50">
                <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-gray-900 leading-tight mb-1">{item.name}</p>
                  <p className="text-xs text-gray-500">Only {item.stock} left (Threshold: {item.threshold})</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="md:col-span-2 overflow-hidden">
          <div className="p-4 border-b border-gray-200 bg-gray-50/50 flex items-center gap-2">
            <Package className="h-4 w-4 text-gray-500" />
            <span className="font-semibold text-sm">Full Inventory List</span>
          </div>
          <Table>
            <TableHeader>
              <TableRow className="bg-gray-50/50 hover:bg-gray-50/50">
                <TableHead className="font-semibold text-gray-900">SKU</TableHead>
                <TableHead className="font-semibold text-gray-900">Part Name</TableHead>
                <TableHead className="font-semibold text-gray-900">Stock Level</TableHead>
                <TableHead className="font-semibold text-gray-900">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {inventoryData.map((item) => (
                <TableRow key={item.id}>
                  <TableCell className="font-medium text-gray-900">{item.id}</TableCell>
                  <TableCell>{item.name}</TableCell>
                  <TableCell>
                    <span className={`font-semibold ${item.stock <= item.threshold ? 'text-red-600' : 'text-gray-900'}`}>
                      {item.stock}
                    </span>
                    <span className="text-gray-400 text-xs ml-1">/ {item.threshold} req</span>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={
                        item.status === "Healthy"
                          ? "bg-green-50 text-green-700 border-green-200"
                          : item.status === "Low Stock"
                          ? "bg-amber-50 text-amber-700 border-amber-200"
                          : "bg-red-50 text-red-700 border-red-200"
                      }
                    >
                      {item.status}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </div>
    </div>
  );
}
