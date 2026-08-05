"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Calendar, PenTool, AlertTriangle } from "lucide-react";

export default function MaintenancePage() {
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
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-semibold text-gray-900">CNC Spindle Bearing (MCH-001)</span>
                  <span className="text-red-600 font-bold">92% Risk</span>
                </div>
                <Progress value={92} className="h-2 [&>div]:bg-red-600" />
                <p className="text-xs text-gray-500 mt-2">Vibration signature matches known failure pattern.</p>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-semibold text-gray-900">Hydraulic Pump Seal (MCH-002)</span>
                  <span className="text-amber-600 font-bold">78% Risk</span>
                </div>
                <Progress value={78} className="h-2 [&>div]:bg-amber-500" />
                <p className="text-xs text-gray-500 mt-2">Pressure drop detected during cycle peak.</p>
              </div>
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
                <div className="flex items-start gap-4 p-3 rounded-lg border border-gray-100 bg-gray-50">
                  <div className="bg-white p-2 rounded border border-gray-200 text-center min-w-[60px]">
                    <p className="text-xs font-bold text-red-600 uppercase">Oct</p>
                    <p className="text-xl font-black text-gray-900">12</p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Emergency Spindle Replacement</h4>
                    <p className="text-sm text-gray-500 mt-0.5">Assigned to: Tech Team Alpha</p>
                    <Badge variant="outline" className="mt-2 text-xs border-red-200 text-red-700 bg-red-50">Critical Priority</Badge>
                  </div>
                </div>
                
                <div className="flex items-start gap-4 p-3 rounded-lg border border-gray-100 bg-gray-50">
                  <div className="bg-white p-2 rounded border border-gray-200 text-center min-w-[60px]">
                    <p className="text-xs font-bold text-gray-500 uppercase">Oct</p>
                    <p className="text-xl font-black text-gray-900">15</p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Routine Conveyor Lubrication</h4>
                    <p className="text-sm text-gray-500 mt-0.5">Assigned to: Maintenance Crew B</p>
                    <Badge variant="outline" className="mt-2 text-xs">Standard</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
