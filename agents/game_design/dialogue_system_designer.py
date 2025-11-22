"""
Dialogue System Designer Agent for LUDEX Framework (Sprint 10)

Designs conversation architecture, dialogue trees, and localization planning.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def dialogue_system_designer_node(state: GameDesignState) -> GameDesignState:
    """
    Dialogue System Designer Agent Node.
    Role: Design dialogue architecture and conversation systems.
    """
    logger.info("dialogue_system_designer_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.7
        )
        
        concept = state.get("concept", "")
        genre = state.get("genre", "Unknown")
        characters = state.get("characters", {})
        
        system_msg = SystemMessage(content="""You are a **Dialogue System Designer** specialized in conversation mechanics.

Output JSON:
```json
{
  "dialogue_system_type": "Linear / Branching / Hub-Based / Full Branching",
  "conversation_ui": "Speech bubbles / Visual Novel / Wheel (Mass Effect) / List",
  "player_agency": "High / Medium / Low",
  "tone_system": {
    "enabled": true/false,
    "tones": ["Aggressive", "Diplomatic", "Sarcastic"]
  },
  "choice_consequences": "Immediate / Long-term / Both",
  "voice_over": {
    "required": true/false,
    "estimated_lines": 1000,
    "character_voices": ["Protagonist: Young male", "..."]
  },
  "localization": {
    "target_languages": ["English", "Spanish", "..."],
    "text_expansion_factor": 1.3,
    "special_considerations": ["...]
  },
  "key_conversations": [
    {"with": "Character X", "purpose": "Reveal backstory", "branching": "Yes/No"}
  ]
}
```""")
        
        human_msg = HumanMessage(content=f"""Design dialogue system for:
**Concept**: {concept}
**Genre**: {genre}
**Characters**: {characters}""")
        
        result = await safe_agent_invoke(
            agent_name="DialogueSystemDesigner",
            llm=llm,
            messages=[system_msg, human_msg],
            state=state,
            tools=[]
        )
        
        if result is None:
            return state
        
        output = result.get("content", "{}")
        if "```json" in output:
            output = output.split("```json")[1].split("```")[0].strip()
        
        import json
        try:
            dialogue_system = json.loads(output)
        except json.JSONDecodeError:
            dialogue_system = {"raw_output": output}
        
        logger.info(
            "dialogue_system_designer_completed",
            system_type=dialogue_system.get("dialogue_system_type", "Unknown")
        )
        
        return {
            **state,
            "dialogue_system": dialogue_system
        }
    
    except Exception as e:
        logger.exception("dialogue_system_designer_error", error=str(e))
        return state
