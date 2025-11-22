"""
UI/UX Designer Agent for LUDEX Framework (Sprint 11)

Designs user interface architecture, HUD layouts, menu systems, 
onboarding flows, and accessibility features.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def ui_ux_designer_node(state: GameDesignState) -> GameDesignState:
    """
    UI/UX Designer Agent Node.
    Role: Design comprehensive UI/UX systems for the game.
    """
    logger.info("ui_ux_designer_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.75
        )
        
        concept = state.get("concept", "")
        genre = state.get("genre", "Unknown")
        mechanics = state.get("mechanics", [])
        
        system_msg = SystemMessage(content="""You are a **Lead UI/UX Designer** specialized in game interfaces.

Design user-friendly, accessible, and visually appealing UI systems.

Output JSON:
```json
{
  "menu_architecture": {
    "main_menu": ["New Game", "Continue", "Settings", "Quit"],
    "pause_menu": ["Resume", "Settings", "Quit to Menu"],
    "settings_categories": ["Video", "Audio", "Controls", "Accessibility"]
  },
  "hud_design": {
    "layout_type": "Minimal / Diegetic / Full HUD",
    "elements": [
      {"name": "Health Bar", "position": "Top Left", "style": "Linear bar with glow"},
      {"name": "Minimap", "position": "Bottom Right", "style": "Circular radar"}
    ],
    "scalability": "Responsive across 16:9, 21:9, 4:3"
  },
  "onboarding_flow": {
    "tutorial_type": "Interactive / Guided / Tooltips",
    "stages": [
      {"stage": 1, "teaches": "Basic movement", "duration": "2 minutes"},
      {"stage": 2, "teaches": "Combat basics", "duration": "3 minutes"}
    ]
  },
  "accessibility_features": [
    "Colorblind modes (Protanopia, Deuteranopia, Tritanopia)",
    "Remappable controls",
    "Subtitles with speaker labels",
    "UI scaling (100%, 125%, 150%)",
    "High contrast mode"
  ],
  "ux_principles": [
    "Minimize clicks to core actions (max 2 clicks)",
    "Clear visual hierarchy (size, color, spacing)",
    "Consistent iconography across all menus"
  ],
  "wireframes_notes": "Main menu uses vertical layout for accessibility, settings grouped by category"
}
```

Cite UX best practices (Don't Make Me Think, The Design of Everyday Things) when applicable.""")
        
        human_msg = HumanMessage(content=f"""Design UI/UX for:
**Concept**: {concept}
**Genre**: {genre}
**Mechanics**: {mechanics}

Create:
1. Menu architecture (main, pause, settings)
2. HUD design with element positioning
3. Onboarding/tutorial flow
4. Accessibility features
5. UX principles to follow""")
        
        result = await safe_agent_invoke(
            agent_name="UIUXDesigner",
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
            ui_ux_design = json.loads(output)
        except json.JSONDecodeError:
            ui_ux_design = {"raw_output": output}
        
        logger.info(
            "ui_ux_designer_completed",
            hud_layout=ui_ux_design.get("hud_design", {}).get("layout_type", "Unknown")
        )
        
        return {
            **state,
            "ui_ux_design": ui_ux_design
        }
    
    except Exception as e:
        logger.exception("ui_ux_designer_error", error=str(e))
        return state
