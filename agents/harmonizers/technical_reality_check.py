import structlog
from langchain_core.messages import SystemMessage
from core.state_v2 import SpiralState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke

logger = structlog.get_logger(__name__)

async def technical_reality_check_node(state: SpiralState):
    """
    Harmonizer Node: Checks consistency between Art/Physics and Performance.
    """
    logger.info("technical_reality_check_started")
    
    core = state.get("core", {})
    working = state.get("working", {})
    
    target_platform = core.get("target_platform", ["PC"])
    art_style = working.get("art_style_guide", {})
    physics = working.get("physics_spec", {})
    
    try:
        llm = create_model(provider=state.get("llm_provider", "github"), model_type="fast")
        
        prompt = f"""
        You are a Technical Director.
        
        **Target Platform**: {target_platform}
        
        **Art Style**: {art_style}
        **Physics Spec**: {physics}
        
        Assess if the proposed Art and Physics are realistic for the Target Platform.
        Flag any performance risks (e.g., "Ray Tracing on Mobile").
        
        Return a JSON object:
        {{
            "risk_level": "Low" | "Medium" | "High" | "Critical",
            "issues": ["string issue 1"],
            "optimization_suggestions": ["string suggestion 1"]
        }}
        """
        
        result = await safe_agent_invoke(llm, [SystemMessage(content=prompt)], "technical_reality_check")
        
        return {
            "working": {
                "validation_warnings": [
                    {
                        "source": "TechnicalRealityCheck", 
                        "message": f"Risk Level: {result.get('risk_level', 'Unknown')}. Issues: {result.get('issues', [])}"
                    }
                ]
            }
        }
        
    except Exception as e:
        logger.error("technical_reality_check_failed", error=str(e))
        return {}
