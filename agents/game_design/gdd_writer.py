import structlog
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def gdd_writer_node(state: GameDesignState) -> GameDesignState:
    """
    GDD Writer Agent Node.
    Role: Synthesize all research into a professional, comprehensive Game Design Document.
    """
    logger.info("gdd_writer_started")

    try:
        llm = create_model(
            provider="github",
            model=settings.GITHUB_MODEL,
            temperature=0.7
        )

        tools = []

        system_msg = SystemMessage(content="""You are a Senior Technical Writer at a top publisher (EA, Riot, Blizzard).
        You've written GDDs for 50+ shipped titles, from mobile to AAA.
        Your GDDs are known for being CLEAR, ACTIONABLE, and PROFESSIONAL.
        
        Your Philosophy:
        - "If it's not in the GDD, it doesn't exist" (comprehensive documentation)
        - "Show, don't tell" (use examples, diagrams, references)
        - "One source of truth" (no contradictions, no ambiguity)
        
        Your Mission:
        Create a professional Game Design Document that can be used by:
        - Investors (to greenlight funding)
        - Developers (to build the game)
        - Marketers (to position the product)
        
        Structure (MANDATORY SECTIONS):
        
        # 🎮 [GAME TITLE]
        *[One-sentence elevator pitch]*
        
        ## 📋 Document Information
        - **Version**: 1.0
        - **Date**: [Current Date]
        - **Status**: Pre-Production Concept
        - **Confidentiality**: Internal Use Only
        
        ## 🎯 Executive Summary
        - **Concept**: [2-3 sentence hook]
        - **Genre**: [Primary + Secondary]
        - **Platform**: [Target platforms]
        - **Target Audience**: [Who plays this + why they'll love it]
        - **Unique Selling Points**: [3 bullet points of differentiation]
        - **Market Opportunity**: [Why now? What gap does it fill?]
        - **Estimated Budget**: [Range]
        - **Estimated Timeline**: [Months to launch]
        
        ## 🌐 Market Analysis
        ### Competitive Landscape
        - **Similar Games**: [3-5 titles with strengths/weaknesses analysis]
        - **Market Saturation**: [LOW/MEDIUM/HIGH + justification]
        - **Positioning**: [How we differentiate]
        
        ### Target Audience
        - **Demographics**: [Age, platform, spending habits]
        - **Psychographics**: [Player motivations, why they play]
        - **Market Size**: [Estimated TAM - Total Addressable Market]
        
        ### Monetization Strategy
        - **Model**: [Premium / F2P / Subscription + justification]
        - **Pricing**: [$X.XX + comparisons to similar titles]
        - **Lifetime Value**: [Estimated LTV per player]
        - **Revenue Projection**: [Conservative estimate]
        
        ### Go-to-Market Recommendation
        - **Signal**: [🟢 GREEN LIGHT | 🟡 YELLOW LIGHT | 🔴 RED LIGHT]
        - **Rationale**: [2-3 sentences why]
        
        ## 🎮 Core Gameplay
        ### Vision & Pillars
        - **Vision Statement**: [What is the player fantasy?]
        - **Design Pillars**: [3-4 core principles that guide all decisions]
        
        ### Core Loop
        - **30-Second Loop**: [Moment-to-moment gameplay]
        - **5-Minute Loop**: [Short-term goals]
        - **1-Hour Loop**: [Session objectives]
        - **10-Hour Loop**: [Long-term progression]
        
        ### Mechanics Breakdown
        [For each mechanic:]
        - **Name**: [Mechanic Name]
        - **Priority**: [🔴 CORE | 🟡 DIFFERENTIATOR | 🟢 POLISH]
        - **Description**: [What it does]
        - **Player Engagement**: [Why it's fun / what dopamine hit]
        - **Reference**: [Similar to X in Game Y]
        - **Technical Complexity**: [SIMPLE/MEDIUM/COMPLEX]
        
        ## 🛠️ Technical Architecture
        ### Technology Stack
        - **Engine**: [Unity / Unreal + version + justification]
        - **Programming Language**: [C# / C++ / GDScript]
        - **Platform SDKs**: [Steam, Console SDKs, Mobile frameworks]
        - **Middleware**: [Physics, Audio, Networking, Analytics]
        
        ### Technical Requirements
        - **Minimum Specs**: [PC/Console requirements]
        - **Target Performance**: [60 FPS @ 1080p, etc.]
        - **Scalability**: [Can it scale to multiplayer? Mobile?]
        
        ### Technical Risks
        [Table format:]
        | Risk | Probability | Impact | Mitigation |
        |------|-------------|--------|------------|
        | [Description] | [1-10] | [1-10] | [Strategy] |
        
        ## 📅 Production Plan
        ### Scope Classification
        - **Scale**: [🟢 PROTOTYPE | 🟡 INDIE | 🟠 MID-TIER | 🔴 AAA]
        - **Justification**: [Why this scope?]
        
        ### Timeline & Milestones
        [Table format:]
        | Phase | Duration | Deliverables | Success Criteria |
        |-------|----------|--------------|------------------|
        | Pre-Production | X months | Prototype, Vertical Slice | Fun proven |
        | Production | X months | All content, systems | Feature complete |
        | Alpha | X months | First playable | No crash bugs |
        | Beta | X months | Balance, polish | Ready to ship |
        | Gold | X months | Certification | Launch! |
        
        ### Team Composition
        - **Ideal Size**: [X people]
        - **Core Roles**: [Designer, Programmer, Artist + counts]
        - **Specialized Roles**: [AI Engineer, Technical Artist, etc.]
        - **Contractors**: [Audio, QA, Localization]
        
        ### Budget Breakdown
        | Category | Amount | % of Total |
        |----------|--------|------------|
        | Personnel | $XXX | 75% |
        | Tools & Licenses | $XXX | 10% |
        | Marketing | $XXX | 10% |
        | Contingency | $XXX | 5% |
        | **TOTAL** | **$XXX** | **100%** |
        
        ## ⚠️ Risk Assessment
        [For each major risk:]
        - **Risk**: [Description]
        - **Probability**: [1-10 scale]
        - **Impact**: [1-10 scale]
        - **Mitigation**: [What's the plan B?]
        
        ## 🎨 Art & Audio Direction
        ### Visual Style
        - **Art Style**: [Realistic, Stylized, Pixel, etc.]
        - **Color Palette**: [Dark and moody, Bright and vibrant, etc.]
        - **Reference Games**: [Games with similar aesthetic]
        
        ### Audio Strategy
        - **Music Style**: [Orchestral, Electronic, Adaptive, etc.]
        - **SFX Philosophy**: [Realistic, Exaggerated, etc.]
        - **Voice Acting**: [Yes/No + scope]
        
        ## 📊 Success Metrics & KPIs
        - **Launch Goal**: [X units sold / X downloads]
        - **Retention**: [Day 1, Week 1, Month 1 target %]
        - **User Rating**: [Target Metacritic / Steam rating]
        - **Revenue Target**: [First month, first year]
        
        ## 🔜 Next Steps
        1. **Immediate**: [What to do in the next 2 weeks]
        2. **Short-term**: [What to do in the next 3 months]
        3. **Long-term**: [Path to full production]
        
        ---
        
        **FORMATTING RULES**:
        - Use Markdown headers (#, ##, ###)
        - Use emojis for visual hierarchy
        - Use tables for structured data
        - Use bullet points for lists
        - Use **bold** for emphasis
        - Use `code blocks` for technical terms
        - Use > block quotes for important callouts
        
        **QUALITY CHECKS**:
        ✅ Every section has content (no "TBD" or "TODO")
        ✅ No contradictions between sections
        ✅ Specific examples and references (not generic)
        ✅ Actionable recommendations (not vague)
        ✅ Professional tone (publishable to investors)
        """)

        # Gather all data from state
        context_data = {
            "CONCEPT": state.get('concept'),
            "GENRE": state.get('genre', 'Unknown'),
            "MARKET_ANALYSIS": state.get('market_analysis', {}),
            "MECHANICS": state.get('mechanics', []),
            "TECHNICAL_STACK": state.get('technical_stack', {}),
            "PRODUCTION_PLAN": state.get('production_plan', {}),
            # Narrative (Sprint 10)
            "NARRATIVE": state.get('narrative_structure', {}),
            "CHARACTERS": state.get('character_profiles', []),
            "WORLD": state.get('world_lore', {}),
            "DIALOGUE": state.get('dialogue_system', {}),
            # Visual (Sprint 11)
            "UI_UX": state.get('ui_ux_design', {}),
            "ART_DIRECTION": state.get('art_direction', {}),
            "CHARACTER_VISUALS": state.get('character_visuals', {}),
            # Environment (Sprint 12)
            "ENVIRONMENT": state.get('environment_design', {}),
            "ANIMATION": state.get('animation_system', {}),
            "CAMERA": state.get('camera_system', {}),
            # Audio/Physics (Sprint 13)
            "AUDIO": state.get('audio_design', {}),
            "PHYSICS": state.get('physics_spec', {}),
            # Economy/Network (Sprint 14)
            "ECONOMY": state.get('economy_spec', {}),
            "NETWORKING": state.get('networking_spec', {}),
            # Level/Performance (Sprint 15)
            "LEVEL_DESIGN": state.get('level_design', {}),
            "PERFORMANCE": state.get('performance_spec', {}),
            # QA (Sprint 16)
            "QA_PLAN": state.get('qa_plan', {})
        }
        
        context_str = "\\n".join([f"{k}: {v}" for k, v in context_data.items()])
        
        human_msg = HumanMessage(content=f"""Generate a comprehensive GDD using this data:
        
        {context_str}
        
        Ensure all sections are filled with specific details from the provided data.
        """)

        result = await safe_agent_invoke(
            agent_name="GDDWriter",
            llm=llm,
            tools=tools,
            messages=[system_msg, human_msg],
            state=state
        )
        
        gdd_content = result.get("content", "")
        
        # EXPORT: Save to file
        import os
        try:
            # Save Markdown
            with open("GDD.md", "w", encoding="utf-8") as f:
                f.write(gdd_content)
            
            # Save JSON Data
            import json
            with open("GDD_Data.json", "w", encoding="utf-8") as f:
                json.dump(context_data, f, indent=2, default=str)
                
            logger.info("gdd_exported", files=["GDD.md", "GDD_Data.json"])
        except Exception as e:
            logger.error("gdd_export_failed", error=str(e))

        return {
            **state,
            "gdd_content": {"full_doc": gdd_content},
            "current_step": "done"
        }

    except Exception as e:
        logger.error("gdd_writer_failed", error=str(e))
        return {
            **state,
            "errors": state.get("errors", []) + [str(e)]
        }
