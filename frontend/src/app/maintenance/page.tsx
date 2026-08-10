"use client";

import { useRealtimeData, generateMaintenanceRisks, generateMaintenanceSchedule } from "@/lib/mockData";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Calendar, AlertTriangle } from "lucide-react";

export default function MaintenancePage() {
  const risks = useRealtimeData(generateMaintenanceRisks, 5000);
  const schedule = useRealtimeData(generateMaintenanceSchedule, 8000);

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Predictive Maintenance</h1>
          <p className="text-gray-500 mt-1">AI-driven failure prediction and maintenance scheduling.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.4 }}>
          <Card className="h-full border-red-100 shadow-sm">
            <CardHeader className="bg-red-50/50 border-b border-red-100">
              <CardTitle className="text-red-900 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                High Risk Components
              </CardTitle>
              <CardDescription className="text-red-700/80">Predicted failure within 72 hours</CardDescription>
            </CardHeader>
            <CardContent className="pt-6 space-y-6">
              {risks.map((r, i) => (
                <div key={i}>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="font-semibold text-gray-900">{r.name}</span>
                    <span className={`font-bold ${r.risk >= 80 ? "text-red-600" : r.risk >= 60 ? "text-amber-600" : "text-gray-600"}`}>
                      {r.risk}% Risk
                    </span>
                  </div>
                  <Progress value={r.risk} className={`h-2 [&>div]:bg-current ${r.risk >= 80 ? "text-red-600" : r.risk >= 60 ? "text-amber-500" : "text-gray-400"}`} />
                  <p className="text-xs text-gray-500 mt-2">Vibration signature matches known failure pattern.</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.4, delay: 0.1 }}>
          <Card className="h-full shadow-sm">
            <CardHeader className="border-b border-gray-100">
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-gray-500" />
                Upcoming Schedule
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-4">
                {schedule.map((s, i) => (
                  <div key={i} className="flex items-start gap-4 p-3 rounded-lg border border-gray-100 bg-gray-50">
                    <div className="bg-white p-2 rounded border border-gray-200 text-center min-w-[60px]">
                      <p className={`text-xs font-bold uppercase ${s.priority === "Critical" ? "text-red-600" : s.priority === "High" ? "text-amber-600" : "text-gray-500"}`}>{s.month}</p>
                      <p className="text-xl font-black text-gray-900">{s.day}</p>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{s.title}</h4>
                      <p className="text-sm text-gray-500 mt-0.5">Assigned to: {s.team}</p>
                      <Badge variant="outline" className={`mt-2 text-xs ${s.priority === "Critical" ? "border-red-200 text-red-700 bg-red-50" : s.priority === "High" ? "border-amber-200 text-amber-700 bg-amber-50" : ""}`}>
                        {s.priority}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
