import structlog
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from tools.retrieval_tool import RetrievalTool
from config.settings import settings

logger = structlog.get_logger(__name__)

async def mechanics_designer_node(state: GameDesignState) -> GameDesignState:
    """
    Mechanics Designer Agent Node.
    Role: Design genre-specific core loops and mechanics with RAG support.
    """
    logger.info("mechanics_designer_started")

    try:
        llm = create_model(
            provider="github",
            model=settings.GITHUB_MODEL,
            temperature=0.7
        )

        # Initialize Retrieval Tool
        retrieval_tool = RetrievalTool()
        tools = [retrieval_tool.search_design_patterns]

        # Enhanced system prompt with genre templates and priority ranking
        system_msg = SystemMessage(content="""You are a Lead Game Designer with 10+ years at top studios (Valve, Supergiant, FromSoftware).
        You specialize in CORE LOOP DESIGN and genre-specific mechanics that create ADDICTION LOOPS.
        
        Your Philosophy:
        - "Minutes to learn, lifetime to master" (easy to understand, deep mastery)
        - Every mechanic must serve the core loop (no feature creep)
        - Mechanics should create EMERGENT GAMEPLAY (player creativity)
        
        Your Mission:
        1. **Genre Analysis**: Identify the core genre and its proven mechanics
           - Roguelike -> Meta-progression, Permadeath, Procedural generation
           - Strategy -> Resource management, Tech trees, Asymmetric factions
           - Action -> Combat system, Movement tech, Skill expression
        
        2. **Core Loop Design**:
           - Define the 30-second loop (what player does moment-to-moment)
           - Define the 5-minute loop (short-term goals, dopamine hits)
           - Define the 1-hour loop (session objectives)
           - Define the 10-hour loop (long-term progression)
        
        3. **Mechanic Prioritization**:
           - **CORE** (P0): Essential to the genre, game fails without these
           - **DIFFERENTIATOR** (P1): What makes THIS game unique
           - **POLISH** (P2): Nice-to-have that elevates quality
        
        4. **Technical Feasibility**:
           - Rate each mechanic: SIMPLE / MEDIUM / COMPLEX / RISKY
           - Flag mechanics that require specialized tech (physics, AI, networking)
        
        5. **Reference Research**:
           - Use RAG tool to find Unity/Unreal design patterns
           - Reference 2-3 existing games that implemented similar mechanics
           - Learn from their successes AND failures

        Output Format (STRICT JSON array):
        [
            {
                "name": "Mechanic Name",
                "priority": "CORE|DIFFERENTIATOR|POLISH",
                "description": "What it does and why it's fun (2-3 sentences)",
                "core_loop": "30sec|5min|1hour|10hour",
                "reference_games": ["Game A did this well because...", "Game B failed because..."],
                "technical_complexity": "SIMPLE|MEDIUM|COMPLEX|RISKY",
                "implementation_notes": "Key technical requirements or risks",
                "player_engagement": "What dopamine hit does this create?"
            }
        ]
        
        CRITICAL:
        - Minimum 5 mechanics total (3 CORE, 1-2 DIFFERENTIATOR, 1-2 POLISH)
        - Every mechanic must justify why it exists (no fluff)
        - Return ONLY valid JSON array. No markdown. No explanations outside JSON.
        """)

        # Get market context for mechanic design
        market_context = (state.get('market_analysis') or {}).get('competitive_analysis', {}).get('positioning_opportunity', '')
        
        human_msg = HumanMessage(content=f"""Design mechanics for: {state['concept']}
        
        Market Positioning: {market_context}
        Genre: {state.get('genre', 'Unknown')}
        
        Remember: Focus on what makes THIS game different while respecting genre conventions.
        """)

        result = await safe_agent_invoke(
            llm=llm,
            tools=tools,
            messages=[system_msg, human_msg],
            max_iterations=5
        )

        import json
        try:
            mechanics = json.loads(result["output"])
        except:
            logger.warning("failed_to_parse_mechanics_json", output=result["output"])
            mechanics = []

        return {
            **state,
            "mechanics": mechanics,
            "current_step": "system_designer",
            "messages": state["messages"] + [HumanMessage(content=result["output"])]
        }

    except Exception as e:
        logger.error("mechanics_designer_failed", error=str(e))
        return {
            **state,
            "errors": state.get("errors", []) + [str(e)]
        }
