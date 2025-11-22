"""
Physics Engineer Agent for LUDEX Framework (Sprint 13)

Designs physics systems including physics style, gameplay physics specs,
and performance optimization strategies.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def physics_engineer_node(state: GameDesignState) -> GameDesignState:
    """
    Physics Engineer Agent Node.
    Role: Design physics systems and optimization strategies.
    """
    logger.info("physics_engineer_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.6
        )
        
        mechanics = state.get("mechanics", [])
        technical_stack = state.get("technical_stack", {})
        
        system_msg = SystemMessage(content="""You are a **Lead Physics Engineer** for games.

Design physics systems that enhance gameplay while maintaining performance.

Output JSON:
```json
{
  "physics_style": "Realistic / Arcade / Cartoony / Hybrid",
  "physics_style_justification": "Arcade physics for responsive platforming feel",
  "gameplay_physics": {
    "character_controller": {
      "type": "Kinematic / Dynamic Rigidbody",
      "gravity": "9.8 m/s² (realistic) or custom",
      "ground_detection": "Raycast / Overlap sphere",
      "slope_limit": "45 degrees"
    },
    "jump_mechanics": {
      "jump_height": "2.5 meters",
      "air_control": "80% of ground control",
      "coyote_time": "0.1s (grace period after leaving platform)",
      "jump_buffer": "0.15s (register jump before landing)"
    },
    "projectiles": {
      "type": "Raycast / Rigidbody",
      "gravity_affected": true,
      "velocity": "50 m/s",
      "collision_layers": ["Environment", "Enemies"]
    }
  },
  "ragdoll_system": {
    "enabled": true,
    "activation": "On death or heavy impact",
    "joint_limits": "Realistic anatomical constraints",
    "blend_time": "0.3s from animated to ragdoll"
  },
  "destructible_objects": {
    "approach": "Pre-fractured meshes / Runtime fracturing",
    "max_debris_pieces": 50,
    "debris_lifetime": "5 seconds"
  },
  "optimization_strategies": {
    "physics_timestep": "Fixed 50Hz (0.02s)",
    "collision_detection": "Continuous for fast-moving objects, discrete for others",
    "sleeping_bodies": "Auto-sleep static objects after 2s",
    "layer_collision_matrix": "Disable unnecessary layer interactions",
    "object_pooling": "Reuse projectiles and debris",
    "LOD_physics": "Simplified collision for distant objects"
  },
  "performance_targets": {
    "physics_budget_ms": "2ms per frame (60 FPS)",
    "max_active_rigidbodies": 200,
    "max_collision_checks_per_frame": 500
  }
}
```""")
        
        human_msg = HumanMessage(content=f"""Design physics system for:
**Mechanics**: {mechanics}
**Engine**: {technical_stack.get('engine', 'Unity')}

Create:
1. Physics style selection and justification
2. Gameplay physics (character, jump, projectiles)
3. Ragdoll and destruction systems
4. Performance optimization strategies
5. Performance targets""")
        
        result = await safe_agent_invoke(
            agent_name="PhysicsEngineer",
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
            physics_spec = json.loads(output)
        except json.JSONDecodeError:
            physics_spec = {"raw_output": output}
        
        logger.info("physics_engineer_completed")
        
        return {
            **state,
            "physics_spec": physics_spec
        }
    
    except Exception as e:
        logger.exception("physics_engineer_error", error=str(e))
        return state
