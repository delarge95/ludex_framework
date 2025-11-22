"""
Character Artist Agent for LUDEX Framework (Sprint 11)

Designs character visual specifications including silhouettes, 
proportions, color schemes, and visual character sheets.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from core.agent_synergies import extract_art_character_style, extract_character_visual_specs, inject_synergy_context
from config.settings import settings

logger = structlog.get_logger(__name__)

async def character_artist_node(state: GameDesignState) -> GameDesignState:
    """
    Character Artist Agent Node.
    Role: Design character visual specifications.
    """
    logger.info("character_artist_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.8
        )
        
        characters = state.get("characters", {})
        art_direction = state.get("art_direction", {})
        
        # SYNERGY 1: Extract art style from ArtDirector
        art_style_guide = state.get("art_style_guide", {})
        art_style = extract_art_character_style(art_style_guide)
        
        # SYNERGY 2: Extract character descriptions from CharacterDesigner
        character_design = state.get("character_design", {})
        character_specs = extract_character_visual_specs(character_design)
        
        base_prompt = """You are a **Lead Character Artist** for games.

Design character visuals that are memorable, readable, and fit the art style.

Output JSON:
```json
{
  "protagonist_visual": {
    "name": "Character name",
    "silhouette": "Recognizable triangular shape with cape flowing right",
    "proportions": "Heroic (7-8 heads tall)",
    "color_scheme": {
      "primary": "#2C3E50",
      "secondary": "#E74C3C",
      "accent": "#F39C12"
    },
    "key_features": ["Glowing sword", "Asymmetric armor", "Flowing scarf"],
    "visual_references": ["Cloud Strife (FF7) for hair", "Link (Zelda) for tunic"]
  },
  "supporting_cast": [
    {
      "name": "Mentor character",
      "archetype": "Wise elder",
      "visual_notes": "Robed figure, staff, long beard",
      "color_contrast": "Muted earth tones vs protagonist's vibrant colors"
    }
  ],
  "design_principles": [
    "Silhouette test: Characters recognizable at distance",
    "Rule of three: Max 3 dominant colors per character",
    "Asymmetry for visual interest"
  ],
  "technical_specs": {
    "polygon_budget": "8k-10k tris per character",
    "texture_resolution": "2048x2048 for main characters",
    "LOD_levels": 3
  }
}
```"""
        
        # SYNERGY: Inject both art style and character specs into prompt
        enhanced_prompt = inject_synergy_context(base_prompt, art_style, "art_character")
        enhanced_prompt = inject_synergy_context(enhanced_prompt, {"characters": character_specs}, "character_art")
        system_msg = SystemMessage(content=enhanced_prompt)
        
        human_msg = HumanMessage(content=f"""Design character visuals for:
**Characters**: {characters}
**Art Style**: {art_direction.get('art_style', 'Unknown')}
**Color Palette**: {art_direction.get('color_palette', {})}

Create visual specs for protagonist and 2-3 supporting characters.""")
        
        result = await safe_agent_invoke(
            agent_name="CharacterArtist",
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
            character_visuals = json.loads(output)
        except json.JSONDecodeError:
            character_visuals = {"raw_output": output}
        
        logger.info("character_artist_completed")
        
        return {
            **state,
            "character_visuals": character_visuals
        }
    
    except Exception as e:
        logger.exception("character_artist_error", error=str(e))
        return state
