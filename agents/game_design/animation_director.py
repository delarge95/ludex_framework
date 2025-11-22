"""
Animation Director Agent for LUDEX Framework (Sprint 12)

Designs animation catalogs, state machines, and blending strategies
for fluid character and object animations.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def animation_director_node(state: GameDesignState) -> GameDesignState:
    """
    Animation Director Agent Node.
    Role: Design animation systems and catalogs.
    """
    logger.info("animation_director_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.7
        )
        
        mechanics = state.get("mechanics", [])
        character_visuals = state.get("character_visuals", {})
        
        system_msg = SystemMessage(content="""You are an **Animation Director** for games.

Design comprehensive animation systems that bring characters and worlds to life.

Output JSON:
```json
{
  "animation_catalog": {
    "locomotion": [
      {"name": "Idle", "blend_time": "0.1s", "priority": 1},
      {"name": "Walk", "blend_time": "0.2s", "priority": 2},
      {"name": "Run", "blend_time": "0.15s", "priority": 3},
      {"name": "Sprint", "blend_time": "0.25s", "priority": 4}
    ],
    "combat": [
      {"name": "Light Attack", "frames": 30, "can_cancel_after": 15},
      {"name": "Heavy Attack", "frames": 60, "can_cancel_after": 45}
    ],
    "contextual": [
      {"name": "Climb Ledge", "type": "IK-driven"},
      {"name": "Open Door", "type": "Animation Matching"}
    ]
  },
  "state_machine_design": {
    "layers": [
      {"name": "Base Layer", "purpose": "Locomotion and core movement"},
      {"name": "Upper Body Layer", "purpose": "Combat and item interactions"},
      {"name": "Facial Layer", "purpose": "Expressions and dialogue"}
    ],
    "transitions": [
      {"from": "Idle", "to": "Walk", "condition": "speed > 0.1", "blend": "0.2s"},
      {"from": "Walk", "to": "Run", "condition": "speed > 3.0", "blend": "0.15s"}
    ]
  },
  "blending_strategies": {
    "locomotion_blend_tree": "1D blend space (speed 0-10)",
    "directional_movement": "2D blend space (speed + direction)",
    "combat_layering": "Additive blending for upper body animations"
  },
  "procedural_animation": {
    "ik_targets": ["Foot placement on slopes", "Hand placement on objects"],
    "procedural_effects": ["Head look-at", "Weapon sway", "Cloth simulation"]
  },
  "technical_specs": {
    "target_framerate": "60 FPS",
    "animation_compression": "Keyframe reduction + quaternion compression",
    "bone_count": "60-80 bones for main character",
    "animation_budget": "Max 200 animations per character"
  }
}
```""")
        
        human_msg = HumanMessage(content=f"""Design animation system for:
**Mechanics**: {mechanics}
**Character Visuals**: {character_visuals}

Create:
1. Animation catalog (locomotion, combat, contextual)
2. State machine architecture
3. Blending strategies
4. Procedural animation features
5. Technical specs""")
        
        result = await safe_agent_invoke(
            agent_name="AnimationDirector",
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
            animation_plan = json.loads(output)
        except json.JSONDecodeError:
            animation_plan = {"raw_output": output}
        
        logger.info("animation_director_completed")
        
        return {
            **state,
            "animation_plan": animation_plan
        }
    
    except Exception as e:
        logger.exception("animation_director_error", error=str(e))
        return state
