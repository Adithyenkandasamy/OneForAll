import { useState, useEffect, useCallback, useRef } from "react";

function rand(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randFloat(min: number, max: number, decimals = 1) {
  return parseFloat((Math.random() * (max - min) + min).toFixed(decimals));
}

function jitter(base: number, range: number) {
  return Math.max(0, base + rand(-range, range));
}

/* ─── Dashboard ─────────────────────────────────────────────── */
export function generateProductionData() {
  const hours = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"];
  return hours.map((time) => ({
    time,
    actual: rand(3800, 11000),
    target: rand(4000, 10800),
  }));
}

export function generateEfficiencyData() {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  return days.map((day) => ({
    day,
    oee: rand(75, 95),
  }));
}

export function generateAlerts() {
  const types = ["critical", "warning", "info"] as const;
  const messages = [
    "CNC Machine 04 Spindle Overheating",
    "Conveyor Belt B vibration anomaly detected",
    "Routine maintenance completed for Robot Arm 2",
    "Hydraulic Press pressure spike on Line 3",
    "Laser Cutter coolant level low",
    "Assembly Robot Joint A torque drift detected",
    "Packaging Line 02 throughput drop",
    "Welding Robot arc instability on Station 7",
  ];
  const times = ["1 min ago", "5 mins ago", "15 mins ago", "30 mins ago", "1 hr ago", "2 hrs ago"];
  return Array.from({ length: rand(2, 4) }, (_, i) => ({
    id: i + 1,
    type: types[rand(0, 2)],
    message: messages[rand(0, messages.length - 1)],
    time: times[rand(0, times.length - 1)],
  }));
}

export function generateDashboardMetrics() {
  return {
    oee: randFloat(82, 92),
    activeMachines: rand(1220, 1260),
    totalProduction: rand(9800, 11200),
    energyConsumption: randFloat(3.8, 4.6),
  };
}

export function generatePredictiveInsights() {
  return [
    {
      label: "Conveyor Motor Risk Score",
      value: rand(70, 90),
      status: "High" as const,
      desc: "Predicted failure in < 48 hours based on vibration anomalies.",
    },
    {
      label: "Hydraulic Press Pump",
      value: rand(8, 25),
      status: "Nominal" as const,
      desc: "Operating within normal parameters. Next service in 14 days.",
    },
    {
      label: "Assembly Robot Joint A",
      value: rand(35, 55),
      status: "Moderate" as const,
      desc: "Torque variations detected. Schedule inspection during next downtime.",
    },
  ];
}

/* ─── Machines ──────────────────────────────────────────────── */
const MACHINE_NAMES = [
  "CNC Milling Station A",
  "Hydraulic Press 500T",
  "Assembly Robot Arm 1",
  "Conveyor System B",
  "Packaging Line 02",
  "Laser Cutter Beta",
  "Welding Robot Station",
  "CNC Lathe Gamma",
  "Drill Press Alpha",
  "Grinding Station 3",
];

export function generateMachinesData() {
  return MACHINE_NAMES.map((name, i) => {
    const health = rand(40, 99);
    const status =
      health >= 85 ? "Running" : health >= 65 ? "Warning" : "Maintenance";
    return {
      id: `MCH-${String(i + 1).padStart(3, "0")}`,
      name,
      status,
      health,
      oee: status === "Maintenance" ? 0 : rand(60, 95),
      uptime: `${rand(0, 150)}h ${rand(0, 59)}m`,
      temperature: randFloat(35, 95),
      vibration: randFloat(0.1, 4.5),
    };
  });
}

/* ─── Plants ────────────────────────────────────────────────── */
const PLANT_BASES = [
  { id: "PL-01", name: "Berlin Gigafactory", location: "Germany", baseHealth: 96, baseWorkers: 450, baseOutput: 1200 },
  { id: "PL-02", name: "Texas Assembly Plant", location: "USA", baseHealth: 82, baseWorkers: 820, baseOutput: 2400 },
  { id: "PL-03", name: "Shanghai Manufacturing", location: "China", baseHealth: 98, baseWorkers: 1200, baseOutput: 4500 },
  { id: "PL-04", name: "Tokyo Robotics Hub", location: "Japan", baseHealth: 65, baseWorkers: 210, baseOutput: 400 },
];

export function generatePlantsData() {
  return PLANT_BASES.map((p) => {
    const health = jitter(p.baseHealth, 5);
    const status = health >= 90 ? "Optimal" : health >= 70 ? "Warning" : "Maintenance";
    return {
      ...p,
      health,
      status,
      workers: jitter(p.baseWorkers, 10),
      output: `${jitter(p.baseOutput, 50)}/day`,
    };
  });
}

/* ─── Analytics ─────────────────────────────────────────────── */
export function generateAnalyticsData() {
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"];
  return months.map((month) => ({
    month,
    downtime: rand(5, 50),
    efficiency: rand(78, 96),
  }));
}

/* ─── Maintenance ───────────────────────────────────────────── */
export function generateMaintenanceRisks() {
  const components = [
    { name: "CNC Spindle Bearing (MCH-001)", baseRisk: 92 },
    { name: "Hydraulic Pump Seal (MCH-002)", baseRisk: 78 },
    { name: "Conveyor Motor Drive (MCH-004)", baseRisk: 65 },
    { name: "Laser Cutter Lens Assembly (MCH-006)", baseRisk: 55 },
  ];
  return components.slice(0, rand(2, 4)).map((c) => ({
    ...c,
    risk: Math.min(99, jitter(c.baseRisk, 5)),
  }));
}

export function generateMaintenanceSchedule() {
  const tasks = [
    { title: "Emergency Spindle Replacement", team: "Tech Team Alpha", priority: "Critical", day: 12, month: "Oct" },
    { title: "Routine Conveyor Lubrication", team: "Maintenance Crew B", priority: "Standard", day: 15, month: "Oct" },
    { title: "Hydraulic Seal Replacement", team: "Tech Team Alpha", priority: "High", day: 18, month: "Oct" },
    { title: "Laser Optics Calibration", team: "Optics Division", priority: "Standard", day: 22, month: "Oct" },
  ];
  return tasks.slice(0, rand(2, 4));
}

/* ─── Team ──────────────────────────────────────────────────── */
const TEAM_BASES = [
  { name: "Sarah Connor", role: "Plant Manager", email: "sarah@oneforall.com" },
  { name: "John Smith", role: "Lead Engineer", email: "john@oneforall.com" },
  { name: "Elena Rodriguez", role: "Maintenance Supervisor", email: "elena@oneforall.com" },
  { name: "David Kim", role: "Robotics Technician", email: "david@oneforall.com" },
  { name: "Aiko Tanaka", role: "Quality Analyst", email: "aiko@oneforall.com" },
  { name: "Marcus Weber", role: "Safety Officer", email: "marcus@oneforall.com" },
];

export function generateTeamData() {
  const statuses = ["Active", "Active", "Active", "On Leave"];
  return TEAM_BASES.map((t) => ({
    ...t,
    status: statuses[rand(0, statuses.length - 1)],
    lastActive: `${rand(1, 30)} mins ago`,
  }));
}

/* ─── Hook: useRealtimeData ─────────────────────────────────── */
export function useRealtimeData<T>(
  generator: () => T,
  intervalMs: number = 5000
): T {
  const [data, setData] = useState<T>(generator);
  const generatorRef = useRef(generator);
  generatorRef.current = generator;

  useEffect(() => {
    const id = setInterval(() => {
      setData(generatorRef.current());
    }, intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);

  return data;
}
