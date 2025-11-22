import structlog
from langchain_core.messages import SystemMessage, HumanMessage
from core.state_v2 import SpiralState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke

logger = structlog.get_logger(__name__)

async def ludonarrative_harmonizer_node(state: SpiralState):
    """
    Harmonizer Node: Checks consistency between Mechanics and Narrative.
    """
    logger.info("ludonarrative_harmonizer_started")
    
    core = state.get("core", {})
    working = state.get("working", {})
    
    narrative_theme = core.get("narrative_theme", "Unknown")
    mechanics = working.get("mechanics", [])
    
    if not mechanics:
        return {"working": {"validation_warnings": [{"source": "LudonarrativeHarmonizer", "message": "No mechanics to validate."}]}}

    try:
        llm = create_model(provider=state.get("llm_provider", "github"), model_type="fast")
        
        mechanics_str = "\n".join([f"- {m['name']}: {m['description']}" for m in mechanics])
        
        prompt = f"""
        You are a Ludonarrative Dissonance Detector.
        
        **Narrative Theme**: {narrative_theme}
        
        **Proposed Mechanics**:
        {mechanics_str}
        
        Analyze if these mechanics support or contradict the narrative theme.
        If there is dissonance (e.g., "Pacifist theme" but "Violent shooting mechanics"), flag it.
        
        Return a JSON object:
        {{
            "dissonance_found": boolean,
            "score": int (0-100, 100 is perfect harmony),
            "analysis": "string explanation",
            "suggestions": ["string suggestion 1", "string suggestion 2"]
        }}
        """
        
        result = await safe_agent_invoke(llm, [SystemMessage(content=prompt)], "ludonarrative_harmonizer")
        
        # In a real implementation, we would parse the JSON and update the state.
        # For now, we log the analysis to the reasoning log.
        
        return {
            "working": {
                "validation_warnings": [
                    {
                        "source": "LudonarrativeHarmonizer", 
                        "message": f"Harmony Score: {result.get('score', 'N/A')}. {result.get('analysis', '')}"
                    }
                ]
            }
        }
        
    except Exception as e:
        logger.error("ludonarrative_harmonizer_failed", error=str(e))
        return {}
