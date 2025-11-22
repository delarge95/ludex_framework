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
}

export function AgentStatus({ agents }: AgentStatusProps) {
  const getStatusIcon = (status: AgentState) => {
    switch (status) {
      case 'working':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case 'done':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'error':
        return <Brain className="h-4 w-4 text-red-500" />;
      default:
        return <CircleDashed className="h-4 w-4 text-gray-300" />;
    }
  };

  const getStatusColor = (status: AgentState) => {
    switch (status) {
      case 'working':
        return "border-blue-500 bg-blue-50";
      case 'done':
        return "border-green-500 bg-green-50";
      case 'error':
        return "border-red-500 bg-red-50";
      default:
        return "border-gray-200";
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <Brain className="h-5 w-5" />
          The Studio
        </CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`flex items-center justify-between p-3 rounded-lg border ${getStatusColor(agent.status)} transition-all duration-300`}
          >
            <div className="flex items-center gap-3">
              {getStatusIcon(agent.status)}
              <div>
                <p className="font-medium text-sm">{agent.name}</p>
                <p className="text-xs text-gray-500">{agent.role}</p>
              </div>
            </div>
            <Badge variant={agent.status === 'working' ? 'default' : 'secondary'}>
              {agent.status}
            </Badge>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
