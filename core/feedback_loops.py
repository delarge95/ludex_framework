"""
Feedback Loop System for Agent Collaboration

Manages iterative refinement cycles between agents to achieve convergence
on design decisions.
"""

from typing import Dict, Any, List, Optional, Tuple
import structlog
from core.state_v2 import SpiralState

logger = structlog.get_logger(__name__)

MAX_ITERATIONS = 3  # Prevent infinite loops

class FeedbackLoopOrchestrator:
    """
    Orchestrates feedback loops between agents.
    Tracks iteration count and detects convergence.
    """
    
    def __init__(self):
        self.loop_history: Dict[str, List[Dict[str, Any]]] = {}
    
    def should_iterate(
        self,
        loop_id: str,
        current_state: SpiralState,
        convergence_threshold: float = 0.8
    ) -> Tuple[bool, str]:
        """
        Determine if a feedback loop should continue iterating.
        
        Args:
            loop_id: Unique identifier for the loop (e.g., "mechanics_feasibility")
            current_state: Current state of the workflow
            convergence_threshold: Similarity threshold for convergence (0.0-1.0)
            
        Returns:
            Tuple of (should_continue, reason)
        """
        # Initialize loop history if needed
        if loop_id not in self.loop_history:
            self.loop_history[loop_id] = []
        
        history = self.loop_history[loop_id]
        iteration_count = len(history)
        
        # Check iteration limit
        if iteration_count >= MAX_ITERATIONS:
            logger.warning("feedback_loop_max_iterations", loop_id=loop_id, count=iteration_count)
            return False, f"Max iterations ({MAX_ITERATIONS}) reached"
        
        # First iteration always runs
        if iteration_count == 0:
            return True, "Initial iteration"
        
        # Check for convergence (simplified - compare last two iterations)
        if iteration_count >= 2:
            last_output = history[-1].get("output", {})
            prev_output = history[-2].get("output", {})
            
            # Simple convergence check: if outputs are identical, we've converged
            if last_output == prev_output:
                logger.info("feedback_loop_converged", loop_id=loop_id, iterations=iteration_count)
                return False, "Converged (outputs identical)"
        
        return True, f"Iteration {iteration_count + 1}/{MAX_ITERATIONS}"
    
    def record_iteration(
        self,
        loop_id: str,
        agent_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any]
    ):
        """
        Record an iteration of a feedback loop.
        
        Args:
            loop_id: Loop identifier
            agent_name: Name of the agent that executed
            input_data: Input to the agent
            output_data: Output from the agent
        """
        if loop_id not in self.loop_history:
            self.loop_history[loop_id] = []
        
        self.loop_history[loop_id].append({
            "agent": agent_name,
            "input": input_data,
            "output": output_data,
            "iteration": len(self.loop_history[loop_id]) + 1
        })
        
        logger.info("feedback_loop_iteration_recorded",
                   loop_id=loop_id,
                   agent=agent_name,
                   iteration=len(self.loop_history[loop_id]))
    
    def get_loop_summary(self, loop_id: str) -> Dict[str, Any]:
        """
        Get a summary of a feedback loop's history.
        
        Args:
            loop_id: Loop identifier
            
        Returns:
            Summary dict with iteration count, convergence status, etc.
        """
        if loop_id not in self.loop_history:
            return {"status": "not_started", "iterations": 0}
        
        history = self.loop_history[loop_id]
        
        return {
            "status": "completed" if len(history) >= MAX_ITERATIONS else "in_progress",
            "iterations": len(history),
            "agents_involved": list(set(h["agent"] for h in history)),
            "converged": len(history) >= 2 and history[-1]["output"] == history[-2]["output"]
        }


# ============================================================================
# SPECIFIC FEEDBACK LOOP IMPLEMENTATIONS
# ============================================================================

