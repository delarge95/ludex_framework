"""
Metrics API endpoints for LUDEX framework.
"""
from fastapi import APIRouter
from core.metrics import metrics_collector

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("")
async def get_metrics():
    """Get current metrics summary."""
    summary = metrics_collector.get_summary()
    return summary

@router.post("/reset")
async def reset_metrics():
    """Reset metrics collector (for testing)."""
    metrics_collector.metrics = []
    return {"status": "reset"}
