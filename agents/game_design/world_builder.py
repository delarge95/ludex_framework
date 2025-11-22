"""
World Builder Agent for LUDEX Framework (Sprint 10)

Creates lore, factions, geography, and environmental storytelling guidelines.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def world_builder_node(state: GameDesignState) -> GameDesignState:
    """
    World Builder Agent Node.
    Role: Design game world, lore, factions, geography.
    """
    logger.info("world_builder_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.9  # High creativity for world-building
        )
        
        concept = state.get("concept", "")
        genre = state.get("genre", "Unknown")
        narrative = state.get("narrative_structure", {})
        
        system_msg = SystemMessage(content="""You are a **World Builder** who creates immersive game worlds.

Output JSON:
```json
{
  "world_name": "...",
  "setting": "Fantasy / Sci-Fi / Modern / Post-Apocalyptic",
  "geography": {
    "biomes": ["Forest", "Desert", "City"],
    "key_locations": [{"name": "...", "significance": "..."}]
  },
  "factions": [
    {"name": "...", "ideology": "...", "relationship_to_player": "Ally/Enemy/Neutral"}
  ],
  "lore": {
    "creation_myth": "...",
    "major_historical_events": ["..."],
    "current_conflict": "..."
  },
  "environmental_storytelling": ["Idea 1", "Idea 2"]
}
```""")
        
        human_msg = HumanMessage(content=f"""Build a world for:
**Concept**: {concept}
**Genre**: {genre}
**Narrative**: {narrative}""")
        
        result = await safe_agent_invoke(
            agent_name="WorldBuilder",
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
            world_lore = json.loads(output)
        except json.JSONDecodeError:
            world_lore = {"raw_output": output}
        
        logger.info("world_builder_completed", world_name=world_lore.get("world_name", "Unknown"))
        
        return {
            **state,
            "world_lore": world_lore
        }
    
    except Exception as e:
        logger.exception("world_builder_error", error=str(e))
        return state
