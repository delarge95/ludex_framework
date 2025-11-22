"""
Audio Director Agent for LUDEX Framework (Sprint 13)

Designs comprehensive audio systems including music style, SFX catalog,
voice-over planning, and audio middleware recommendations.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings
from schemas.audio_design_schema import AudioDesignSchema
from tools.domain_knowledge_tool import DomainKnowledgeTool

logger = structlog.get_logger(__name__)

async def audio_director_node(state: GameDesignState) -> GameDesignState:
    """
    Audio Director Agent Node.
    Role: Design complete audio architecture and soundscape.
    """
    logger.info("audio_director_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.8
        )
        
        narrative = state.get("narrative_structure", {})
        art_direction = state.get("art_direction", {})
        
        system_msg = SystemMessage(content="""You are a **Lead Audio Director** for games.
Design immersive audio that enhances atmosphere, gameplay, and narrative.
You have access to a 'domain_knowledge_tool'. USE IT to research specific audio techniques, middleware capabilities (Wwise/FMOD), or genre-specific music patterns before making decisions.
Return a structured audio design plan.""")
        
        human_msg = HumanMessage(content=f"""Design audio system for:
**Narrative Tone**: {narrative.get('tone', 'Unknown')}
**Art Style**: {art_direction.get('art_style', 'Unknown')}

Create:
1. Music style and dynamic system
2. SFX catalog (UI, combat, environment)
3. Voice-over planning
4. Audio middleware recommendation
5. Technical specifications""")
        
        result = await safe_agent_invoke(
            agent_name="AudioDirector",
            llm=llm,
            messages=[system_msg, human_msg],
            state=state,
            tools=[DomainKnowledgeTool()], # RAG Tool Injected!
            output_schema=AudioDesignSchema # Pydantic integration
        )
        
        if result is None:
            return state
            
        # Result 'output' is now a Pydantic model
        audio_design_model = result.get("output")
        
        # Convert back to dict for state storage
        if hasattr(audio_design_model, "model_dump"):
            audio_design = audio_design_model.model_dump()
        else:
            audio_design = {"raw_output": str(audio_design_model)}
        
        logger.info("audio_director_completed")
        
        return {
            **state,
            "audio_design": audio_design
        }
    
    except Exception as e:
        logger.exception("audio_director_error", error=str(e))
        return state
