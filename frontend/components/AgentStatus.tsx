/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, CheckCircle2, CircleDashed, Loader2 } from "lucide-react";

export type AgentState = 'idle' | 'working' | 'done' | 'error';

export interface Agent {
  id: string;
  name: string;
  role: string;
  status: AgentState;
  message?: string;
}

interface AgentStatusProps {
  agents: Agent[];
  compact?: boolean;
}

export function AgentStatus({ agents, compact = false }: AgentStatusProps) {
  return (
    <div className={`grid gap-2 ${compact ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'}`}>
      {agents.map((agent) => (
        <div 
          key={agent.id} 
          className={`flex items-center justify-between p-2 rounded-lg border bg-card text-card-foreground shadow-sm ${compact ? 'py-1.5 px-3' : 'p-3'}`}
        >
          <div className="flex items-center gap-3">
            <div className={`flex items-center justify-center rounded-full ${compact ? 'w-6 h-6' : 'w-8 h-8'} ${
              agent.status === 'working' ? 'bg-blue-100 text-blue-600 animate-pulse' :
              agent.status === 'done' ? 'bg-green-100 text-green-600' :
              'bg-muted text-muted-foreground'
            }`}>
              {agent.status === 'working' ? <Loader2 className={compact ? "h-3 w-3 animate-spin" : "h-4 w-4 animate-spin"} /> :
               agent.status === 'done' ? <CheckCircle2 className={compact ? "h-3 w-3" : "h-4 w-4"} /> :
               <Brain className={compact ? "h-3 w-3" : "h-4 w-4"} />}
            </div>
            <div>
              <p className={`font-medium leading-none ${compact ? 'text-xs' : 'text-sm'}`}>{agent.name}</p>
              {!compact && <p className="text-xs text-muted-foreground">{agent.role}</p>}
            </div>
          </div>
          <Badge variant={
            agent.status === 'working' ? "default" :
            agent.status === 'done' ? "secondary" :
            "outline"
          } className={compact ? "text-[10px] px-1 py-0 h-5" : ""}>
            {agent.status}
          </Badge>
        </div>
      ))}
    </div>
  );
}
