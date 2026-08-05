"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Factory, MapPin, Activity } from "lucide-react";

const plantsData = [
  { id: "PL-01", name: "Berlin Gigafactory", location: "Germany", status: "Optimal", health: 96, workers: 450, output: "1,200/day" },
  { id: "PL-02", name: "Texas Assembly Plant", location: "USA", status: "Warning", health: 82, workers: 820, output: "2,400/day" },
  { id: "PL-03", name: "Shanghai Manufacturing", location: "China", status: "Optimal", health: 98, workers: 1200, output: "4,500/day" },
  { id: "PL-04", name: "Tokyo Robotics Hub", location: "Japan", status: "Maintenance", health: 65, workers: 210, output: "400/day" },
];

export default function PlantsPage() {
  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Global Plants</h1>
          <p className="text-gray-500 mt-1">Overview of all manufacturing facilities.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
        {plantsData.map((plant, idx) => (
          <motion.div
            key={plant.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: idx * 0.1 }}
          >
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-xl font-bold">{plant.name}</CardTitle>
                <Factory className="h-5 w-5 text-gray-500" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center text-sm text-gray-500 mb-4">
                  <MapPin className="h-4 w-4 mr-1" />
                  {plant.location}
                </div>
                
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">Plant Health</span>
                      <span className="font-bold">{plant.health}%</span>
                    </div>
                    <Progress value={plant.health} className={`h-2 ${plant.health > 90 ? '[&>div]:bg-green-500' : plant.health > 70 ? '[&>div]:bg-amber-500' : '[&>div]:bg-red-500'}`} />
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 pt-4 border-t">
                    <div>
                      <p className="text-xs text-gray-500">Status</p>
                      <Badge variant="outline" className={`mt-1 ${plant.status === 'Optimal' ? 'bg-green-50 text-green-700' : plant.status === 'Warning' ? 'bg-amber-50 text-amber-700' : 'bg-red-50 text-red-700'}`}>
                        {plant.status}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Output</p>
                      <p className="font-semibold mt-1 text-sm">{plant.output}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Workers</p>
                      <p className="font-semibold mt-1 text-sm">{plant.workers}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
