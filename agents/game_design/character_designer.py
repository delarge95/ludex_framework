"""
Character Designer Agent for LUDEX Framework (Sprint 10)

Designs compelling protagonist, supporting cast, and antagonist characters
with clear motivations, flaws, and character arcs.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model  
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def character_designer_node(state: GameDesignState) -> GameDesignState:
    """
    Character Designer Agent Node.
    Role: Design protagonist, antagonist, and supporting cast.
    """
    logger.info("character_designer_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.85
        )
        
        concept = state.get("concept", "")
        genre = state.get("genre", "Unknown")
        narrative_structure = state.get("narrative_structure", {})
        
        system_msg = SystemMessage(content="""You are a **Character Designer** specialized in creating memorable game characters.

Output protagonist, antagonist, and 3 supporting characters with clear motivations and arcs.

Output JSON:
```json
{
  "protagonist": {
    "name": "Name",
    "archetype": "Hero / Antihero / Reluctant Hero",
    "motivation": "Core drive",
    "flaw": "Character weakness",
    "growth_arc": "How they change",
    "gameplay_expression": "How character reflected in mechanics"
  },
  "antagonist": {
    "name": "Name",
    "motivation": "Why they oppose protagonist",
    "philosophy": "Their worldview"
  },
  "supporting_cast": [
    {"name": "...", "role": "Mentor/Rival/Comic Relief", "purpose": "..."}
  ]
}
```""")
        
        human_msg = HumanMessage(content=f"""Design characters for:
**Concept**: {concept}
**Genre**: {genre}
**Narrative**: {narrative_structure}

Create compelling protagonist, antagonist, and supporting cast.""")
        
        result = await safe_agent_invoke(
            agent_name="CharacterDesigner",
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
            characters = json.loads(output)
        except json.JSONDecodeError:
            characters = {"raw_output": output}
        
        logger.info("character_designer_completed")
        
        return {
            **state,
            "characters": characters
        }
    
    except Exception as e:
        logger.exception("character_designer_error", error=str(e))
        return state
