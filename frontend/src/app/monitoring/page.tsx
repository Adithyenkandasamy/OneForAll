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
  CheckCircle2,
  Database,
  Network
} from "lucide-react";

export default function QualityMonitoringPage() {
  const [machines, setMachines] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Connect natively to the FastAPI EventBus Websocket stream
  useEffect(() => {
    let reconnectTimeout: NodeJS.Timeout;
    let ws: WebSocket;

    const connectWS = () => {
      ws = new WebSocket("ws://127.0.0.1:8000/api/v1/ws/dashboard");

      ws.onopen = () => {
        setLoading(false);
      };

      ws.onmessage = (event) => {
        try {
          // Payload format: {"machine_id": "...", "status": {}, "telemetry": {}}
          const payload = JSON.parse(event.data);

          setMachines(prev => {
            const arr = [...prev];
            const idx = arr.findIndex(m => m.machine_id === payload.machine_id);
            const flatMachine = {
              machine_id: payload.machine_id,
              ...payload.status,
              ...payload.telemetry
            };

            if (idx === -1) {
              arr.push(flatMachine);
            } else {
              arr[idx] = flatMachine;
            }
            // Maintain stable sort order
            return arr.sort((a, b) => a.machine_id.localeCompare(b.machine_id));
          });
        } catch (e) {
          console.error("Payload parse error:", e);
        }
      };

      ws.onclose = () => {
        // Auto-reconnect on dropped physics frames
        reconnectTimeout = setTimeout(connectWS, 3000);
      };
    };

    connectWS();

    return () => {
      clearTimeout(reconnectTimeout);
      if (ws) ws.close();
    };
  }, []);

  return (
    <div className="relative min-h-[calc(100vh-4rem)] p-4 md:p-8 overflow-x-hidden select-none bg-slate-50/50">
      {/* Absolute Ambient Backgrounds tailored for light theme */}
      <div className="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-br from-indigo-50 via-white to-slate-50 -z-20 rounded-b-[4rem] shadow-sm border-b border-indigo-100/50" />
      <div className="absolute top-0 left-10 w-96 h-96 bg-primary/10 blur-[100px] rounded-full -z-10 pointer-events-none" />
      <div className="absolute top-40 right-20 w-80 h-80 bg-emerald-400/10 blur-[100px] rounded-full -z-10 pointer-events-none" />

      <div className="max-w-7xl mx-auto flex flex-col gap-8 animate-in fade-in duration-700 relative z-10">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-6 relative z-10">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 mb-2">
              Process Intelligence
            </h1>
            <p className="text-slate-500 font-medium">
              Live native Mosquitto MQTT event loop + Deterministic Rules Engine
            </p>
          </div>
          <div className="flex items-center gap-3 bg-emerald-500/10 border border-emerald-500/30 backdrop-blur-md px-4 py-2 rounded-full shadow-[0_0_15px_rgba(16,185,129,0.15)]">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
            <span className="text-xs font-bold uppercase tracking-widest text-emerald-300">Live IoT WebSockets Active</span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
          <MetricCard
            title="Active CNC Nodes"
            value={machines.length}
            icon={Cpu}
            trend="Synchronized"
          />
          <MetricCard
            title="Avg Fleet Health"
            value={machines.length ? `${Math.round(machines.reduce((acc, m) => acc + (m.health_score || 0), 0) / machines.length)}%` : "0%"}
            icon={Activity}
            trend="Aggregate Metric"
          />
          <MetricCard
            title="Yield Quality"
            value={machines.length ? `${Math.round(machines.reduce((acc, m) => acc + (m.quality_score || 0), 0) / machines.length)}%` : "0%"}
            icon={CheckCircle2}
            trend="Aggregate Metric"
          />
          <MetricCard
            title="Priority Breaches"
            value={machines.filter((m) => (m.risk_level || "").toLowerCase() === "high" || (m.risk_level || "").toLowerCase() === "critical").length}
            icon={AlertTriangle}
            trend="Requires Action"
            status={machines.filter((m) => (m.risk_level || "").toLowerCase() === "high" || (m.risk_level || "").toLowerCase() === "critical").length > 0 ? "warning" : "normal"}
          />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
          <Card className="xl:col-span-3 min-w-0 border-indigo-100/50 bg-white/70 backdrop-blur-xl shadow-xl shadow-indigo-900/5 overflow-hidden rounded-[2rem]">
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-indigo-950 font-bold uppercase tracking-wider bg-white/60 border-b border-indigo-100/50 backdrop-blur-md">
                  <tr>
                    <th className="px-6 py-5">Machine ID</th>
                    <th className="px-6 py-5 text-center">Telemetry Stream</th>
                    <th className="px-6 py-5 text-center">Health %</th>
                    <th className="px-6 py-5 text-center">Quality %</th>
                    <th className="px-6 py-5 text-center">Risk Vector</th>
                    <th className="px-6 py-5 text-right">Inspection Module</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-indigo-50/50">
                  {machines.map((machine, index) => (
                    <MachineRow key={machine.machine_id || index} data={machine} />
                  ))}
                </tbody>
              </table>

              {loading && machines.length === 0 && (
                <div className="w-full py-16 flex flex-col items-center justify-center text-slate-400 gap-4">
                  <Activity className="h-8 w-8 animate-pulse text-indigo-400" />
                  <span className="font-medium tracking-wide">Initializing EventBus pipeline...</span>
                </div>
              )}
              {!loading && machines.length === 0 && (
                <div className="w-full py-16 flex flex-col items-center justify-center text-slate-400 gap-4">
                  <Network className="h-8 w-8 text-slate-300" />
                  <span className="font-medium tracking-wide">Awaiting Mosquitto payloads on port 1883</span>
                </div>
              )}
            </div>
          </Card>

          <Card className="min-w-0 border-indigo-100/50 bg-white/70 backdrop-blur-xl shadow-xl shadow-indigo-900/5 rounded-[2rem] p-6 h-fit">
            <h3 className="text-lg font-bold text-zinc-900 mb-4 flex items-center gap-2">
              <Database className="h-5 w-5 text-indigo-600" />
              How this works
            </h3>
            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-indigo-200 before:to-transparent">
              <div className="relative flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 shrink-0 shadow-sm z-10 font-bold font-mono text-sm">
                  1Hz
                </div>
                <div>
                  <h4 className="font-bold text-zinc-900 text-sm">IoT Simulators</h4>
                  <p className="text-xs text-zinc-500 font-medium leading-relaxed mt-0.5">10 virtual CNC agents publish shifting physics variables iteratively to a local `amqtt` broker on port 1883.</p>
                </div>
              </div>
              <div className="relative flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600 shrink-0 shadow-sm z-10 font-bold font-mono text-sm">
                  Fast
                </div>
                <div>
                  <h4 className="font-bold text-zinc-900 text-sm">Consumer Queue</h4>
                  <p className="text-xs text-zinc-500 font-medium leading-relaxed mt-0.5">The FastAPI native loop intercepts the JSON packets without using network proxy polling.</p>
                </div>
              </div>
              <div className="relative flex items-center gap-4">
                <div className="h-10 w-10 rounded-full bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600 shrink-0 shadow-sm z-10 font-bold font-mono text-sm">
                  DB
                </div>
                <div>
                  <h4 className="font-bold text-zinc-900 text-sm">Deterministic Engine</h4>
                  <p className="text-xs text-zinc-500 font-medium leading-relaxed mt-0.5">Engine validates metrics, inserts instantly to Postgres mapping, and broadcasts the arrays down the WebSocket.</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon: Icon, trend, status = "normal" }: any) {
  return (
    <Card className="min-w-0 bg-white/70 backdrop-blur-xl border-indigo-100/50 shadow-xl shadow-indigo-900/5 transform transition-all duration-300 hover:-translate-y-1 hover:shadow-indigo-900/10 rounded-3xl">
      <CardContent className="p-6">
        <div className="flex justify-between items-start">
          <div className="space-y-2">
            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{title}</p>
            <p className={`text-4xl font-extrabold tracking-tighter drop-shadow-sm ${status === 'warning' ? 'text-rose-600' : 'text-slate-900'}`}>{value}</p>
          </div>
          <div className={`p-3 rounded-2xl shadow-inner ${status === 'warning' ? 'bg-rose-50 text-rose-600 border border-rose-100' : 'bg-indigo-50/80 text-indigo-600 border border-indigo-100'}`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
        <p className={`text-xs mt-4 font-semibold uppercase tracking-wider ${status === 'warning' ? 'text-rose-500' : 'text-indigo-500'}`}>{trend}</p>
      </CardContent>
    </Card>
  );
}

function MachineRow({ data }: any) {
  const isHighRisk = (data.risk_level || "").toUpperCase() === "HIGH" || (data.risk_level || "").toUpperCase() === "CRITICAL";
  const isMediumRisk = (data.risk_level || "").toUpperCase() === "MEDIUM";

  return (
    <tr className="hover:bg-indigo-50/40 transition-all duration-300 bg-white/50 group">
      <td className="px-6 py-5 whitespace-nowrap">
        <div className="flex items-center gap-3">
          <div className={`h-2.5 w-2.5 rounded-full ${isHighRisk ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.8)]' : isMediumRisk ? 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.8)]' : 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]'} animate-pulse`} />
          <span className="font-extrabold text-zinc-800 tracking-tight text-base">{data.machine_id}</span>
        </div>
      </td>
      <td className="px-6 py-5 whitespace-nowrap text-center">
        <div className="flex justify-center gap-4 text-xs font-mono text-indigo-900/80 font-bold bg-indigo-50/50 py-1.5 px-3 rounded-xl border border-indigo-100/50 backdrop-blur-sm max-w-fit mx-auto">
          <span className="flex items-center gap-1.5"><Thermometer className="h-3.5 w-3.5 text-indigo-500" /> {data.temperature?.toFixed(1)}°C</span>
          <span className="flex items-center gap-1.5"><Activity className="h-3.5 w-3.5 text-indigo-500" /> {(data.vibration || 0).toFixed(2)}v</span>
        </div>
      </td>
      <td className="px-6 py-5 whitespace-nowrap font-mono font-extrabold text-center text-lg tracking-tight">
        <span className={data.health_score < 75 ? "text-amber-600 drop-shadow-sm" : "text-emerald-700 drop-shadow-sm"}>{data.health_score?.toFixed(1)}%</span>
      </td>
      <td className="px-6 py-5 whitespace-nowrap font-mono font-extrabold text-center text-lg tracking-tight">
        <span className={data.quality_score < 90 ? "text-amber-600 drop-shadow-sm" : "text-emerald-700 drop-shadow-sm"}>{data.quality_score?.toFixed(1)}%</span>
      </td>
      <td className="px-6 py-5 whitespace-nowrap text-center">
        <Badge variant="outline" className={`px-4 py-1.5 text-xs font-black tracking-widest ${isMediumRisk ? "bg-amber-100/80 text-amber-700 hover:bg-amber-200 border-transparent shadow-inner" : isHighRisk ? "bg-gradient-to-r from-rose-500 to-red-600 text-white shadow-lg border-transparent" : "bg-emerald-100/80 text-emerald-800 border-transparent hover:bg-emerald-200 shadow-inner"}`}>
          {data.risk_level?.toUpperCase()}
        </Badge>
      </td>
      <td className="px-6 py-5 whitespace-nowrap text-right">
        <span className={`text-[11px] font-bold uppercase tracking-wider px-3 py-1.5 rounded-lg ${isHighRisk ? "text-rose-600 bg-rose-50 border border-rose-100" : isMediumRisk ? "text-amber-700 bg-amber-50 border border-amber-100" : "text-zinc-400 font-semibold"}`}>{data.inspection_result}</span>
      </td>
    </tr>
  );
}
