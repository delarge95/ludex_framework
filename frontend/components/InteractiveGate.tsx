"use client";

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, XCircle, Clock } from "lucide-react";

interface InteractiveGateProps {
  gateName: string;
  phaseData?: any;
  onApprove: () => void;
  onReject: () => void;
}

export function InteractiveGate({ gateName, phaseData, onApprove, onReject }: InteractiveGateProps) {
  if (!gateName) return null;

  const gateInfo: Record<string, { title: string; desc: string }> = {
    'mechanics_designer': {
      title: 'Market Analysis Approval',
      desc: 'Review the market analysis before proceeding to mechanics design'
    },
    'producer': {
      title: 'System Design Approval',
      desc: 'Review the technical architecture before moving to production planning'
    }
  };

  const currentGate = gateInfo[gateName] || { 
    title: 'Approval Required', 
    desc: 'Review this phase before proceeding' 
  };

  return (
    <Card className="border-blue-500/50 bg-blue-50/50 dark:bg-blue-950/20">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-blue-600 animate-pulse" />
          <CardTitle>{currentGate.title}</CardTitle>
        </div>
        <CardDescription>{currentGate.desc}</CardDescription>
      </CardHeader>
      <CardContent>
        {phaseData && (
          <div className="mb-4 p-3 bg-white dark:bg-gray-800 rounded-md border">
            <pre className="text-xs overflow-auto max-h-[200px]">
              {JSON.stringify(phaseData, null, 2)}
            </pre>
          </div>
        )}
        
        <div className="flex gap-2">
          <Button 
            onClick={onApprove} 
            className="flex-1 bg-green-600 hover:bg-green-700"
          >
            <CheckCircle2 className="mr-2 h-4 w-4" />
            Approve & Continue
          </Button>
          <Button 
            onClick={onReject} 
            variant="destructive"
            className="flex-1"
          >
            <XCircle className="mr-2 h-4 w-4" />
            Reject & Restart
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
