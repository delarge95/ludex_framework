"""
Environment Artist Agent for LUDEX Framework (Sprint 12)

Designs environment art including biomes, modular kits, prop catalogs,
and environmental storytelling guidelines.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def environment_artist_node(state: GameDesignState) -> GameDesignState:
    """
    Environment Artist Agent Node.
    Role: Design environment art and biomes.
    """
    logger.info("environment_artist_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.8
        )
        
        world_lore = state.get("world_lore", {})
        art_direction = state.get("art_direction", {})
        
        system_msg = SystemMessage(content="""You are a **Lead Environment Artist** for games.

Design cohesive, immersive environments that support gameplay and narrative.

Output JSON:
```json
{
  "biomes": [
    {
      "name": "Dark Forest",
      "mood": "Mysterious, foreboding",
      "color_palette": ["#1A2B1A", "#2C4A2C", "#4A7C59"],
      "key_features": ["Ancient trees", "Glowing mushrooms", "Fog effects"],
      "gameplay_purpose": "Stealth encounters, resource gathering"
    }
  ],
  "modular_kits": {
    "architecture": ["Medieval castle pieces", "Wooden village assets"],
    "natural": ["Rock formations", "Tree variations", "Vegetation"],
    "props": ["Crates", "Barrels", "Torches", "Furniture"]
  },
  "environmental_storytelling": {
    "techniques": [
      "Abandoned settlements hint at past conflict",
      "Graffiti shows faction territories",
      "Light sources guide player progression"
    ]
  },
  "technical_specs": {
    "polygon_budget_per_asset": "500-5000 tris",
    "texture_resolution": "1024x1024 for props, 2048x2048 for structures",
    "draw_call_budget": "Max 100 draw calls per scene",
    "LOD_strategy": "3 LOD levels for all outdoor assets"
  },
  "atmospheric_elements": {
    "lighting": "Dynamic day/night cycle with warm sunset tones",
    "weather": "Rain, fog, snow based on biome",
    "particles": "Dust motes, fireflies, embers"
  }
}
```""")
        
        human_msg = HumanMessage(content=f"""Design environment art for:
**World Lore**: {world_lore}
**Art Style**: {art_direction.get('art_style', 'Unknown')}

Create:
1. Biome designs (2-3 major biomes)
2. Modular asset kits
3. Environmental storytelling techniques
4. Technical specifications
5. Atmospheric elements""")
        
        result = await safe_agent_invoke(
            agent_name="EnvironmentArtist",
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
            environment_design = json.loads(output)
        except json.JSONDecodeError:
            environment_design = {"raw_output": output}
        
        logger.info("environment_artist_completed")
        
        return {
            **state,
            "environment_design": environment_design
        }
    
    except Exception as e:
        logger.exception("environment_artist_error", error=str(e))
        return state