async def mechanics_feasibility_loop(
    state: SpiralState,
    orchestrator: FeedbackLoopOrchestrator
) -> SpiralState:
    """
    Feedback loop: MechanicsDesigner ⇄ TechnicalFeasibilityValidator
    
    Iteratively refine mechanics until they are technically feasible.
    """
    loop_id = "mechanics_feasibility"
    
    should_continue, reason = orchestrator.should_iterate(loop_id, state)
    
    if not should_continue:
        logger.info("mechanics_feasibility_loop_complete", reason=reason)
        return state
    
    # Get current mechanics
    mechanics = state.get("working", {}).get("mechanics", [])
    
    # Validate feasibility (simplified - in real implementation, call TechnicalFeasibilityValidator)
    feasibility_issues = []
    for mechanic in mechanics:
        complexity = mechanic.get("complexity", "medium")
        if complexity == "very_high":
            feasibility_issues.append(f"{mechanic.get('name')}: Too complex to implement")
    
    # Record iteration
    orchestrator.record_iteration(
        loop_id=loop_id,
        agent_name="TechnicalFeasibilityValidator",
        input_data={"mechanics": mechanics},
        output_data={"issues": feasibility_issues}
    )
    
    # If issues found, mark for refinement
    if feasibility_issues:
        logger.warning("mechanics_feasibility_issues", issues=feasibility_issues)
        return {
            **state,
            "feedback_required": True,
            "feedback_target": "MechanicsDesigner",
            "feedback_message": f"Feasibility issues: {', '.join(feasibility_issues)}"
        }
    
    return state


async def ludonarrative_harmony_loop(
    state: SpiralState,
    orchestrator: FeedbackLoopOrchestrator
) -> SpiralState:
    """
    Feedback loop: NarrativeArchitect ⇄ MechanicsDesigner ⇄ LudonarrativeHarmonizer
    
    Ensure story and gameplay are harmonious.
    """
    loop_id = "ludonarrative_harmony"
    
    should_continue, reason = orchestrator.should_iterate(loop_id, state)
    
    if not should_continue:
        logger.info("ludonarrative_harmony_loop_complete", reason=reason)
        return state
    
    # Get narrative and mechanics
    narrative = state.get("working", {}).get("narrative_structure", {})
    mechanics = state.get("working", {}).get("mechanics", [])
    
    # Check harmony (simplified)
    harmony_score = 0.8  # Placeholder - real implementation would analyze alignment
    
    orchestrator.record_iteration(
        loop_id=loop_id,
        agent_name="LudonarrativeHarmonizer",
        input_data={"narrative": narrative, "mechanics": mechanics},
        output_data={"harmony_score": harmony_score}
    )
    
    if harmony_score < 0.7:
        logger.warning("ludonarrative_dissonance", score=harmony_score)
        return {
            **state,
            "feedback_required": True,
            "feedback_target": "MechanicsDesigner",
            "feedback_message": "Mechanics don't align with narrative themes"
        }
    
    return state


async def art_performance_balance_loop(
    state: SpiralState,
    orchestrator: FeedbackLoopOrchestrator
) -> SpiralState:
    """
    Feedback loop: ArtDirector ⇄ PerformanceAnalyst
    
    Balance visual fidelity with performance targets.
    """
    loop_id = "art_performance_balance"
    
    should_continue, reason = orchestrator.should_iterate(loop_id, state)
    
    if not should_continue:
        logger.info("art_performance_balance_loop_complete", reason=reason)
        return state
    
    # Get art style and performance targets
    art_style = state.get("working", {}).get("art_style_guide", {})
    performance_spec = state.get("working", {}).get("performance_spec", {})
    
    # Check if targets are achievable (simplified)
    target_fps = performance_spec.get("target_fps", 60)
    visual_fidelity = art_style.get("visual_fidelity", "medium")
    
    achievable = True
    if visual_fidelity == "high" and target_fps >= 60:
        achievable = False  # High fidelity + 60 FPS may be unrealistic
    
    orchestrator.record_iteration(
        loop_id=loop_id,
        agent_name="PerformanceAnalyst",
        input_data={"art_style": art_style, "performance_spec": performance_spec},
        output_data={"achievable": achievable}
    )
    
    if not achievable:
        logger.warning("art_performance_conflict")
        return {
            **state,
            "feedback_required": True,
            "feedback_target": "ArtDirector",
            "feedback_message": "Visual fidelity too high for performance targets"
        }
    
    return state


# ============================================================================
# LOOP REGISTRY
# ============================================================================

FEEDBACK_LOOPS = {
    "mechanics_feasibility": mechanics_feasibility_loop,
    "ludonarrative_harmony": ludonarrative_harmony_loop,
    "art_performance_balance": art_performance_balance_loop,
}
