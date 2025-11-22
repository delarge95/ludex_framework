"""
Network Architect Agent for LUDEX Framework (Sprint 14)

Designs networking architecture for multiplayer games including netcode strategy,
server infrastructure, matchmaking, and anti-cheat.

NOTE: This agent is CONDITIONAL - only activates for multiplayer games.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def network_architect_node(state: GameDesignState) -> GameDesignState:
    """
    Network Architect Agent Node (CONDITIONAL - Multiplayer only).
    Role: Design networking and multiplayer infrastructure.
    """
    logger.info("network_architect_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.6
        )
        
        mechanics = state.get("mechanics", [])
        technical_stack = state.get("technical_stack", {})
        
        system_msg = SystemMessage(content="""You are a **Network Architect** specialized in multiplayer games.

Design scalable, secure networking architecture for smooth multiplayer experiences.

Output JSON:
```json
{
  "netcode_strategy": {
    "authority_model": "Server-authoritative / Client-authoritative / Hybrid",
    "justification": "Server-authoritative prevents cheating in competitive game",
    "prediction": "Client-side prediction for movement, server reconciliation",
    "lag_compensation": "Rewind time to player's perspective for hit detection",
    "interpolation": "Interpolate other players' positions for smooth movement"
  },
  "server_infrastructure": {
    "hosting_model": "Dedicated servers / Listen servers / Peer-to-peer",
    "cloud_provider": "AWS GameLift / Azure PlayFab / Google Cloud",
    "server_regions": ["US-East", "US-West", "EU-West", "Asia-Pacific"],
    "auto_scaling": "Scale based on player count (min 10 servers, max 100)",
    "tick_rate": "60 Hz for competitive, 30 Hz for casual"
  },
  "matchmaking_design": {
    "algorithm": "Skill-based matchmaking (SBMM) with ELO rating",
    "queue_types": ["Quick Play", "Ranked", "Custom Lobbies"],
    "party_handling": "Balance teams when parties queue together",
    "region_priority": "Prioritize same-region matches (<50ms ping)",
    "wait_time_threshold": "Max 60s wait, then expand skill range"
  },
  "anti_cheat_strategy": {
    "client_side": [
      "Input validation (impossible speeds/actions rejected)",
      "Memory protection (detect memory editing tools)"
    ],
    "server_side": [
      "Server authority on gameplay logic",
      "Statistical analysis (flag abnormal accuracy/reaction times)",
      "Replay system for match reviews"
    ],
    "third_party": "Easy Anti-Cheat (EAC) or BattlEye integration",
    "reporting_system": "Player report system with automated flagging"
  },
  "network_optimization": {
    "bandwidth_target": "<5 KB/s per player",
    "packet_compression": "Delta compression for state updates",
    "interest_management": "Only sync nearby players/objects",
    "network_culling": "Don't sync objects outside player's view cone"
  },
  "technical_specs": {
    "protocol": "UDP with reliability layer (Photon/Mirror/Netcode for GameObjects)",
    "max_players_per_match": 16,
    "max_concurrent_players": 10000,
    "network_tick_rate": "60 Hz",
    "client_send_rate": "30 Hz"
  }
}
```""")
        
        human_msg = HumanMessage(content=f"""Design multiplayer networking for:
**Mechanics**: {mechanics}
**Engine**: {technical_stack.get('engine', 'Unity')}

Create:
1. Netcode strategy (authority, prediction, lag compensation)
2. Server infrastructure (hosting, regions)
3. Matchmaking design
4. Anti-cheat strategy
5. Network optimization""")
        
        result = await safe_agent_invoke(
            agent_name="NetworkArchitect",
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
            networking_spec = json.loads(output)
        except json.JSONDecodeError:
            networking_spec = {"raw_output": output}
        
        logger.info("network_architect_completed")
        
        return {
            **state,
            "networking_spec": networking_spec
        }
    
    except Exception as e:
        logger.exception("network_architect_error", error=str(e))
        return state
