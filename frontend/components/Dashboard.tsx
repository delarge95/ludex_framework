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

export function Dashboard() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [markdown, setMarkdown] = useState<string>("");
  const [agents, setAgents] = useState<Agent[]>([
    { id: '1', name: 'Market Analyst', role: 'Validating Concept', status: 'idle' },
    { id: '2', name: 'Mechanics Designer', role: 'Designing Systems', status: 'idle' },
    { id: '3', name: 'System Designer', role: 'Checking Tech Feasibility', status: 'idle' },
    { id: '4', name: 'Producer', role: 'Estimating Scope', status: 'idle' },
    { id: '5', name: 'GDD Writer', role: 'Compiling Document', status: 'idle' },
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

  // WebSocket ref
  const wsRef = React.useRef<WebSocket | null>(null);

  const handleDirectorAnswer = async (answer: string) => {
    // Send answer back to backend
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: 'director_answer',
        answer: answer
      }));
      setDirectorQuestions([]);
    }
  };

  const handleGateApprove = async () => {
    if (wsRef.current && currentGate) {
      wsRef.current.send(JSON.stringify({
        type: 'gate_approve',
        gate: currentGate
      }));
      setCurrentGate(null);
      setGateData(null);
    }
  };

  const handleGateReject = async () => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: 'gate_reject'
      }));
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
    
    // Reset agents
    setAgents(prev => prev.map(a => ({ ...a, status: 'idle', message: undefined })));

    try {
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
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data) as WebSocketMessage;
        console.log('WS Message:', data);

        if (data.type === 'director_questions') {
          // Director is asking for clarification
          setDirectorQuestions(data.questions as string[]);
        } else if (data.type === 'gate_reached') {
          // Interactive gate reached
          setCurrentGate(data.gate_name as string);
          setGateData(data.data);
        } else if (data.type === 'metrics_update') {
          // Metrics update
          setMetrics(data.metrics);
        } else if (data.type === 'tool_call_started' || data.type === 'tool_call_completed') {
          // Update activity stream
          setLastActivityMessage(data);
        } else if (data.type === 'agent_update') {
          setAgents(prev => prev.map(a => {
            // Map backend agent names to frontend IDs/Names if needed
            const agentNameMap: Record<string, string> = {
              'market_analyst': 'Market Analyst',
              'mechanics_designer': 'Mechanics Designer',
              'system_designer': 'System Designer',
              'producer': 'Producer',
              'gdd_writer': 'GDD Writer'
            };
            
            const agentKey = data.agent as string;
            if (agentKey && agentNameMap[agentKey] === a.name) {
              return { ...a, status: data.status === 'done' ? 'done' : 'working' };
            }
            return a;
          }));
        } else if (data.type === 'gdd_update') {
          setMarkdown(data.markdown as string);
        } else if (data.type === 'status') {
          if (data.status === 'completed') {
            setIsGenerating(false);
            ws.close();
          }
        } else if (data.type === 'error') {
          console.error('Backend Error:', data.message);
          setIsGenerating(false);
          ws.close();
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket Error:', error);
        setIsGenerating(false);
      };

    } catch (error) {
      console.error('Error starting generation:', error);
      setIsGenerating(false);
    }
  };

  // Removed simulateGeneration

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
        // Silently fail - metrics not critical
      }
    };

    const interval = setInterval(fetchMetrics, 5000); // Every 5 seconds
    fetchMetrics(); // Initial fetch

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container mx-auto p-6 max-w-7xl space-y-6">
      <header className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold tracking-tight">LUDEX Studio</h1>
          <p className="text-muted-foreground">AI-Powered Game Design Automation</p>
          <div className="flex items-center gap-4 mt-1">
            <p className="text-xs text-red-500">
              WS Status: {wsRef.current ? (wsRef.current.readyState === 1 ? 'Connected' : 'Connecting...') : 'Disconnected'}
            </p>
            <SettingsModal onProviderChange={(provider, model) => {
              console.log(`Switched to ${provider} (${model})`);
              // Optional: Show a toast notification here
            }} />
          </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <InputForm onSubmit={handleStartGeneration} isGenerating={isGenerating} />
          
          {/* Director Questions */}
          <DirectorQuestions 
            questions={directorQuestions} 
            onAnswer={handleDirectorAnswer} 
          />

          {/* Interactive Gate */}
          {currentGate && (
            <InteractiveGate 
              gateName={currentGate}
              phaseData={gateData}
              onApprove={handleGateApprove}
              onReject={handleGateReject}
            />
          )}

          <AgentStatus agents={agents} />
          
          {/* Activity Stream - New Component */}
          <AgentActivityStream lastMessage={lastActivityMessage} />
          
          {/* Metrics Dashboard */}
          <MetricsDashboard metrics={metrics} />
        </div>
        
        <div className="lg:col-span-2">
          <GDDViewer markdown={markdown} />
        </div>
      </div>
    </div>
  );
}

