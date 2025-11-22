import structlog
from core.state_v2 import SpiralState
from agents.governance.decision_gate import generate_decision

logger = structlog.get_logger(__name__)

async def visual_review_gate_node(state: SpiralState):
    """
    Visual Review Gate: The Art Direction checkpoint.
    Evaluates the Art Style and Character Designs before expensive asset production.
    """
    logger.info("visual_review_gate_started")
    
    # Check if we are resuming from a decision
    pending = state.get("pending_decision")
    if pending and pending.get("id") == "visual_review_gate" and pending.get("selected_option_id"):
        logger.info(f"visual_review_gate_resumed: {pending['selected_option_id']}")
        return {"awaiting_input": False}

    # Extract context
    core = state.get("core", {})
    working = state.get("working", {})
    
    art_pillars = core.get("art_direction_pillars", [])
    art_style = working.get("art_style_guide", {})
    character_visuals = working.get("character_visuals", {})
    
    context = f"""
    **Art Pillars**: {', '.join(art_pillars)}
    
    **Proposed Art Style**:
    {art_style}
    
    **Character Visuals**:
    {len(character_visuals)} characters designed.
    """
    
    # Generate the decision options
    decision = await generate_decision(
        state,
        context_data=context,
        decision_title="Visual Identity Review",
        decision_description="The Art Direction is defined. Does this match the vision?",
        gate_id="visual_review_gate"
    )
    
    return {
        "pending_decision": decision,
        "awaiting_input": True
    }
