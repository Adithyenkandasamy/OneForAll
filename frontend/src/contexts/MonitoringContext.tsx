"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

const MACHINES = Array.from({ length: 10 }, (_, i) => ({
    machine_id: `CNC${(i + 1).toString().padStart(2, "0")}`,
    temperature: 0,
    vibration: 0,
    health_score: 0,
    quality_score: 0,
    risk_level: "UNKNOWN",
    inspection_result: "WAITING",
}));

interface MonitoringContextValue {
    machines: any[];
    connected: boolean;
}

const MonitoringContext = createContext<MonitoringContextValue>({
    machines: MACHINES,
    connected: false,
});

export function MonitoringProvider({ children }: { children: React.ReactNode }) {
    const [machines, setMachines] = useState<any[]>(MACHINES);
    const [connected, setConnected] = useState(false);

    useEffect(() => {
        let reconnectTimeout: NodeJS.Timeout;
        let ws: WebSocket;

        const connect = () => {
            ws = new WebSocket("ws://127.0.0.1:8000/api/v1/ws/dashboard");

            ws.onopen = () => setConnected(true);

            ws.onmessage = (event) => {
                try {
                    const payload = JSON.parse(event.data);
                    const flat = {
                        machine_id: payload.machine_id,
                        ...payload.status,
                        ...payload.telemetry,
                    };
                    setMachines((prev) => {
                        const next = [...prev];
                        const idx = next.findIndex((m) => m.machine_id === flat.machine_id);
                        if (idx === -1) next.push(flat);
                        else next[idx] = flat;
                        return next.sort((a, b) => a.machine_id.localeCompare(b.machine_id));
                    });
                } catch (e) {
                    console.error("WS parse error", e);
                }
            };

            ws.onclose = () => {
                setConnected(false);
                reconnectTimeout = setTimeout(connect, 3000);
            };

            ws.onerror = () => ws.close();
        };

        connect();

        return () => {
            clearTimeout(reconnectTimeout);
            ws?.close();
        };
    }, []);

    return (
        <MonitoringContext.Provider value={{ machines, connected }}>
            {children}
        </MonitoringContext.Provider>
    );
}

export const useMonitoring = () => useContext(MonitoringContext);
