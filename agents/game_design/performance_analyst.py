"""
Performance Analyst Agent for LUDEX Framework (Sprint 15)

Defines performance targets, memory budgets, LOD strategies,
and optimization recommendations for smooth gameplay.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def performance_analyst_node(state: GameDesignState) -> GameDesignState:
    """
    Performance Analyst Agent Node.
    Role: Define performance targets and optimization strategies.
    """
    logger.info("performance_analyst_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.6
        )
        
        technical_stack = state.get("technical_stack", {})
        target_platforms = state.get("target_platforms", [])
        
        system_msg = SystemMessage(content="""You are a **Lead Performance Analyst** for games.

Define realistic performance targets and optimization strategies.

Output JSON:
```json
{
  "fps_targets": {
    "pc_high_end": "144 FPS (RTX 3080, i9)",
    "pc_mid_range": "60 FPS (GTX 1660, i5)",
    "pc_low_end": "30 FPS (GTX 1050, i3)",
    "console_current_gen": "60 FPS (PS5, Xbox Series X)",
    "console_last_gen": "30 FPS (PS4, Xbox One)",
    "mobile_high": "60 FPS (iPhone 13, Galaxy S21)",
    "mobile_mid": "30 FPS (iPhone X, Galaxy S10)"
  },
  "memory_budgets": {
    "total_memory_pc": "8 GB VRAM recommended",
    "total_memory_console": "13.5 GB (shared, PS5)",
    "total_memory_mobile": "4 GB RAM",
    "breakdown": {
      "textures": "3 GB",
      "meshes": "2 GB",
      "audio": "500 MB",
      "animations": "500 MB",
      "engine_overhead": "2 GB"
    }
  },
  "lod_strategy": {
    "character_lods": [
      {"lod_0": "8k tris (0-10m)", "lod_1": "4k tris (10-30m)", "lod_2": "1k tris (30m+)"},
      {"lod_3": "Impostor billboard (100m+)"}
    ],
    "environment_lods": [
      {"lod_0": "High detail (0-20m)", "lod_1": "Medium (20-50m)", "lod_2": "Low (50m+)"}
    ],
    "lod_bias": "Dynamic based on GPU budget"
  },
  "optimization_recommendations": {
    "rendering": [
      "Use GPU instancing for repeated objects (trees, rocks)",
      "Occlusion culling with conservative settings",
      "Bake lighting for static objects",
      "Use draw call batching (static + dynamic batching)",
      "Limit real-time shadows to key objects"
    ],
    "cpu": [
      "Object pooling for projectiles/particles",
      "Limit physics calculations to 50Hz fixed timestep",
      "Use Unity Jobs System for multi-threading",
      "Avoid GetComponent() in Update loops"
    ],
    "memory": [
      "Texture streaming for large worlds",
      "Compress audio to Vorbis/AAC",
      "Use texture atlases to reduce memory",
      "Unload unused assets via Addressables"
    ],
    "mobile_specific": [
      "Reduce texture resolution (1024x1024 max)",
      "Limit post-processing effects",
      "Use ASTC compression for textures",
      "Minimize overdraw (alpha blending)"
    ]
  },
  "profiling_plan": {
    "tools": ["Unity Profiler", "RenderDoc", "Instruments (iOS)"],
    "key_metrics": [
      "Frame time (main thread, render thread)",
      "Draw calls per frame (<500 target)",
      "SetPass calls (<50 target)",
      "Garbage collection spikes"
    ],
    "optimization_phases": [
      {"phase": "Pre-alpha", "goal": "Establish baseline performance"},
      {"phase": "Alpha", "goal": "Optimize critical path (main gameplay)"},
      {"phase": "Beta", "goal": "Polish and platform-specific optimization"}
    ]
  },
  "performance_budgets": {
    "frame_time_budget_60fps": "16.67ms",
    "breakdown": {
      "cpu_game_logic": "4ms",
      "cpu_rendering": "3ms",
      "gpu_rendering": "8ms",
      "cpu_physics": "2ms",
      "audio": "0.5ms",
      "buffer": "1ms"
    }
  }
}
```""")
        
        human_msg = HumanMessage(content=f"""Define performance targets for:
**Engine**: {technical_stack.get('engine', 'Unity')}
**Platforms**: {target_platforms}

Create:
1. FPS targets per platform
2. Memory budgets with breakdown
3. LOD strategy
4. Optimization recommendations
5. Profiling plan with milestones""")
        
        result = await safe_agent_invoke(
            agent_name="PerformanceAnalyst",
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
            performance_spec = json.loads(output)
        except json.JSONDecodeError:
            performance_spec = {"raw_output": output}
        
        logger.info("performance_analyst_completed")
        
        return {
            **state,
            "performance_spec": performance_spec
        }
    
    except Exception as e:
        logger.exception("performance_analyst_error", error=str(e))
        return state
