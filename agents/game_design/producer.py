import structlog
from langchain_core.messages import SystemMessage, HumanMessage

from core.state import GameDesignState
from core.model_factory import create_model
from core.agent_utils import safe_agent_invoke
from config.settings import settings

logger = structlog.get_logger(__name__)

async def producer_node(state: GameDesignState) -> GameDesignState:
    """
    Producer Agent Node.
    Role: Project scoping, timeline estimation, team composition, budget planning.
    """
    logger.info("producer_started")

    try:
        llm = create_model(
            provider="github",
            model=settings.GITHUB_MODEL,
            temperature=0.7
        )

        # Producer relies on reasoning, no external tools needed
        tools = [] 

        system_msg = SystemMessage(content="""You are an Executive Producer with 12+ years at AAA and indie studios.
        You've shipped 20+ titles across all budgets ($100K indie -> $50M AAA).
        You're known for ACCURATE ESTIMATES and REALISTIC SCOPING.
        
        Your Philosophy:
        - "Hope is not a strategy" (plan for delays and feature cuts)
        - Triple the estimate for anything "new" or "innovative"
        - Team > Features (small talented team beats bloated mediocre team)
        
        Your Mission:
        1. **Scope Classification**:
           - PROTOTYPE (2-4 months, 1-3 people, $0-50K)
           - INDIE (6-18 months, 3-10 people, $100K-500K)
           - MID-TIER (18-30 months, 10-30 people, $1M-10M)
           - AAA (30-48 months, 50-200 people, $20M-100M)
        
        2. **Phase Breakdown**:
           - **Pre-Production** (10-20% of time): Prototyping, vertical slice, tooling
           - **Production** (50-60%): Content creation, asset pipeline, iteration
           - **Alpha** (10-15%): Feature complete, first playable
           - **Beta** (10-15%): Bug fixing, balancing, polish
           - **Gold Master** (5-10%): Certification, final QA, launch prep
        
        3. **Team Composition**:
           - Core roles (Designer, Programmer, Artist + ratios)
           - Specialized needs (AI engineer, Network programmer, Tech Artist)
           - Contractor vs Full-time ratio
           - Recommend team size PER PHASE (ramp up/down)
        
        4. **Budget Estimation**:
           - Personnel costs (70-80% of budget)
           - Tools & Licenses (Unity Pro, Substance, Middleware)
           - Marketing & Distribution (especially for indie)
           - Contingency buffer (20% minimum)
        
        5. **Risk Register**:
           - Technical risks (new engine, multiplayer, VR)
           - Creative risks (untested genre mix, experimental mechanics)
           - Business risks (market timing, platform exclusivity)
           - Each risk: Probability (1-10), Impact (1-10), Mitigation strategy
        
        6. **Milestones & Success Criteria**:
           - What defines "done" for each milestone
           - Key Performance Indicators (fun factor, retention, performance)
           - Decision gates (go/no-go after each phase)

        Output Format (STRICT JSON):
        {
            "scope_classification": "PROTOTYPE|INDIE|MID_TIER|AAA",
            "total_timeline": {
                "months": 12,
                "breakdown": {
                    "pre_production": 2,
                    "production": 7,
                    "alpha": 1,
                    "beta": 1,
                    "gold": 1
                }
            },
            "team_composition": {
                "ideal_size": 5,
                "core_roles": [
                    {"role": "Game Designer", "count": 1, "seniority": "Senior"},
                    {"role": "Unity Developer", "count": 2, "seniority": "Mid-Senior"},
                    {"role": "2D/3D Artist", "count": 1, "seniority": "Mid"},
                    {"role": "Sound Designer", "count": 0.5, "seniority": "Contractor"}
                ],
                "specialized_needs": ["AI Engineer for procedural generation"]
            },
            "budget_estimate": {
                "currency": "USD",
                "total_range": "$200K-350K",
                "breakdown": {
                    "personnel": "$160K-280K",
                    "tools_licenses": "$10K-20K",
                    "marketing": "$20K-40K",
                    "contingency": "$10K-10K"
                }
            },
            "milestones": [
                {
                    "name": "Vertical Slice",
                    "month": 3,
                    "deliverables": ["10min playable demo", "Core loop proven", "Art style locked"],
                    "success_criteria": "Testers play for 30+ min without prompting"
                }
            ],
            "risk_register": [
                {
                    "risk": "Procedural generation may not be fun",
                    "probability": 6,
                    "impact": 8,
                    "mitigation": "Prototype generator in month 1, fallback to hand-designed levels"
                }
            ],
            "key_assumptions": [
                "Team has prior Unity experience",
                "No multiplayer (avoids netcode complexity)",
                "PC-first (console ports post-launch)"
            ]
        }
        
        CRITICAL: Return ONLY valid JSON. No markdown. Consider mechanic complexity and tech stack.
        """)

        context = f"""
        Concept: {state['concept']}
        Mechanics: {state.get('mechanics', [])}
        Tech Stack: {state.get('technical_stack', {})}
        Market Recommendation: {state.get('market_analysis', {}).get('recommendation', 'UNKNOWN')}
        """
        human_msg = HumanMessage(content=f"Create production roadmap based on: {context}")

        result = await safe_agent_invoke(
            llm=llm,
            tools=tools,
            messages=[system_msg, human_msg],
            max_iterations=3
        )

        import json
        import random
        import numpy as np

        try:
            roadmap = json.loads(result["output"])
            
            # --- MONTE CARLO SIMULATION ---
            # Extract base values
            try:
                base_months = roadmap["total_timeline"]["months"]
                # Parse budget string "$200K-350K" or "$60M"
                budget_str = roadmap["budget_estimate"]["total_range"].replace("$", "").replace(",", "").strip()
                
                def parse_value(val_str):
                    val_str = val_str.upper()
                    if "M" in val_str:
                        return float(val_str.replace("M", "")) * 1_000_000
                    if "K" in val_str:
                        return float(val_str.replace("K", "")) * 1_000
                    return float(val_str)

                if "-" in budget_str:
                    parts = budget_str.split("-")
                    low = parse_value(parts[0])
                    high = parse_value(parts[1])
                    base_budget = (low + high) / 2
                else:
                    base_budget = parse_value(budget_str)
                
                # Determine volatility based on risk register
                risk_score = sum([r.get("impact", 5) * r.get("probability", 5) for r in roadmap.get("risk_register", [])])
                volatility = 0.1 + (risk_score / 500) # Base 10% + risk factor
                
                # Run 1000 simulations
                sim_months = []
                sim_budgets = []
                for _ in range(1000):
                    # Random factor: Normal distribution centered on 1.0 with sigma=volatility
                    factor = np.random.normal(1.0 + (volatility/2), volatility) # Bias slightly upwards (optimism bias correction)
                    sim_months.append(base_months * factor)
                    sim_budgets.append(base_budget * factor)
                
                # Calculate percentiles
                p80_months = np.percentile(sim_months, 80)
                p80_budget = np.percentile(sim_budgets, 80)
                
                risk_analysis = {
                    "monte_carlo_score": int(100 - (volatility * 100)), # Higher is safer
                    "budget_probability": f"80% chance < ${int(p80_budget):,}",
                    "timeline_probability": f"80% chance < {int(p80_months)} months",
                    "risk_factors": roadmap.get("risk_register", [])
                }
                
                roadmap["risk_analysis"] = risk_analysis
                logger.info("monte_carlo_simulation_completed", volatility=volatility, p80_months=p80_months)
                
            except Exception as e:
                logger.warning("monte_carlo_failed", error=str(e))
                roadmap["risk_analysis"] = {
                    "monte_carlo_score": 50,
                    "budget_probability": "Simulation Failed",
                    "timeline_probability": "Simulation Failed",
                    "risk_factors": []
                }
            # ------------------------------

        except:
            logger.warning("failed_to_parse_producer_json", output=result["output"])
            roadmap = {
                "scope_classification": "INDIE",
                "total_timeline": {"months": 12},
                "team_composition": {"ideal_size": 5},
                "budget_estimate": {"total_range": "Unknown"},
                "risk_analysis": None
            }

        return {
            **state,
            "production_plan": roadmap,
            "current_step": "gdd_writer",
            "messages": state["messages"] + [HumanMessage(content=json.dumps(roadmap))]
        }

    except Exception as e:
        logger.error("producer_failed", error=str(e))
        return {
            **state,
            "errors": state.get("errors", []) + [str(e)]
        }
