"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Activity, Thermometer, Wind, Zap } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const telemetryData = [
  { time: "10:00", temp: 45, vibration: 0.2, power: 120 },
  { time: "10:05", temp: 48, vibration: 0.3, power: 125 },
  { time: "10:10", temp: 52, vibration: 0.8, power: 130 },
  { time: "10:15", temp: 51, vibration: 0.5, power: 128 },
  { time: "10:20", temp: 55, vibration: 1.2, power: 140 },
  { time: "10:25", temp: 53, vibration: 0.9, power: 135 },
  { time: "10:30", temp: 50, vibration: 0.4, power: 122 },
];

export default function MonitoringPage() {
  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Real-Time Monitoring</h1>
          <p className="text-gray-500 mt-1">Live telemetry feeds from factory sensors.</p>
        </div>
        <div className="flex items-center gap-2 text-sm font-medium text-green-600 bg-green-50 px-3 py-1 rounded-full border border-green-200">
          <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
          Live Stream Active
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SensorCard title="Average Temperature" value="51°C" icon={Thermometer} status="normal" />
        <SensorCard title="Vibration Levels" value="0.9mm/s" icon={Activity} status="warning" />
        <SensorCard title="Power Draw" value="135 kW" icon={Zap} status="normal" />
        <SensorCard title="Air Pressure" value="6.2 Bar" icon={Wind} status="normal" />
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Live Sensor Feed</CardTitle>
          <CardDescription>Temperature and Power draw over the last 30 minutes.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={telemetryData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E5E5" />
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} />
                <Tooltip />
                <Line type="monotone" dataKey="temp" name="Temperature (°C)" stroke="#000000" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="power" name="Power (kW)" stroke="#9CA3AF" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function SensorCard({ title, value, icon: Icon, status }: any) {
  return (
    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.3 }}>
      <Card>
        <CardContent className="p-6 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <h3 className={`text-2xl font-bold mt-1 ${status === 'warning' ? 'text-amber-600' : 'text-gray-900'}`}>{value}</h3>
          </div>
          <div className={`p-3 rounded-lg ${status === 'warning' ? 'bg-amber-50 text-amber-600' : 'bg-gray-50 text-gray-700'}`}>
            <Icon className="h-5 w-5" />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
