"use client";

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Clock, Zap, TrendingUp } from "lucide-react";

interface MetricsData {
  total_executions: number;
  completed: number;
  failed: number;
  total_latency_ms: number;
  avg_latency_ms: number;
  total_tokens: number;
  avg_tokens_per_agent: number;
}

interface MetricsDashboardProps {
  metrics: MetricsData | null;
}

export function MetricsDashboard({ metrics }: MetricsDashboardProps) {
  if (!metrics || metrics.total_executions === 0) return null;

  // Provide safe defaults for all metrics
  const safeMetrics = {
    total_executions: metrics.total_executions || 0,
    completed: metrics.completed || 0,
    failed: metrics.failed || 0,
    total_latency_ms: metrics.total_latency_ms || 0,
    avg_latency_ms: metrics.avg_latency_ms || 0,
    total_tokens: metrics.total_tokens || 0,
    avg_tokens_per_agent: metrics.avg_tokens_per_agent || 0
  };

  const stats = [
    {
      title: "Total Executions",
      value: safeMetrics.total_executions,
      icon: Activity,
      color: "text-blue-600"
    },
    {
      title: "Avg Latency",
      value: `${safeMetrics.avg_latency_ms.toFixed(0)}ms`,
      icon: Clock,
      color: "text-green-600"
    },
    {
      title: "Total Tokens",
      value: safeMetrics.total_tokens.toLocaleString(),
      icon: Zap,
      color: "text-amber-600"
    },
    {
      title: "Success Rate",
      value: safeMetrics.total_executions > 0 
        ? `${((safeMetrics.completed / safeMetrics.total_executions) * 100).toFixed(1)}%`
        : "0%",
      icon: TrendingUp,
      color: "text-emerald-600"
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Metrics</CardTitle>
        <CardDescription>Live telemetry from LUDEX framework</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div 
                key={stat.title}
                className="flex items-start gap-3 p-3 rounded-lg border bg-card"
              >
                <Icon className={`h-5 w-5 ${stat.color} mt-1`} />
                <div>
                  <p className="text-sm text-muted-foreground">{stat.title}</p>
                  <p className="text-2xl font-bold">{stat.value}</p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-4 pt-4 border-t">
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-muted-foreground">Completed:</span>
              <span className="ml-2 font-semibold text-green-600">{safeMetrics.completed}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Failed:</span>
              <span className="ml-2 font-semibold text-red-600">{safeMetrics.failed}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Avg Tokens/Agent:</span>
              <span className="ml-2 font-semibold">{safeMetrics.avg_tokens_per_agent.toFixed(0)}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Total Latency:</span>
              <span className="ml-2 font-semibold">{(safeMetrics.total_latency_ms / 1000).toFixed(1)}s</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
