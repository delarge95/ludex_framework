"""
Level Designer Agent for LUDEX Framework (Sprint 15)

Designs level flow, pacing, environmental storytelling integration,
and difficulty curve for engaging gameplay progression.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from core.agent_synergies import extract_narrative_level_beats, inject_synergy_context
from config.settings import settings

logger = structlog.get_logger(__name__)

async def level_designer_node(state: GameDesignState) -> GameDesignState:
    """
    Level Designer Agent Node.
    Role: Design level structure, pacing, and progression.
    """
    logger.info("level_designer_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.75
        )
        
        mechanics = state.get("mechanics", [])
        narrative = state.get("narrative_structure", {})
        world_lore = state.get("world_lore", {})
        
        # SYNERGY: Extract narrative beats from NarrativeArchitect
        beats = extract_narrative_level_beats(narrative)
        
        base_prompt = """You are a **Lead Level Designer** for games.

Design levels that balance challenge, pacing, and narrative integration.

Output JSON:
```json
{
  "level_structure": {
    "total_levels": 12,
    "level_types": [
      {"name": "Tutorial", "count": 1, "duration": "10 minutes"},
      {"name": "Combat arenas", "count": 6, "duration": "20-30 minutes"},
      {"name": "Boss fights", "count": 3, "duration": "15 minutes"},
      {"name": "Exploration hubs", "count": 2, "duration": "30+ minutes"}
    ]
  },
  "level_flow_example": {
    "level_name": "Level 3: The Forgotten Forge",
    "narrative_setup": "Find ancient weapon blueprints",
    "gameplay_flow": [
      {"phase": "Introduction", "duration": "2 min", "gameplay": "Exploration, environmental storytelling"},
      {"phase": "Rising action", "duration": "8 min", "gameplay": "Combat encounters, puzzle solving"},
      {"phase": "Climax", "duration": "5 min", "gameplay": "Mini-boss fight"},
      {"phase": "Falling action", "duration": "3 min", "gameplay": "Escape sequence"},
      {"phase": "Resolution", "duration": "2 min", "gameplay": "Reward reveal, story beat"}
    ],
    "pacing_rhythm": "Tension → Release → Tension → Release"
  },
  "environmental_storytelling": {
    "techniques": [
      "Abandoned settlements hint at past events",
      "Graffiti shows faction conflicts",
      "Environmental clues guide progression"
    ],
    "integration_with_narrative": "Each level reveals lore through environment"
  },
  "difficulty_curve": {
    "progression_model": "Gradual increase with peaks at boss fights",
    "difficulty_levels": [
      {"level": 1, "difficulty": "Easy (tutorial)", "enemy_count": 5},
      {"level": 5, "difficulty": "Medium", "enemy_count": 15},
      {"level": 10, "difficulty": "Hard", "enemy_count": 25},
      {"level": 12, "difficulty": "Very Hard (final boss)", "enemy_count": 1}
    ],
    "balancing_strategy": "Playtesting with 50th percentile skill players"
  },
  "replayability_features": {
    "secrets": "Hidden collectibles in each level (3-5 per level)",
    "alternate_paths": "Multiple solutions to puzzles",
    "time_trials": "Speedrun mode unlocked after completion",
    "difficulty_modifiers": "New Game+ with harder enemies"
  },
  "technical_considerations": {
    "occlusion_culling": "Use portals/rooms for performance",
    "streaming": "Level streaming for seamless transitions",
    "checkpoints": "Every 5 minutes of gameplay",
    "save_system": "Auto-save at checkpoints + manual save"
  }
}
```"""
        
        # SYNERGY: Inject narrative beats into prompt
        system_msg = SystemMessage(content=inject_synergy_context(base_prompt, {"beats": beats}, "narrative_level"))
        
        human_msg = HumanMessage(content=f"""Design level structure for:
**Mechanics**: {mechanics}
**Narrative**: {narrative}
**World**: {world_lore}

Create:
1. Level structure and types
2. Level flow example with pacing
3. Environmental storytelling integration
4. Difficulty curve
5. Replayability features""")
        
        result = await safe_agent_invoke(
            agent_name="LevelDesigner",
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
            level_design = json.loads(output)
        except json.JSONDecodeError:
            level_design = {"raw_output": output}
        
        logger.info("level_designer_completed")
        
        return {
            **state,
            "level_design": level_design
        }
    
    except Exception as e:
        logger.exception("level_designer_error", error=str(e))
        return state
