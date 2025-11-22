import asyncio
from agents.game_design.producer import producer_node
from core.state import GameDesignState
from langchain_core.messages import HumanMessage

async def test_risk_engine():
    print("🧪 Testing Risk Engine (Monte Carlo)...")
    
    # Mock Input State
    state = {
        "concept": "A complex MMORPG with VR support", # High risk concept
        "mechanics": [{"name": "VR Combat", "technical_complexity": "RISKY"}],
        "technical_stack": {"engine": "Unreal 5", "risks": ["Netcode", "VR Optimization"]},
        "market_analysis": {"recommendation": "YELLOW_LIGHT"},
        "messages": [],
        "current_step": "system_designer",
        "errors": []
    }
    
    # Run Producer Node
    print("⏳ Running Producer Node (this calls LLM + Simulation)...")
    result = await producer_node(state)
    
    # Verify Output
    plan = result.get("production_plan")
    if not plan:
        print("❌ No production plan generated.")
        return

    risk = plan.get("risk_analysis")
    if not risk:
        print("❌ No risk analysis found in plan.")
        return
        
    print("\n📊 Risk Analysis Results:")
    print(f"   - Monte Carlo Score: {risk['monte_carlo_score']} (Should be low for MMORPG)")
    print(f"   - Budget Prob (80%): {risk['budget_probability']}")
    print(f"   - Timeline Prob (80%): {risk['timeline_probability']}")
    
    if risk['monte_carlo_score'] < 90:
        print("✅ Risk Engine correctly identified high volatility.")
    else:
        print("⚠️ Risk Score seems too high (safe) for a risky project.")

    print("\n✅ Test Complete.")

if __name__ == "__main__":
    asyncio.run(test_risk_engine())
