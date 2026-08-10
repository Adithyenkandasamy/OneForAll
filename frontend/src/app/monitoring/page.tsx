"use client";

import { useMonitoring } from "@/contexts/MonitoringContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Activity,
  Thermometer,
  AlertTriangle,
  Cpu,
  CheckCircle2,
  Database,
  Network,
} from "lucide-react";

export default function QualityMonitoringPage() {
  const { machines, connected, source } = useMonitoring();

  const validMachines = machines.filter((m) => m.health_score > 0);
  const avgHealth = validMachines.length
    ? Math.round(validMachines.reduce((acc, m) => acc + (m.health_score || 0), 0) / validMachines.length)
    : 0;
  const avgQuality = validMachines.length
    ? Math.round(validMachines.reduce((acc, m) => acc + (m.quality_score || 0), 0) / validMachines.length)
    : 0;
  const breaches = validMachines.filter(
    (m) => (m.risk_level || "").toLowerCase() === "high" || (m.risk_level || "").toLowerCase() === "critical"
  ).length;

  return (
    <div className="space-y-6 pb-12 w-full animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Quality Intelligence</h1>
          <p className="text-muted-foreground mt-1">
            {source === "live"
              ? "Live machine telemetry refreshed every five seconds"
              : "Simulated telemetry — connect a production data source to enable live monitoring"}
          </p>
        </div>
        <div
          className={`flex items-center gap-2 px-3 py-1 rounded-md border text-xs font-semibold uppercase tracking-wide ${connected
              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
              : "bg-rose-50 text-rose-700 border-rose-200"
            }`}
        >
          <span
            className={`h-2 w-2 rounded-full ${connected ? "bg-emerald-500 animate-pulse" : "bg-rose-500"
              }`}
          />
          {connected ? "Live telemetry active" : "Demo telemetry active"}
        </div>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricCard title="Active CNC Nodes" value={validMachines.length.toString()} icon={Cpu} trend="Synchronized" />
        <MetricCard title="Avg Machine Health" value={`${avgHealth}%`} icon={Activity} trend="Aggregate Metric" />
        <MetricCard title="Yield Quality" value={`${avgQuality}%`} icon={CheckCircle2} trend="Aggregate Metric" />
        <MetricCard
          title="Priority Breaches"
          value={breaches.toString()}
          icon={AlertTriangle}
          trend="Requires Action"
          status={breaches > 0 ? "warning" : "normal"}
        />
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        <Card className="xl:col-span-3 shadow-md">
          <div className="p-4 border-b border-border bg-muted/30 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Network className="h-4 w-4 text-muted-foreground" />
              <span className="font-semibold text-sm">Real-time Telemetry Grid</span>
            </div>
            <span className="text-xs text-muted-foreground">
              {connected ? "Last refresh: under 5 seconds" : "Simulated feed"}
            </span>
          </div>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/10 hover:bg-muted/10">
                  <TableHead className="font-semibold px-4 py-3">Machine ID</TableHead>
                  <TableHead className="font-semibold px-4 py-3 text-center">Telemetry Stream</TableHead>
                  <TableHead className="font-semibold px-4 py-3 text-center">Health %</TableHead>
                  <TableHead className="font-semibold px-4 py-3 text-center">Quality %</TableHead>
                  <TableHead className="font-semibold px-4 py-3 text-center">Risk Vector</TableHead>
                  <TableHead className="font-semibold px-4 py-3 text-right">Inspection Module</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {machines.map((machine, index) => (
                  <MachineRow key={machine.machine_id || index} data={machine} />
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>

        <Card className="shadow-md h-fit">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Database className="h-5 w-5" />
              How this works
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              source === "live"
                ? { label: "LIVE", title: "Production telemetry", desc: "The dashboard reads the latest machine states from the deployed quality service every five seconds." }
                : { label: "DEMO", title: "Simulated telemetry", desc: "Illustrative machine readings are shown because no production machine records are available yet." },
              { label: "RULES", title: "Deterministic Engine", desc: "Health, quality, and risk are calculated from the collected machine readings." },
              { label: "ACTION", title: "Operational alerts", desc: "High-risk machines can be routed to the maintenance team with a recommended inspection action." },
            ].map((step) => (
              <div key={step.label} className="flex items-start gap-3">
                <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center text-muted-foreground shrink-0 text-xs font-bold font-mono">
                  {step.label}
                </div>
                <div>
                  <h4 className="font-semibold text-sm">{step.title}</h4>
                  <p className="text-xs text-muted-foreground leading-relaxed mt-1">{step.desc}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon: Icon, trend, status = "normal" }: any) {
  return (
    <Card className="shadow-sm hover:shadow-md transition-shadow">
      <CardContent className="p-5">
        <div className="flex justify-between items-start">
          <div className="space-y-1.5">
            <p className="text-xs font-semibold text-muted-foreground uppercase">{title}</p>
            <p className={`text-3xl font-bold tracking-tight ${status === "warning" ? "text-destructive" : ""}`}>
              {value}
            </p>
          </div>
          <div className={`p-2.5 rounded-lg ${status === "warning" ? "bg-destructive/10 text-destructive" : "bg-muted text-muted-foreground"}`}>
            <Icon className="h-5 w-5" />
          </div>
        </div>
        <p className={`text-xs mt-4 ${status === "warning" ? "text-destructive" : "text-muted-foreground"}`}>{trend}</p>
      </CardContent>
    </Card>
  );
}

function MachineRow({ data }: any) {
  const statusStr = (data.risk_level || "").toUpperCase();
  const isHighRisk = statusStr === "HIGH" || statusStr === "CRITICAL";
  const isMediumRisk = statusStr === "MEDIUM";
  const isUnknown = statusStr === "UNKNOWN";

  return (
    <TableRow className="transition-colors hover:bg-muted/20">
      <TableCell className="px-4 py-3 align-middle">
        <div className="flex items-center gap-2">
          <div
            className={`h-2 w-2 rounded-full ${isUnknown
                ? "bg-muted"
                : isHighRisk
                  ? "bg-destructive animate-pulse"
                  : isMediumRisk
                    ? "bg-amber-500 animate-pulse"
                    : "bg-green-500 animate-pulse"
              }`}
          />
          <span className="font-semibold text-sm">{data.machine_id}</span>
        </div>
      </TableCell>
      <TableCell className="px-4 py-3 text-center align-middle">
        {isUnknown ? (
          <span className="text-muted-foreground/40 text-xs font-mono">-</span>
        ) : (
          <div className="flex justify-center gap-3 text-xs font-mono text-muted-foreground">
            <span className="flex items-center gap-1">
              <Thermometer className="h-3 w-3" /> {data.temperature?.toFixed(1)}°C
            </span>
            <span className="flex items-center gap-1">
              <Activity className="h-3 w-3" /> {(data.vibration || 0).toFixed(2)}v
            </span>
          </div>
        )}
      </TableCell>
      <TableCell className="px-4 py-3 text-center align-middle font-mono font-medium">
        {isUnknown ? (
          <span className="text-muted-foreground/40">-</span>
        ) : (
          <span className={data.health_score < 75 ? "text-amber-600" : "text-green-600"}>
            {data.health_score?.toFixed(1)}%
          </span>
        )}
      </TableCell>
      <TableCell className="px-4 py-3 text-center align-middle font-mono font-medium">
        {isUnknown ? (
          <span className="text-muted-foreground/40">-</span>
        ) : (
          <span className={data.quality_score < 90 ? "text-amber-600" : "text-green-600"}>
            {data.quality_score?.toFixed(1)}%
          </span>
        )}
      </TableCell>
      <TableCell className="px-4 py-3 text-center align-middle">
        <Badge
          variant={isHighRisk ? "destructive" : "outline"}
          className={`text-[10px] uppercase font-bold tracking-wider ${isMediumRisk
              ? "bg-amber-100 text-amber-800 border-amber-200 hover:bg-amber-200"
              : isUnknown
                ? "opacity-40"
                : !isHighRisk
                  ? "bg-green-100 text-green-800 border-transparent hover:bg-green-200"
                  : ""
            }`}
        >
          {statusStr}
        </Badge>
      </TableCell>
      <TableCell className="px-4 py-3 text-right align-middle">
        <span
          className={`text-[10px] font-bold uppercase tracking-wider ${isHighRisk
              ? "text-destructive"
              : isMediumRisk
                ? "text-amber-600"
                : isUnknown
                  ? "text-muted-foreground/40"
                  : "text-green-600"
            }`}
        >
          {data.inspection_result}
        </span>
      </TableCell>
    </TableRow>
  );
}
