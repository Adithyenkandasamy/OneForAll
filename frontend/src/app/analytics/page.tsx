"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const analyticsData = [
  { month: "Jan", downtime: 45, efficiency: 82 },
  { month: "Feb", downtime: 30, efficiency: 85 },
  { month: "Mar", downtime: 20, efficiency: 89 },
  { month: "Apr", downtime: 25, efficiency: 87 },
  { month: "May", downtime: 15, efficiency: 92 },
  { month: "Jun", downtime: 10, efficiency: 95 },
];

export default function AnalyticsPage() {
  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Production Analytics</h1>
          <p className="text-gray-500 mt-1">Deep dive into historical performance metrics.</p>
        </div>
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <Card>
          <CardHeader>
            <CardTitle>Historical Efficiency vs Downtime</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[400px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analyticsData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E5E5" />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} />
                  <YAxis axisLine={false} tickLine={false} />
                  <Tooltip cursor={{ fill: '#F5F5F5' }} />
                  <Bar dataKey="efficiency" fill="#000000" name="Efficiency (%)" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="downtime" fill="#9CA3AF" name="Downtime (hrs)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
