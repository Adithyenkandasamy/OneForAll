"use client";

import { useRealtimeData, generateTeamData } from "@/lib/mockData";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Mail, Phone } from "lucide-react";

export default function TeamPage() {
  const teamData = useRealtimeData(generateTeamData, 10000);

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Team Directory</h1>
        <p className="text-gray-500 mt-1">Manage personnel and assignments.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {teamData.map((member, i) => (
          <Card key={i}>
            <CardContent className="p-6 flex flex-col items-center text-center">
              <Avatar className="h-20 w-20 mb-4">
                <AvatarFallback className="text-lg bg-gray-100 text-gray-900 font-bold">{member.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
              </Avatar>
              <h3 className="font-bold text-gray-900 text-lg">{member.name}</h3>
              <p className="text-sm text-gray-500 mb-3">{member.role}</p>
              <Badge variant="outline" className={member.status === 'Active' ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'}>
                {member.status}
              </Badge>
              <p className="text-xs text-gray-400 mt-2">Last active: {member.lastActive}</p>
              <div className="mt-6 flex justify-center gap-3 w-full border-t pt-4 border-gray-100">
                <button className="text-gray-400 hover:text-black transition-colors"><Mail className="h-4 w-4" /></button>
                <button className="text-gray-400 hover:text-black transition-colors"><Phone className="h-4 w-4" /></button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
