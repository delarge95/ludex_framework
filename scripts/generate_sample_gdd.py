import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import GameDesignState
from agents.game_design.market_analyst import market_analyst_node
from agents.game_design.mechanics_designer import mechanics_designer_node
from agents.game_design.producer import producer_node
from agents.game_design.gdd_writer import gdd_writer_node

async def generate_sample():
    print("🚀 Starting GDD Generation Script...")
    
    # Initial State
    state = GameDesignState(
        concept="A cozy farming sim where you grow musical plants that create a symphony as they bloom. Stardew Valley meets Guitar Hero.",
        genre="Simulation / Rhythm",
        market_analysis={},
        mechanics=[],
        technical_stack={},
        production_plan=None,
        gdd_content={},
        messages=[],
        current_step="start",
        errors=[]
    )

    # 1. Market Analyst
    print("\n📊 Running Market Analyst...")
    state = await market_analyst_node(state)
    print("✅ Market Analysis Complete")

    # 2. Mechanics Designer
    print("\n⚙️ Running Mechanics Designer...")
    state = await mechanics_designer_node(state)
    print("✅ Mechanics Design Complete")

    # 3. Producer
    print("\n📅 Running Producer...")
    state = await producer_node(state)
    print("✅ Production Planning Complete")

    # 4. GDD Writer
    print("\n📝 Running GDD Writer...")
    state = await gdd_writer_node(state)
    print("✅ GDD Generation Complete")

    # Save to file
    output_path = "docs/generated/musical_farming_sim_gdd.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(state["gdd_content"]["full_doc"])
    
    print(f"\n💾 Saved GDD to: {output_path}")

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(generate_sample())
