"""
Metrics tracking module for LUDEX framework.
Tracks token usage, latency, and other operational metrics.
"""
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class AgentMetrics:
    """Metrics for a single agent execution."""
    agent_name: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    tokens_used: int = 0
    latency_ms: Optional[float] = None
    status: str = "running"  # running, completed, failed
    error: Optional[str] = None
    
    def complete(self, tokens: int = 0):
        """Mark the agent execution as complete."""
        self.end_time = time.time()
        self.latency_ms = (self.end_time - self.start_time) * 1000
        self.tokens_used = tokens
        self.status = "completed"
        
        logger.info(
            "agent_execution_completed",
            agent=self.agent_name,
            latency_ms=self.latency_ms,
            tokens=self.tokens_used,
            status=self.status
        )
    
    def fail(self, error: str):
        """Mark the agent execution as failed."""
        self.end_time = time.time()
        self.latency_ms = (self.end_time - self.start_time) * 1000
        self.status = "failed"
        self.error = error
        
        logger.error(
            "agent_execution_failed",
            agent=self.agent_name,
            latency_ms=self.latency_ms,
            error=error
        )

class MetricsCollector:
    """Singleton metrics collector for the framework."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.metrics = []
        return cls._instance
    
    def start_agent(self, agent_name: str) -> AgentMetrics:
        """Start tracking an agent execution."""
        metric = AgentMetrics(agent_name=agent_name)
        self.metrics.append(metric)
        logger.info("agent_execution_started", agent=agent_name)
        return metric
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all tracked executions."""
        if not self.metrics:
            return {"total_executions": 0}
        
        completed = [m for m in self.metrics if m.status == "completed"]
        failed = [m for m in self.metrics if m.status == "failed"]
        
        total_latency = sum(m.latency_ms for m in completed if m.latency_ms)
        total_tokens = sum(m.tokens_used for m in completed)
        
        return {
            "total_executions": len(self.metrics),
            "completed": len(completed),
            "failed": len(failed),
            "total_latency_ms": total_latency,
            "avg_latency_ms": total_latency / len(completed) if completed else 0,
            "total_tokens": total_tokens,
            "avg_tokens_per_agent": total_tokens / len(completed) if completed else 0
        }

# Singleton instance
metrics_collector = MetricsCollector()
