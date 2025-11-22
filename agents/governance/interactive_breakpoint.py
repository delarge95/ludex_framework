from typing import Dict, Any
from core.state_v2 import SpiralState
import structlog

logger = structlog.get_logger(__name__)

def create_progress_summary(state: SpiralState) -> Dict[str, Any]:
    """
    Creates a "Daily Standup" style summary of current progress.
    This is an Interactive Breakpoint that gives the user visibility.
    """
    summary = {
        "current_phase": state.get("current_phase", "unknown"),
        "iteration": state.get("iteration_count", 0),
        "completed_agents": [],
        "pending_decisions": state.get("pending_decision"),
        "awaiting_input": state.get("awaiting_input", False),
        "key_artifacts": {}
    }
    
    # Extract completed work from reasoning_log
    reasoning_log = state.get("reasoning_log", [])
    for entry in reasoning_log:
        agent_name = entry.get("agent_name")
        if agent_name and agent_name not in summary["completed_agents"]:
            summary["completed_agents"].append(agent_name)
    
    # Extract key artifacts from working state
    working = state.get("working", {})
    if working.get("mechanics"):
        summary["key_artifacts"]["mechanics"] = len(working["mechanics"])
    if working.get("narrative_structure"):
        summary["key_artifacts"]["narrative"] = "defined"
    if working.get("art_style_guide"):
        summary["key_artifacts"]["art_style"] = "defined"
    
    return summary

def interactive_breakpoint_node(state: SpiralState) -> SpiralState:
    """
    Graph node that creates a progress summary for the user.
    This acts as an "Interactive Breakpoint" - a pause point where
    the user can see what's been accomplished.
    """
    logger.info("interactive_breakpoint_triggered")
    
    summary = create_progress_summary(state)
    
    logger.info("progress_summary_created", 
                phase=summary["current_phase"],
                completed_agents=len(summary["completed_agents"]))
    
    # Store summary in state for frontend to display
    return {
        **state,
        "progress_summary": summary,
        "last_checkpoint": "interactive_breakpoint"
    }
