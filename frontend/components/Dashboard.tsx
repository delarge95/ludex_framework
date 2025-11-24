/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import React, { useState, useEffect } from 'react';
import { AgentActivityStream, WebSocketMessage } from './AgentActivityStream';
import { SettingsModal } from './SettingsModal';
import { AgentStatus, Agent } from './AgentStatus';
import { GDDViewer } from './GDDViewer';
import { InputForm } from './InputForm';
import { DirectorQuestions } from './DirectorQuestions';
import { InteractiveGate } from './InteractiveGate';
import { MetricsDashboard } from './MetricsDashboard';
import { LogViewer } from './LogViewer';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export function Dashboard() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [markdown, setMarkdown] = useState<string>("");
  const [agents, setAgents] = useState<Agent[]>([
    { id: '1', name: 'Director', role: 'Concept Validation', status: 'idle' },
    { id: '2', name: 'Market Analyst', role: 'Market Analysis', status: 'idle' },
    { id: '3', name: 'Mechanics Designer', role: 'Game Mechanics', status: 'idle' },
    { id: '4', name: 'System Designer', role: 'Tech Stack', status: 'idle' },
    { id: '5', name: 'Producer', role: 'Production Plan', status: 'idle' },
    { id: '6', name: 'Narrative Architect', role: 'Story Structure', status: 'idle' },
    { id: '7', name: 'Character Designer', role: 'Character Development', status: 'idle' },
    { id: '8', name: 'World Builder', role: 'World Lore', status: 'idle' },
    { id: '9', name: 'Dialogue Designer', role: 'Dialogue Systems', status: 'idle' },
    { id: '10', name: 'Technical Validator', role: 'Feasibility Check', status: 'idle' },
    { id: '11', name: 'UI/UX Designer', role: 'Interface Design', status: 'idle' },
    { id: '12', name: 'Art Director', role: 'Visual Direction', status: 'idle' },
    { id: '13', name: 'Character Artist', role: 'Character Visuals', status: 'idle' },
    { id: '14', name: 'Environment Artist', role: 'Environment Design', status: 'idle' },
    { id: '15', name: 'Animation Director', role: 'Animation Planning', status: 'idle' },
    { id: '16', name: 'Camera Designer', role: 'Camera Systems', status: 'idle' },
    { id: '17', name: 'Audio Director', role: 'Audio Design', status: 'idle' },
    { id: '18', name: 'Physics Engineer', role: 'Physics Specs', status: 'idle' },
    { id: '19', name: 'Economy Balancer', role: 'Economy Design', status: 'idle' },
    { id: '20', name: 'Network Architect', role: 'Networking', status: 'idle' },
    { id: '21', name: 'Level Designer', role: 'Level Design', status: 'idle' },
    { id: '22', name: 'Performance Analyst', role: 'Performance Specs', status: 'idle' },
    { id: '23', name: 'QA Planner', role: 'QA Strategy', status: 'idle' },
    { id: '24', name: 'GDD Writer', role: 'Document Compilation', status: 'idle' },
  ]);

  // Director Questions State
  const [directorQuestions, setDirectorQuestions] = useState<string[]>([]);
  
  // Interactive Gate State
  const [currentGate, setCurrentGate] = useState<string | null>(null);
  const [gateData, setGateData] = useState<any>(null);
  
  // Metrics State
  const [metrics, setMetrics] = useState<any>(null);

  // Activity Stream State
  const [lastActivityMessage, setLastActivityMessage] = useState<WebSocketMessage | null>(null);

  // Logs State
  const [logs, setLogs] = useState<any[]>([]);

  // WebSocket ref
  const wsRef = React.useRef<WebSocket | null>(null);

  const addLog = (type: string, message: string, data?: any) => {
    setLogs(prev => [...prev, {
      timestamp: new Date().toLocaleTimeString(),
      type,
      message,
      data
    }]);
  };

  const handleDirectorAnswer = async (answer: string) => {
    // Send answer back to backend
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: 'director_answer',
        answer: answer
      }));
      setDirectorQuestions([]);
      addLog('info', `Director Answer: ${answer}`);
    }
  };

  const handleGateApprove = async () => {
    if (wsRef.current && currentGate) {
      wsRef.current.send(JSON.stringify({
        type: 'gate_approve',
        gate: currentGate
      }));
      addLog('info', `Gate Approved: ${currentGate}`);
      setCurrentGate(null);
      setGateData(null);
    }
  };

  const handleGateReject = async () => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: 'gate_reject'
      }));
      addLog('info', `Gate Rejected`);
      setIsGenerating(false);
      setCurrentGate(null);
      setGateData(null);
      wsRef.current.close();
    }
  };

  const handleStartGeneration = async (idea: string) => {
    setIsGenerating(true);
    setMarkdown("");
    setDirectorQuestions([]);
    setCurrentGate(null);
    setLastActivityMessage(null);
    setLogs([]); // Clear logs on new run
    
    // Reset agents
    setAgents(prev => prev.map(a => ({ ...a, status: 'idle', message: undefined })));

    try {
      addLog('status', 'Starting generation...');
      // Start generation via API
      const response = await fetch('http://localhost:9090/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept: idea, genre: "Unknown" }),
      });

      if (!response.ok) {
        throw new Error('Failed to start generation');
      }

      // Connect to WebSocket for updates
      const ws = new WebSocket('ws://127.0.0.1:9090/ws');
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('Connected to WebSocket');
        addLog('status', 'Connected to WebSocket');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data) as WebSocketMessage;
        
        // Log everything except frequent metrics/gdd updates to avoid spam, or log them nicely
        if (data.type !== 'gdd_update') {
           // console.log('WS Message:', data);
        }

        if (data.type === 'director_questions') {
          setDirectorQuestions(data.questions as string[]);
          addLog('info', 'Director asking questions', data.questions);
        } else if (data.type === 'gate_reached') {
          setCurrentGate(data.gate_name as string);
          setGateData(data.data);
          addLog('info', `Gate Reached: ${data.gate_name}`);
        } else if (data.type === 'metrics_update') {
          setMetrics(data.metrics);
        } else if (data.type === 'tool_call_started') {
          setLastActivityMessage(data);
          addLog('tool_call_started', `Tool Start: ${data.tool}`, data.args);
        } else if (data.type === 'tool_call_completed') {
          setLastActivityMessage(data);
          addLog('tool_call_completed', `Tool End: ${data.tool}`, { output_preview: typeof data.output === 'string' ? data.output.substring(0, 50) + '...' : 'Data' });
        } else if (data.type === 'agent_update') {
          setAgents(prev => prev.map(a => {
            const agentNameMap: Record<string, string> = {
              'director': 'Director',
              'market_analyst': 'Market Analyst',
              'mechanics_designer': 'Mechanics Designer',
              'system_designer': 'System Designer',
              'producer': 'Producer',
              'narrative_architect': 'Narrative Architect',
              'character_designer': 'Character Designer',
              'world_builder': 'World Builder',
              'dialogue_system_designer': 'Dialogue Designer',
              'technical_feasibility_validator': 'Technical Validator',
              'uiux_designer': 'UI/UX Designer',
              'art_director': 'Art Director',
              'character_artist': 'Character Artist',
              'environment_artist': 'Environment Artist',
              'animation_director': 'Animation Director',
              'camera_designer': 'Camera Designer',
              'audio_director': 'Audio Director',
              'physics_engineer': 'Physics Engineer',
              'economy_balancer': 'Economy Balancer',
              'network_architect': 'Network Architect',
              'level_designer': 'Level Designer',
              'performance_analyst': 'Performance Analyst',
              'qa_planner': 'QA Planner',
              'gdd_writer': 'GDD Writer'
            };
            
            const agentKey = data.agent as string;
            if (agentKey && agentNameMap[agentKey] === a.name) {
              return { ...a, status: data.status === 'done' ? 'done' : 'working' };
            }
            return a;
          }));
          addLog('agent_update', `Agent Update: ${data.agent}`, data.data);
        } else if (data.type === 'gdd_update') {
          setMarkdown(data.markdown as string);
        } else if (data.type === 'status') {
          addLog('status', `Status: ${data.status} - ${data.message}`);
          if (data.status === 'completed') {
            setIsGenerating(false);
            ws.close();
          }
        } else if (data.type === 'error') {
          console.error('Backend Error:', data.message);
          addLog('error', `Backend Error: ${data.message}`);
          setIsGenerating(false);
          ws.close();
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket Error:', error);
        addLog('error', 'WebSocket Error');
        setIsGenerating(false);
      };

    } catch (error) {
      console.error('Error starting generation:', error);
      addLog('error', `Error starting generation: ${error}`);
      setIsGenerating(false);
    }
  };

  // Fetch metrics periodically
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('http://localhost:9090/metrics');
        if (response.ok) {
          const data = await response.json();
          setMetrics(data);
        }
      } catch (error) {
        // Silently fail
      }
    };

    const interval = setInterval(fetchMetrics, 5000);
    fetchMetrics(); 

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-background text-foreground">
      {/* Header - Compact */}
      <header className="flex-none flex items-center justify-between px-6 py-3 border-b bg-card">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold tracking-tight">LUDEX Studio</h1>
          <span className="text-xs text-muted-foreground px-2 py-1 bg-muted rounded-full">Sprint 23</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs">
             <span className={`h-2 w-2 rounded-full ${wsRef.current?.readyState === 1 ? 'bg-green-500' : 'bg-red-500'}`}></span>
             {wsRef.current?.readyState === 1 ? 'Connected' : 'Disconnected'}
          </div>
          <SettingsModal onProviderChange={(provider, model) => {
            addLog('info', `Provider switched to ${provider} (${model})`);
          }} />
        </div>
      </header>

      {/* Main Content - 3 Column Grid */}
      <div className="flex-1 grid grid-cols-12 gap-4 p-4 overflow-hidden">
        
        {/* Column 1: Controls (Left - 25%) */}
        <div className="col-span-3 flex flex-col gap-4 overflow-y-auto pr-2">
          <div className="bg-card rounded-lg border p-4 shadow-sm">
            <h2 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wider">Input & Controls</h2>
            <InputForm onSubmit={handleStartGeneration} isGenerating={isGenerating} />
          </div>

          {/* Director Questions */}
          {directorQuestions.length > 0 && (
             <div className="bg-card rounded-lg border p-4 shadow-sm border-blue-500/50">
                <DirectorQuestions 
                  questions={directorQuestions} 
                  onAnswer={handleDirectorAnswer} 
                />
             </div>
          )}

          {/* Interactive Gate */}
          {currentGate && (
            <div className="bg-card rounded-lg border p-4 shadow-sm border-yellow-500/50">
              <InteractiveGate 
                gateName={currentGate}
                phaseData={gateData}
                onApprove={handleGateApprove}
                onReject={handleGateReject}
              />
            </div>
          )}

           {/* Metrics - Compact */}
           {metrics && (
             <div className="bg-card rounded-lg border p-4 shadow-sm">
                <h2 className="text-sm font-semibold mb-2 text-muted-foreground">Metrics</h2>
                <MetricsDashboard metrics={metrics} compact={true} />
             </div>
           )}
        </div>

        {/* Column 2: The Studio (Center - 25%) */}
        <div className="col-span-3 flex flex-col gap-4 overflow-hidden">
           <div className="flex-1 bg-card rounded-lg border shadow-sm flex flex-col overflow-hidden">
              <div className="p-3 border-b bg-muted/30">
                <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Agent Swarm</h2>
              </div>
              <div className="flex-1 overflow-y-auto p-0">
                 <AgentStatus agents={agents} compact={true} />
              </div>
           </div>
           
           <div className="h-1/3 bg-card rounded-lg border shadow-sm flex flex-col overflow-hidden">
              <div className="p-3 border-b bg-muted/30">
                 <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Live Activity</h2>
              </div>
              <div className="flex-1 overflow-y-auto p-0">
                 <AgentActivityStream lastMessage={lastActivityMessage} compact={true} />
              </div>
           </div>
        </div>

        {/* Column 3: Output (Right - 50%) */}
        <div className="col-span-6 flex flex-col overflow-hidden bg-card rounded-lg border shadow-sm">
           <Tabs defaultValue="gdd" className="flex-1 flex flex-col overflow-hidden">
              <div className="flex items-center justify-between px-4 py-2 border-b bg-muted/30">
                 <TabsList className="grid w-[200px] grid-cols-2">
                    <TabsTrigger value="gdd">GDD Preview</TabsTrigger>
                    <TabsTrigger value="logs">System Logs</TabsTrigger>
                 </TabsList>
              </div>
              
              <TabsContent value="gdd" className="flex-1 overflow-hidden p-0 m-0 data-[state=active]:flex flex-col">
                 <div className="flex-1 overflow-y-auto p-4">
                    <GDDViewer markdown={markdown} />
                 </div>
              </TabsContent>
              
              <TabsContent value="logs" className="flex-1 overflow-hidden p-0 m-0 data-[state=active]:flex flex-col">
                 <div className="flex-1 p-4 overflow-hidden">
                    <LogViewer logs={logs} />
                 </div>
              </TabsContent>
           </Tabs>
        </div>

      </div>
    </div>
  );
}
