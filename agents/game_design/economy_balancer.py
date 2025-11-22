"""
Economy Balancer Agent for LUDEX Framework (Sprint 14)

Designs economy systems for F2P games including currency design,
progression curves, monetization balance, and economy simulation.

NOTE: This agent is CONDITIONAL - only activates for F2P/monetization games.
"""

import structlog
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def economy_balancer_node(state: GameDesignState) -> GameDesignState:
    """
    Economy Balancer Agent Node (CONDITIONAL - F2P only).
    Role: Design balanced economy and monetization systems.
    """
    logger.info("economy_balancer_started")
    
    try:
        llm = create_model(
            provider=state.get("llm_provider", "github"),
            model=settings.GITHUB_MODEL,
            temperature=0.7
        )
        
        mechanics = state.get("mechanics", [])
        
        system_msg = SystemMessage(content="""You are an **Economy Balancer** specialized in F2P game monetization.

Design fair, engaging economy systems that balance player progression and revenue.

Output JSON:
```json
{
  "currency_design": {
    "hard_currency": {
      "name": "Gems",
      "earn_rate": "5-10 per day (free)",
      "purchase_packs": [100, 500, 1200, 2500, 6000],
      "price_points_usd": [0.99, 4.99, 9.99, 19.99, 49.99]
    },
    "soft_currency": {
      "name": "Gold",
      "earn_rate": "500-2000 per hour of gameplay",
      "uses": ["Upgrades", "Consumables", "Crafting"]
    }
  },
  "progression_curve": {
    "total_levels": 50,
    "xp_formula": "XP = 100 * (level ^ 1.5)",
    "time_to_max_level": "200-300 hours",
    "retention_gates": [
      {"level": 5, "unlock": "PvP modes"},
      {"level": 10, "unlock": "Guilds"},
      {"level": 20, "unlock": "Raids"}
    ]
  },
  "monetization_balance": {
    "conversion_target": "2-5% of players spend",
    "arpu": "$3-5 (Average Revenue Per User)",
    "arppu": "$50-100 (Average Revenue Per Paying User)",
    "monetization_types": [
      "Battle Pass ($9.99/season)",
      "Cosmetic skins ($2.99-$9.99)",
      "Gacha pulls (100 Gems per pull, 0.5% drop rate for legendary)"
    ],
    "anti_whale_protection": "Diminishing returns after $100/month spending"
  },
  "economy_simulation": {
    "tools": "Excel-based economy simulator",
    "key_metrics": [
      "Daily Active Users (DAU)",
      "Average session length (30 min target)",
      "Currency sink effectiveness (>80% spent within 7 days)"
    ],
    "inflation_control": [
      "Hard cap on gold generation per day",
      "Currency sinks (cosmetics, upgrades)",
      "Seasonal economy resets"
    ]
  },
  "ethical_considerations": {
    "loot_box_regulation": "Display drop rates prominently (per Apple/Google policies)",
    "no_pay_to_win": "Cosmetic-only monetization for competitive modes",
    "pity_system": "Guaranteed legendary after 100 pulls",
    "parental_controls": "Spending limits for minor accounts"
  }
}
```""")
        
        human_msg = HumanMessage(content=f"""Design F2P economy for:
**Mechanics**: {mechanics}

Create:
1. Currency design (hard/soft)
2. Progression curve with retention gates
3. Monetization balance (conversion, ARPU, ARPPU)
4. Economy simulation approach
5. Ethical considerations (loot boxes, pay-to-win)""")
        
        result = await safe_agent_invoke(
            agent_name="EconomyBalancer",
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
            economy_spec = json.loads(output)
        except json.JSONDecodeError:
            economy_spec = {"raw_output": output}
        
        logger.info("economy_balancer_completed")
        
        return {
            **state,
            "economy_spec": economy_spec
        }
    
    except Exception as e:
        logger.exception("economy_balancer_error", error=str(e))
        return state
