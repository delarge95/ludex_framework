"""
Art Director Agent for LUDEX Framework (Sprint 11)

Defines art style, visual pillars, color palettes, and reference mood boards
for the game's visual identity.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def art_director_node(state: GameDesignState) -> GameDesignState:
    """
    Art Director Agent Node.
    Role: Define visual style and art direction.
    """
    logger.info("art_director_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.85  # Higher for creative art direction
        )
        
        concept = state.get("concept", "")
        genre = state.get("genre", "Unknown")
        narrative = state.get("narrative_structure", {})
        
        system_msg = SystemMessage(content="""You are a **Lead Art Director** for video games.

Define cohesive visual identity that supports narrative and gameplay.

Output JSON:
```json
{
  "art_style": "Stylized realism / Pixel art / Cel-shaded / Low-poly / Photorealistic",
  "visual_pillars": [
    "Dark & Gothic",
    "Highly detailed environments",
    "Vibrant character designs"
  ],
  "color_palette": {
    "primary": ["#1A1A2E", "#16213E"],
    "secondary": ["#0F3460", "#533483"],
    "accent": ["#E94560", "#F4A261"],
    "palette_rationale": "Dark blues evoke mystery, warm accents draw attention to interactive elements"
  },
  "artistic_references": [
    "Hades (Supergiant Games) - Stylized character designs",
    "Hollow Knight (Team Cherry) - Atmospheric lighting",
    "Ori and the Blind Forest - Color grading"
  ],
  "mood_boards": {
    "environments": "Dark fantasy cities with neon accents",
    "characters": "Anime-inspired with realistic proportions",
    "ui": "Minimalist with glowing elements"
  },
  "technical_art_notes": {
    "shading_style": "Toon shading with rim lighting",
    "post_processing": "Bloom, Color grading, Vignette",
    "target_polygon_budget": "10k tris for characters, 50k for environments"
  }
}
```""")
        
        human_msg = HumanMessage(content=f"""Define art direction for:
**Concept**: {concept}
**Genre**: {genre}
**Narrative Tone**: {narrative.get('tone', 'Unknown')}

Create:
1. Art style selection
2. Visual pillars (3-4)
3. Color palette with hex codes
4. Artistic references
5. Technical art guidelines""")
        
        result = await safe_agent_invoke(
            agent_name="ArtDirector",
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
            art_direction = json.loads(output)
        except json.JSONDecodeError:
            art_direction = {"raw_output": output}
        
        logger.info(
            "art_director_completed",
            art_style=art_direction.get("art_style", "Unknown")
        )
        
        return {
            **state,
            "art_direction": art_direction
        }
    
    except Exception as e:
        logger.exception("art_director_error", error=str(e))
        return state
