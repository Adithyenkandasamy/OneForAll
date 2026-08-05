"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  BatteryCharging,
  Cpu,
  Factory,
  CheckCircle2,
} from "lucide-react";

// Mock Data
const productionData = [
  { time: "08:00", actual: 4000, target: 4200 },
  { time: "10:00", actual: 5200, target: 4800 },
  { time: "12:00", actual: 6100, target: 5500 },
  { time: "14:00", actual: 7500, target: 7000 },
  { time: "16:00", actual: 8200, target: 8100 },
  { time: "18:00", actual: 9500, target: 9200 },
  { time: "20:00", actual: 10400, target: 10500 },
];

const efficiencyData = [
  { day: "Mon", oee: 82 },
  { day: "Tue", oee: 85 },
  { day: "Wed", oee: 78 },
  { day: "Thu", oee: 90 },
  { day: "Fri", oee: 88 },
  { day: "Sat", oee: 92 },
  { day: "Sun", oee: 87 },
];

const alerts = [
  { id: 1, type: "critical", message: "CNC Machine 04 Spindle Overheating", time: "2 mins ago" },
  { id: 2, type: "warning", message: "Conveyor Belt B vibration anomaly detected", time: "15 mins ago" },
  { id: 3, type: "info", message: "Routine maintenance completed for Robot Arm 2", time: "1 hr ago" },
];

export default function Dashboard() {
  return (
    <div className="space-y-6 pb-12">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Enterprise Overview</h1>
          <p className="text-gray-500 mt-1">Real-time telemetry and AI insights across all facilities.</p>
        </div>
        <div className="flex gap-2">
          <Badge variant="outline" className="px-3 py-1 bg-green-50 text-green-700 border-green-200">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              All Systems Nominal
            </span>
          </Badge>
          <Badge variant="outline" className="px-3 py-1">
            Last updated: Just now
          </Badge>
        </div>
      </div>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Overall Equipment Effectiveness"
          value="87.4%"
          trend="+2.1%"
          isPositive={true}
          icon={Activity}
          delay={0.1}
        />
        <MetricCard
          title="Active Machines"
          value="1,248"
          trend="-3"
          isPositive={false}
          icon={Cpu}
          delay={0.2}
        />
        <MetricCard
          title="Total Production (Units)"
          value="10,400"
          trend="+1,200"
          isPositive={true}
          icon={Factory}
          delay={0.3}
        />
        <MetricCard
          title="Energy Consumption"
          value="4.2 MWh"
          trend="-0.4 MWh"
          isPositive={true}
          icon={BatteryCharging}
          delay={0.4}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart */}
        <motion.div 
          className="lg:col-span-2"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Production Output vs Target</CardTitle>
              <CardDescription>Daily production output across all facilities</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={productionData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#000000" stopOpacity={0.1}/>
                        <stop offset="95%" stopColor="#000000" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E5E5" />
                    <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} dy={10} />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} dx={-10} />
                    <Tooltip 
                      contentStyle={{ borderRadius: '8px', border: '1px solid #E5E5E5', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    />
                    <Area type="monotone" dataKey="actual" stroke="#000000" strokeWidth={2} fillOpacity={1} fill="url(#colorActual)" />
                    <Area type="monotone" dataKey="target" stroke="#9CA3AF" strokeWidth={2} strokeDasharray="5 5" fill="none" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Alerts Panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <Card className="h-full flex flex-col">
            <CardHeader>
              <CardTitle className="flex justify-between items-center">
                Active Alerts
                <Badge variant="destructive" className="ml-2">3 New</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-auto">
              <div className="space-y-4">
                {alerts.map((alert) => (
                  <div key={alert.id} className="flex items-start gap-3 p-3 rounded-lg border border-gray-100 bg-gray-50/50">
                    {alert.type === 'critical' ? (
                      <AlertTriangle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                    ) : alert.type === 'warning' ? (
                      <AlertTriangle className="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
                    ) : (
                      <CheckCircle2 className="h-5 w-5 text-blue-500 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <p className="text-sm font-medium text-gray-900 leading-tight mb-1">{alert.message}</p>
                      <p className="text-xs text-gray-500">{alert.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Bottom Section: Efficiency & Predictive Maintenance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.7 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>OEE Weekly Trend</CardTitle>
              <CardDescription>Overall Equipment Effectiveness over the last 7 days</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[250px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={efficiencyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E5E5" />
                    <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} dy={10} />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#6B7280', fontSize: 12}} />
                    <Tooltip cursor={{fill: '#F5F5F5'}} />
                    <Bar dataKey="oee" fill="#000000" radius={[4, 4, 0, 0]} maxBarSize={40} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          <Card className="h-full">
            <CardHeader>
              <CardTitle>AI Predictive Insights</CardTitle>
              <CardDescription>Machine learning models predicting future anomalies</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="font-medium text-gray-700">Conveyor Motor Risk Score</span>
                    <span className="text-amber-600 font-bold">High (82%)</span>
                  </div>
                  <Progress value={82} className="h-2 [&>div]:bg-amber-500" />
                  <p className="text-xs text-gray-500 mt-2">Predicted failure in &lt; 48 hours based on vibration anomalies.</p>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="font-medium text-gray-700">Hydraulic Press Pump</span>
                    <span className="text-green-600 font-bold">Nominal (14%)</span>
                  </div>
                  <Progress value={14} className="h-2 [&>div]:bg-green-500" />
                  <p className="text-xs text-gray-500 mt-2">Operating within normal parameters. Next service in 14 days.</p>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="font-medium text-gray-700">Assembly Robot Joint A</span>
                    <span className="text-gray-900 font-bold">Moderate (45%)</span>
                  </div>
                  <Progress value={45} className="h-2 [&>div]:bg-gray-800" />
                  <p className="text-xs text-gray-500 mt-2">Torque variations detected. Schedule inspection during next downtime.</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string | number;
  trend: string;
  isPositive: boolean;
  icon: React.ElementType;
  delay: number;
}

function MetricCard({ title, value, trend, isPositive, icon: Icon, delay }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
    >
      <Card>
        <CardContent className="p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-gray-500">{title}</p>
              <h3 className="text-3xl font-bold mt-2 text-gray-900">{value}</h3>
            </div>
            <div className="p-2 bg-gray-50 rounded-lg">
              <Icon className="h-5 w-5 text-gray-700" />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-2">
            <Badge variant="secondary" className={cn("px-2 py-0.5 text-xs font-medium", isPositive ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700")}>
              {isPositive ? <ArrowUpRight className="h-3 w-3 mr-1" /> : <ArrowDownRight className="h-3 w-3 mr-1" />}
              {trend}
            </Badge>
            <span className="text-xs text-gray-500">vs last week</span>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

function cn(...classes: (string | undefined)[]) {
  return classes.filter(Boolean).join(" ");
}
