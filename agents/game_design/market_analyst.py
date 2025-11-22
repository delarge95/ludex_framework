import structlog
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings
from tools.game_info.game_info_tool import create_game_info_tools
from tools.game_info.steam_scraper import get_steam_data

logger = structlog.get_logger(__name__)

async def market_analyst_node(state: GameDesignState) -> GameDesignState:
    """
    Market Analyst Agent Node.
    Role: Competitive analysis, market validation, monetization strategy.
    """
    logger.info("market_analyst_started", concept=state["concept"])

    try:
        # Initialize LLM
        llm = create_model(
            provider="github",
            model=settings.GITHUB_MODEL,
            temperature=0.7
        )

        # Initialize Tools
        game_info_tools = create_game_info_tools()
        tools = [*game_info_tools, get_steam_data]

        # System Prompt - Enhanced with competitive analysis
        system_msg = SystemMessage(content="""You are a veteran Product Manager at a top game publisher with 15+ years experience.
        You have a track record of greenlighting hits (#1 Steam bestsellers, IGN 9/10+) and cancelling flops before they burn budget.
        You don't believe in "gut feeling" - you believe in DATA + PLAYER PSYCHOLOGY.
        You use IGDB, SteamDB, and Steam Reviews as your primary weapons.

        Your Mission:
        1. **Competitive Landscape Analysis**:
           - Search for similar games on IGDB (at least 3-5 titles)
           - Identify direct competitors AND adjacent market segments
           - Analyze what made successful titles work (gameplay loops, hooks, monetization)
           - Identify failures and why they failed (poor execution vs bad concept)
        
        2. **Market Demand Validation**:
           - Use Steam data (tags, reviews, player counts) to gauge actual player demand
           - Identify trending mechanics/themes (e.g., roguelike resurgence, extraction shooters)
           - Calculate market saturation: HIGH (avoid), MEDIUM (differentiate), LOW (opportunity)
        
        3. **Target Audience Segmentation**:
           - Primary demographic (age, gaming habits, spending power)
           - Player motivation profile (achievement, social, immersion, exploration)
           - Platform preference (PC, Console, Mobile, Cross-platform)
        
        4. **Monetization Strategy**:
           - Recommend pricing tier ($9.99 indie, $29.99 mid-tier, $59.99 premium)
           - Suggest monetization model (Premium, F2P + cosmetics, F2P + battle pass, DLC seasons)
           - Estimate lifetime value (LTV) potential
        
        5. **Risk Assessment**:
           - Market saturation risk (1-10 scale)
           - Technical complexity risk (can indie team deliver?)
           - Player acquisition cost (high competition = high CAC)
        
        6. **Go/No-Go Recommendation**:
           - GREEN LIGHT: Clear market gap + proven demand + feasible execution
           - YELLOW LIGHT: Crowded market BUT strong differentiation needed
           - RED LIGHT: Oversaturated + no clear unique value proposition

        Output Format (STRICT JSON, no markdown):
        {
            "competitive_analysis": {
                "similar_games": [
                    {"title": "Game 1", "strengths": "...", "weaknesses": "..."},
                    {"title": "Game 2", "strengths": "...", "weaknesses": "..."}
                ],
                "market_saturation": "LOW|MEDIUM|HIGH",
                "positioning_opportunity": "What makes this concept unique?"
            },
            "target_audience": {
                "primary_demographic": "18-35 male PC gamers",
                "player_motivation": "Achievement + Exploration",
                "estimated_size": "100K-500K potential players"
            },
            "monetization": {
                "recommended_model": "Premium $19.99",
                "reasoning": "Similar to Hades pricing tier...",
                "estimated_ltv": "$25-40 per player"
            },
            "market_trends": {
                "rising_trends": ["Roguelike mechanics", "Deckbuilding"],
                "declining_trends": ["Battle Royale fatigue"],
                "steam_tags": ["Roguelike", "Deckbuilder", "Cyberpunk"]
            },
            "risk_score": {
                "saturation_risk": 4,
                "technical_risk": 6,
                "acquisition_risk": 5,
                "overall": "MEDIUM"
            },
            "recommendation": "GREEN_LIGHT|YELLOW_LIGHT|RED_LIGHT",
            "rationale": "2-3 sentence justification"
        }
        
        CRITICAL: Return ONLY valid JSON. No markdown. No code fences. No explanations outside JSON.
        """)

        human_msg = HumanMessage(content=f"Analyze the market for this concept: {state['concept']} ({state['genre']})")

        # Invoke Agent
        import time
        start_time = time.time()
        
        result = await safe_agent_invoke(
            llm=llm,
            tools=tools,
            messages=[system_msg, human_msg],
            max_iterations=5
        )
        
        execution_time = int((time.time() - start_time) * 1000)

        # Parse Output
        import json
        try:
            market_data = json.loads(result["output"])
        except:
            # Fallback if LLM returns markdown-wrapped JSON or just text
            logger.warning("failed_to_parse_json", output=result["output"])
            market_data = {
                "competitive_analysis": {
                    "similar_games": [],
                    "market_saturation": "UNKNOWN",
                    "positioning_opportunity": result["output"][:200]
                },
                "target_audience": {
                    "primary_demographic": "General Audience",
                    "player_motivation": "Unknown",
                    "estimated_size": "Unknown"
                },
                "recommendation": "YELLOW_LIGHT",
                "rationale": "Unable to parse market analysis"
            }

        # Construct Reasoning Log
        from core.state import AgentReasoning, ToolCall
        
        # Transform tool calls to our schema
        tool_calls_log: List[ToolCall] = []
        for tc in result.get("tool_calls", []):
            tool_calls_log.append({
                "tool_name": tc["name"],
                "args": tc["args"],
                "timestamp": str(time.time()), # Approximation, ideally captured in safe_agent_invoke
                "result_summary": "Tool executed successfully", # We might want to capture actual result in safe_agent_invoke return
                "raw_data_ref": None
            })

        reasoning_entry: AgentReasoning = {
            "agent_name": "MarketAnalyst",
            "input_state_snapshot": {"concept": state["concept"], "genre": state["genre"]},
            "tool_calls": tool_calls_log,
            "llm_reasoning": result["output"], # In a real CoT scenario, we'd parse this out if it was separate
            "sources_cited": [], # We would need to parse this from the output or tool results
            "output_created": market_data,
            "timestamp": str(time.time()),
            "execution_time_ms": execution_time
        }

        # Update State
        new_reasoning_log = state.get("reasoning_log", []) + [reasoning_entry]
        new_tool_log = state.get("tool_execution_log", []) + tool_calls_log

        return {
            **state,
            "market_analysis": market_data,
            "current_step": "mechanics_designer",
            "messages": state["messages"] + [HumanMessage(content=result["output"])],
            "reasoning_log": new_reasoning_log,
            "tool_execution_log": new_tool_log
        }

    except Exception as e:
        logger.error("market_analyst_failed", error=str(e))
        return {
            **state,
            "errors": state.get("errors", []) + [str(e)]
        }
