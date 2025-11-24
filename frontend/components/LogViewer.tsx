import React, { useRef, useEffect } from 'react';
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Copy } from "lucide-react";

interface LogEntry {
  timestamp: string;
  type: string;
  message: string;
  data?: any;
}

interface LogViewerProps {
  logs: LogEntry[];
}

export function LogViewer({ logs }: LogViewerProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

  const copyLogs = () => {
    const text = logs.map(l => `[${l.timestamp}] [${l.type}] ${l.message} ${l.data ? JSON.stringify(l.data) : ''}`).join('\n');
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="flex flex-col h-full border rounded-md bg-black/90 font-mono text-xs">
      <div className="flex items-center justify-between p-2 border-b bg-muted/20">
        <span className="font-semibold text-muted-foreground">System Logs</span>
        <Button variant="ghost" size="icon" onClick={copyLogs} className="h-6 w-6">
          <Copy className="h-3 w-3" />
        </Button>
      </div>
      <ScrollArea className="flex-1 p-2">
        <div className="space-y-1">
          {logs.map((log, i) => (
            <div key={i} className="break-all">
              <span className="text-muted-foreground">[{log.timestamp}]</span>{' '}
              <span className={`font-bold ${getColorForType(log.type)}`}>[{log.type.toUpperCase()}]</span>{' '}
              <span className="text-foreground">{log.message}</span>
              {log.data && (
                <pre className="mt-1 ml-4 text-[10px] text-muted-foreground overflow-x-auto">
                  {JSON.stringify(log.data, null, 2)}
                </pre>
              )}
            </div>
          ))}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>
    </div>
  );
}

function getColorForType(type: string): string {
  switch (type) {
    case 'error': return 'text-red-500';
    case 'status': return 'text-blue-500';
    case 'agent_update': return 'text-green-500';
    case 'tool_call_started': return 'text-yellow-500';
    default: return 'text-gray-500';
  }
}
