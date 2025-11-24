/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Terminal, Loader2, CheckCircle2, ExternalLink } from 'lucide-react';

interface ToolCall {
  id: string;
  agent: string;
  tool: string;
  args: Record<string, unknown>;
  status: 'running' | 'completed' | 'failed';
  result?: string;
  timestamp: number;
}

export interface WebSocketMessage {
  type: string;
  agent?: string;
  tool?: string;
  args?: Record<string, unknown>;
  result?: string;
  [key: string]: unknown;
}

interface AgentActivityStreamProps {
  lastMessage: WebSocketMessage | null;
  compact?: boolean;
}

export function AgentActivityStream({ lastMessage, compact = false }: AgentActivityStreamProps) {
  const [activities, setActivities] = useState<ToolCall[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!lastMessage) return;

    if (lastMessage.type === 'tool_call_started') {
      const newActivity: ToolCall = {
        id: `${lastMessage.agent}-${lastMessage.tool}-${Date.now()}`,
        agent: lastMessage.agent || 'unknown',
        tool: lastMessage.tool || 'unknown',
        args: lastMessage.args || {},
        status: 'running',
        timestamp: Date.now()
      };
      setActivities(prev => [...prev, newActivity]);
    } 
    else if (lastMessage.type === 'tool_call_completed') {
      setActivities(prev => {
        const newActivities = [...prev];
        // Find the most recent running activity for this tool/agent
        const index = newActivities.reverse().findIndex(
          a => a.agent === lastMessage.agent && a.tool === lastMessage.tool && a.status === 'running'
        );
        
        if (index !== -1) {
          const realIndex = newActivities.length - 1 - index;
          newActivities[realIndex] = {
            ...newActivities[realIndex],
            status: 'completed',
            result: lastMessage.result
          };
        }
        return newActivities; // reverse back handled by index logic
      });
    }
  }, [lastMessage]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      const scrollContainer = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
         scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [activities]);

  if (compact) {
    return (
      <ScrollArea className="h-full w-full p-2" ref={scrollRef}>
        <div className="space-y-2">
           {activities.length === 0 && (
              <div className="text-center text-muted-foreground text-xs py-4">
                Waiting for activity...
              </div>
            )}
            {activities.map((activity) => (
              <div key={activity.id} className="text-xs border-l-2 border-muted pl-2 relative">
                 <div className={`absolute -left-[3px] top-1 w-1.5 h-1.5 rounded-full ${
                    activity.status === 'running' ? 'bg-blue-500 animate-pulse' : 'bg-green-500'
                  }`} />
                  <div className="flex items-center gap-1 mb-0.5">
                    <span className="font-bold text-primary truncate max-w-[80px]">{activity.agent}</span>
                    <span className="text-muted-foreground">→</span>
                    <span className="font-mono text-muted-foreground truncate">{activity.tool}</span>
                  </div>
                  {activity.status === 'running' && <span className="text-blue-500 italic text-[10px]">Running...</span>}
                  {activity.status === 'completed' && <span className="text-green-600 text-[10px]">✓ Done</span>}
              </div>
            ))}
        </div>
      </ScrollArea>
    );
  }

  return (
    <Card className="h-[400px] flex flex-col w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Terminal className="h-4 w-4" />
          Agent Activity Stream
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-0 overflow-hidden">
        <ScrollArea className="h-full p-4" ref={scrollRef}>
          <div className="space-y-4">
            {activities.length === 0 && (
              <div className="text-center text-muted-foreground text-sm py-8">
                Waiting for agent activity...
              </div>
            )}
            
            {activities.map((activity) => (
              <div key={activity.id} className="flex flex-col gap-2 text-sm border-l-2 border-muted pl-4 relative">
                {/* Timeline dot */}
                <div className={`absolute -left-[5px] top-0 w-2 h-2 rounded-full ${
                  activity.status === 'running' ? 'bg-blue-500 animate-pulse' : 'bg-green-500'
                }`} />
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs font-mono">
                      {activity.agent}
                    </Badge>
                    <span className="font-semibold text-primary">
                      {activity.tool}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(activity.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                <div className="bg-muted/50 rounded p-2 font-mono text-xs overflow-x-auto">
                  <div className="text-muted-foreground mb-1">Input:</div>
                  <pre>{JSON.stringify(activity.args, null, 2)}</pre>
                </div>

                {activity.status === 'running' && (
                  <div className="flex items-center gap-2 text-blue-500 text-xs">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    Executing...
                  </div>
                )}

                {activity.status === 'completed' && activity.result && (
                  <div className="bg-green-500/10 rounded p-2 font-mono text-xs mt-1 border border-green-500/20">
                    <div className="text-green-600 mb-1 flex items-center gap-1">
                      <CheckCircle2 className="h-3 w-3" /> Result:
                    </div>
                    <div className="truncate">{activity.result}</div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
