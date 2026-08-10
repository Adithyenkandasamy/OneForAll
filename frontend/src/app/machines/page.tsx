"use client";

import { useState } from "react";
import { useRealtimeData, generateMachinesData } from "@/lib/mockData";
import { motion } from "framer-motion";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Search, Filter, MoreHorizontal, Activity, Settings2, ShieldAlert } from "lucide-react";

export default function MachinesPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const machinesData = useRealtimeData(generateMachinesData, 4000);

  const filteredMachines = machinesData.filter((m) =>
    m.name.toLowerCase().includes(searchTerm.toLowerCase()) || m.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Machine Fleet</h1>
          <p className="text-gray-500 mt-1">Manage and monitor all factory equipment.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2">
            <Filter className="h-4 w-4" />
            Filter
          </Button>
          <Button className="gap-2 bg-black text-white hover:bg-gray-800">
            <Settings2 className="h-4 w-4" />
            Manage Fleet
          </Button>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
      >
        <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50/50">
          <div className="relative w-72">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <Input placeholder="Search machines by ID or name..." className="pl-9 bg-white" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
          </div>
          <p className="text-sm text-gray-500 font-medium">Showing {filteredMachines.length} machines</p>
        </div>

        <Table>
          <TableHeader>
            <TableRow className="bg-gray-50/50 hover:bg-gray-50/50">
              <TableHead className="font-semibold text-gray-900">Machine ID</TableHead>
              <TableHead className="font-semibold text-gray-900">Name / Type</TableHead>
              <TableHead className="font-semibold text-gray-900">Status</TableHead>
              <TableHead className="font-semibold text-gray-900">Health Score</TableHead>
              <TableHead className="font-semibold text-gray-900">Temp (°C)</TableHead>
              <TableHead className="font-semibold text-gray-900">Vibration</TableHead>
              <TableHead className="font-semibold text-gray-900">OEE</TableHead>
              <TableHead className="font-semibold text-gray-900">Uptime</TableHead>
              <TableHead className="text-right font-semibold text-gray-900">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredMachines.map((machine) => (
              <TableRow key={machine.id}>
                <TableCell className="font-medium text-gray-900">{machine.id}</TableCell>
                <TableCell>{machine.name}</TableCell>
                <TableCell>
                  <Badge variant="outline" className={machine.status === "Running" ? "bg-green-50 text-green-700 border-green-200" : machine.status === "Warning" ? "bg-amber-50 text-amber-700 border-amber-200" : "bg-red-50 text-red-700 border-red-200"}>
                    {machine.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${machine.health >= 90 ? "bg-green-500" : machine.health >= 70 ? "bg-amber-500" : "bg-red-500"}`} style={{ width: `${machine.health}%` }} />
                    </div>
                    <span className="text-sm text-gray-600 font-medium">{machine.health}%</span>
                  </div>
                </TableCell>
                <TableCell className="text-gray-600">{machine.temperature}°C</TableCell>
                <TableCell className="text-gray-600">{machine.vibration} mm/s</TableCell>
                <TableCell className="text-gray-600">{machine.oee}%</TableCell>
                <TableCell className="text-gray-600">{machine.uptime}</TableCell>
                <TableCell className="text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger className="h-8 w-8 p-0 inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-gray-100 focus-visible:outline-none">
                      <span className="sr-only">Open menu</span>
                      <MoreHorizontal className="h-4 w-4" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-48">
                      <DropdownMenuLabel>Actions</DropdownMenuLabel>
                      <DropdownMenuItem className="cursor-pointer">
                        <Activity className="mr-2 h-4 w-4" /> View Telemetry
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem className="text-red-600 focus:bg-red-50 focus:text-red-700 cursor-pointer">
                        <ShieldAlert className="mr-2 h-4 w-4" /> Schedule Maintenance
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </motion.div>
    </div>
  );
}
