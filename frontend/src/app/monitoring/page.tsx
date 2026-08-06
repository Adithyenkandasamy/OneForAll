"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";
import { 
  Activity, 
  Thermometer, 
  Settings2, 
  AlertTriangle,
  Cpu,
  CheckCircle2
} from "lucide-react";

export default function QualityMonitoringPage() {
  const [machines, setMachines] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchQuality = async (isSilent = false) => {
    if (!isSilent) setLoading(true);
    try {
      const res = await api.get("/api/v1/agents/quality/dashboard");
      if (res.data && res.data.machines) {
        // Sort explicitly by Machine ID strings like "Machine-01" to keep it stable
        const sorted = res.data.machines.sort((a: any, b: any) => 
            a.machine_id.localeCompare(b.machine_id)
        );
        setMachines(sorted);
      }
    } catch (err) {
      console.error("Failed to fetch quality dashboard", err);
    } finally {
      if (!isSilent) setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuality();
    const interval = setInterval(() => fetchQuality(true), 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Quality Monitoring</h1>
          <p className="text-gray-500 mt-1">Live machine telemetry and deterministic quality engine metrics.</p>
        </div>
        <div className="flex items-center gap-2 text-sm font-medium text-green-600 bg-green-50 px-3 py-1 rounded-full border border-green-200">
          <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
          Live Mockaroo Stream Active
        </div>
      </div>

      {/* Aggregate Engine Summaries */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard 
          title="Active Machines" 
          value={machines.length} 
          icon={Cpu} 
          trend="Tracking" 
        />
        <MetricCard 
          title="Avg Health Score" 
          value={machines.length ? `${Math.round(machines.reduce((acc, m) => acc + (m.health_score || 0), 0) / machines.length)}%` : "0%"} 
          icon={Activity} 
          trend="Nominal" 
        />
        <MetricCard 
          title="Avg Quality Score" 
          value={machines.length ? `${Math.round(machines.reduce((acc, m) => acc + (m.quality_score || 0), 0) / machines.length)}%` : "0%"} 
          icon={CheckCircle2} 
          trend="Nominal" 
        />
        <MetricCard 
          title="Critical Alerts" 
          value={machines.filter((m) => (m.risk_level || "").toLowerCase() === "high").length} 
          icon={AlertTriangle} 
          trend="Requires Action"
          status={machines.filter((m) => (m.risk_level || "").toLowerCase() === "high").length > 0 ? "warning" : "normal"}
        />
      </div>

      <Card className="mt-6 border border-zinc-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-zinc-500 bg-zinc-50 border-b">
              <tr>
                <th className="px-6 py-4 font-semibold uppercase tracking-wider">Machine ID</th>
                <th className="px-6 py-4 font-semibold uppercase tracking-wider">Telemetry</th>
                <th className="px-6 py-4 font-semibold uppercase tracking-wider">Health %</th>
                <th className="px-6 py-4 font-semibold uppercase tracking-wider">Quality %</th>
                <th className="px-6 py-4 font-semibold uppercase tracking-wider">Risk Level</th>
                <th className="px-6 py-4 font-semibold uppercase tracking-wider text-right">Inspection Output</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100">
              {machines.map((machine, index) => (
                <MachineRow key={machine.machine_id || index} data={machine} />
              ))}
            </tbody>
          </table>
          
          {loading && machines.length === 0 && (
             <div className="w-full py-12 flex justify-center text-zinc-500 animate-pulse">Loading telemetry engines...</div>
          )}
          {!loading && machines.length === 0 && (
             <div className="w-full py-12 flex justify-center text-zinc-500">No mockaroo data received yet.</div>
          )}
        </div>
      </Card>
      
    </div>
  );
}

function MetricCard({ title, value, icon: Icon, trend, status = "normal" }: any) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex justify-between items-start">
          <div className="space-y-1">
            <p className="text-sm font-medium text-zinc-500">{title}</p>
            <p className={`text-2xl font-bold tracking-tight ${status === 'warning' ? 'text-red-500' : 'text-zinc-900'}`}>{value}</p>
          </div>
          <div className={`p-2 rounded-lg ${status === 'warning' ? 'bg-red-50 text-red-500' : 'bg-zinc-100 text-zinc-600'}`}>
            <Icon className="h-5 w-5" />
          </div>
        </div>
        <p className={`text-xs mt-4 ${status === 'warning' ? 'text-red-600/70' : 'text-zinc-500'}`}>{trend}</p>
      </CardContent>
    </Card>
  );
}

function MachineRow({ data }: any) {
  const isHighRisk = (data.risk_level || "").toUpperCase() === "HIGH";
  const isMediumRisk = (data.risk_level || "").toUpperCase() === "MEDIUM";

  return (
    <tr className="hover:bg-zinc-50/50 transition-colors bg-white group">
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex items-center gap-2">
          <div className={`h-2 w-2 rounded-full ${isHighRisk ? 'bg-red-500' : isMediumRisk ? 'bg-amber-400' : 'bg-green-500'} animate-pulse`} />
          <span className="font-semibold text-zinc-900">{data.machine_id}</span>
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex gap-4 text-xs font-mono text-zinc-600">
           <span className="flex items-center gap-1"><Thermometer className="h-3 w-3"/> {data.temperature?.toFixed(1)}°C</span>
           <span className="flex items-center gap-1"><Activity className="h-3 w-3"/> {(data.vibration || 0).toFixed(2)}v</span>
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap font-mono font-medium">
        <span className={data.health_score < 75 ? "text-amber-600" : "text-zinc-900"}>{data.health_score?.toFixed(1)}%</span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap font-mono font-medium">
        <span className={data.quality_score < 90 ? "text-amber-600" : "text-zinc-900"}>{data.quality_score?.toFixed(1)}%</span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <Badge variant={isHighRisk ? "destructive" : isMediumRisk ? "secondary" : "outline"} className={isMediumRisk ? "bg-amber-100 text-amber-700 hover:bg-amber-100 border-amber-200" : isHighRisk ? "" : "bg-green-50 text-green-700 border-green-200"}>
          {data.risk_level?.toUpperCase()}
        </Badge>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-right text-xs font-semibold">
        <span className={isHighRisk ? "text-red-600" : "text-zinc-500"}>{data.inspection_result}</span>
      </td>
    </tr>
  );
}
