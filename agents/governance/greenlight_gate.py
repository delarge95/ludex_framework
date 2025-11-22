import structlog
from core.state_v2 import SpiralState
from agents.governance.decision_gate import generate_decision

logger = structlog.get_logger(__name__)

async def greenlight_gate_node(state: SpiralState):
    """
    Greenlight Gate: The critical "Go/No-Go" decision point.
    Evaluates the Concept Phase output (Market Analysis + Mechanics) and asks the user to proceed.
    """
    logger.info("greenlight_gate_started")
    
    # Check if we are resuming from a decision
    pending = state.get("pending_decision")
    if pending and pending.get("id") == "greenlight_gate" and pending.get("selected_option_id"):
        logger.info(f"greenlight_gate_resumed: {pending['selected_option_id']}")
        return {"awaiting_input": False}

    # Extract context for the LLM
    core = state.get("core", {})
    working = state.get("working", {})
    
    concept = core.get("concept", "Unknown Concept")
    genre = core.get("genre", "Unknown Genre")
    market_report = core.get("market_analysis", {})
    mechanics = working.get("mechanics", [])
    
    context = f"""
    **Concept**: {concept}
    **Genre**: {genre}
    
    **Market Analysis**:
    - Target Audience: {market_report.get('target_audience', 'N/A')}
    - Market Gap: {market_report.get('market_gap', 'N/A')}
    
    **Core Mechanics**:
    {', '.join([m['name'] for m in mechanics])}
    """
    
    # Generate the decision options
    decision = await generate_decision(
        state,
        context_data=context,
        decision_title="Project Greenlight",
        decision_description="The Concept Phase is complete. How should we proceed to Production?",
        gate_id="greenlight_gate"
    )
    
    # Update state with the pending decision and pause flag
    return {
        "pending_decision": decision,
        "awaiting_input": True
    }
