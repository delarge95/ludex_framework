"""
Camera Designer Agent for LUDEX Framework (Sprint 12)

Designs camera systems including third-person, first-person, cinematic,
and Cinemachine configurations for optimal player experience.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from core.agent_synergies import extract_ui_camera_requirements, inject_synergy_context
from config.settings import settings

logger = structlog.get_logger(__name__)

async def camera_designer_node(state: GameDesignState) -> GameDesignState:
    """
    Camera Designer Agent Node.
    Role: Design camera systems and behaviors.
    """
    logger.info("camera_designer_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.7
        )
        
        mechanics = state.get("mechanics", [])
        ui_design = state.get("ui_design", {})
        
        # SYNERGY: Extract camera requirements from UIUXDesigner
        camera_reqs = extract_ui_camera_requirements(ui_design)
        
        base_prompt = """You are a **Camera Systems Designer** for games.

Design camera systems that enhance gameplay and provide cinematic feel.

Output JSON:
```json
{
  "primary_camera_system": "Third-Person / First-Person / Isometric / Side-Scroller",
  "camera_behaviors": {
    "default": {
      "type": "Follow cam with shoulder offset",
      "distance": "3.5 units",
      "height_offset": "1.2 units",
      "damping": "Smooth (0.3s lag)",
      "collision_handling": "Push camera forward on obstruction"
    },
    "combat": {
      "type": "Lock-on camera",
      "behavior": "Focus on target, player at screen edge",
      "transition": "Blend in 0.2s when locking on"
    },
    "exploration": {
      "type": "Free look",
      "behavior": "Player controls yaw/pitch, auto-follows after 2s idle"
    }
  },
  "cinemachine_setup": {
    "virtual_cameras": [
      {"name": "VC_Default", "priority": 10, "follow": "Player", "look_at": "Player Forward"},
      {"name": "VC_Combat", "priority": 20, "follow": "Player", "look_at": "Target"},
      {"name": "VC_Cutscene", "priority": 30, "path": "Dolly track"}
    ],
    "state_driven_camera": "Switch cameras based on game state (exploration/combat/cutscene)"
  },
  "camera_shake": {
    "events": [
      {"trigger": "Explosion nearby", "intensity": "High", "duration": "0.5s"},
      {"trigger": "Footstep (heavy enemy)", "intensity": "Low", "duration": "0.1s"}
    ]
  },
  "cinematic_features": {
    "depth_of_field": "Dynamic focus on look-at target",
    "motion_blur": "Subtle during fast movement",
    "letterboxing": "For cutscenes"
  },
  "technical_specs": {
    "fov": "75 degrees (adjustable 60-90)",
    "near_clip": "0.1 units",
    "far_clip": "1000 units",
    "occlusion_handling": "Transparency or push camera forward"
  }
}
```"""
        
        # SYNERGY: Inject UI requirements into prompt
        system_msg = SystemMessage(content=inject_synergy_context(base_prompt, camera_reqs, "ui_camera"))
        
        human_msg = HumanMessage(content=f"""Design camera system for:
**Mechanics**: {mechanics}

Create:
1. Primary camera type selection
2. Camera behaviors (default, combat, exploration)
3. Cinemachine configuration
4. Camera shake and effects
5. Technical specifications""")
        
        result = await safe_agent_invoke(
            agent_name="CameraDesigner",
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
            camera_systems = json.loads(output)
        except json.JSONDecodeError:
            camera_systems = {"raw_output": output}
        
        logger.info("camera_designer_completed")
        
        return {
            **state,
            "camera_systems": camera_systems
        }
    
    except Exception as e:
        logger.exception("camera_designer_error", error=str(e))
        return state
