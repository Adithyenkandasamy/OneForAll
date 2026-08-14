"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import api from "@/lib/api";

export interface MachineTelemetry {
  machine_id: string;
  temperature: number | null;
  vibration: number | null;
  health_score: number;
  quality_score: number;
  risk_level: string;
  inspection_result: string;
  status_time?: string;
}

type MonitoringSource = "live" | "demo";

const DEMO_MACHINE_PROFILES = [
  { temperature: 54, vibration: 0.42, health: 97, quality: 99 },
  { temperature: 68, vibration: 1.15, health: 89, quality: 95 },
  { temperature: 81, vibration: 2.45, health: 74, quality: 87 },
  { temperature: 62, vibration: 0.78, health: 93, quality: 97 },
  { temperature: 91, vibration: 3.35, health: 61, quality: 79 },
  { temperature: 72, vibration: 1.82, health: 83, quality: 91 },
  { temperature: 58, vibration: 0.56, health: 96, quality: 98 },
  { temperature: 76, vibration: 2.06, health: 80, quality: 89 },
  { temperature: 65, vibration: 0.94, health: 91, quality: 96 },
  { temperature: 85, vibration: 2.74, health: 70, quality: 84 },
] as const;

function demoMachines(tick = 0): MachineTelemetry[] {
  return DEMO_MACHINE_PROFILES.map((profile, index) => {
    const phase = tick / 3 + index * 0.8;
    const health = Math.round(profile.health + Math.sin(phase) * 3);
    const quality = Math.round(profile.quality + Math.cos(phase) * 2);
    const risk = health < 70 ? "HIGH" : health < 85 ? "MEDIUM" : "LOW";

    return {
      machine_id: `CNC${String(index + 1).padStart(2, "0")}`,
      temperature: Number((profile.temperature + Math.sin(phase) * 2.5).toFixed(1)),
      vibration: Number((profile.vibration + Math.abs(Math.cos(phase)) * 0.16).toFixed(2)),
      health_score: health,
      quality_score: quality,
      risk_level: risk,
      inspection_result: risk === "HIGH" ? "STOP & INSPECT" : risk === "MEDIUM" ? "INSPECT" : "NOMINAL",
      status_time: new Date().toISOString(),
    };
  });
}

interface MonitoringContextValue {
  machines: MachineTelemetry[];
  connected: boolean;
  source: MonitoringSource;
}

const MonitoringContext = createContext<MonitoringContextValue>({
  machines: demoMachines(),
  connected: false,
  source: "demo",
});

export function MonitoringProvider({ children }: { children: React.ReactNode }) {
  const [machines, setMachines] = useState<MachineTelemetry[]>(demoMachines());
  const [connected, setConnected] = useState(false);
  const [source, setSource] = useState<MonitoringSource>("demo");

  useEffect(() => {
    let active = true;
    let tick = 0;

    const loadMonitoring = async () => {
      try {
        const response = await api.get<{ machines?: MachineTelemetry[] }>(
          "/api/v1/agents/quality/dashboard"
        );
        const liveMachines = response.data.machines ?? [];

        const newestUpdate = Math.max(
          ...liveMachines.map((machine) => {
            const timestamp = machine.status_time ? Date.parse(machine.status_time) : Number.NaN;
            return Number.isNaN(timestamp) ? 0 : timestamp;
          })
        );
        const hasFreshTelemetry = newestUpdate > 0 && Date.now() - newestUpdate < 15_000;

        if (liveMachines.length > 0 && hasFreshTelemetry) {
          if (!active) return;
          setMachines(liveMachines);
          setConnected(true);
          setSource("live");
          return;
        }
      } catch {
        // No live telemetry is available yet; the labelled demo feed remains usable.
      }

      if (!active) return;
      tick += 1;
      setMachines(demoMachines(tick));
      setConnected(false);
      setSource("demo");
    };

    void loadMonitoring();
    const interval = window.setInterval(() => void loadMonitoring(), 5000);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  return (
    <MonitoringContext.Provider value={{ machines, connected, source }}>
      {children}
    </MonitoringContext.Provider>
  );
}

export const useMonitoring = () => useContext(MonitoringContext);
