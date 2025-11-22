import asyncio
from graphs.game_design_graph import create_game_design_graph
from core.state import GameDesignState

async def test_director_flow():
    print("🧪 Testing Director Flow...")
    
    graph = create_game_design_graph()
    
    # Test Case 1: Vague Concept
    print("\n--- Test Case 1: Vague Concept ('A shooter') ---")
    initial_state = {
        "concept": "A shooter",
        "messages": [],
        "current_step": "start",
        "errors": [],
        "awaiting_input": False
    }
    
    async for event in graph.astream(initial_state):
        for key, value in event.items():
            print(f"Node: {key}")
            if key == "director":
                print(f"Status: {value.get('awaiting_input')}")
                print(f"Questions: {value.get('director_questions')}")
                if value.get('awaiting_input'):
                    print("✅ Director correctly paused for input.")
                else:
                    print("❌ Director failed to pause.")

    # Test Case 2: Clear Concept
    # print("\n--- Test Case 2: Clear Concept ---")
    # clear_concept = "A 2D roguelike shooter where you play as a musical note fighting silence. Visuals are neon. Fast paced."
    # initial_state_2 = {
    #     "concept": clear_concept,
    #     "messages": [],
    #     "current_step": "start",
    #     "errors": [],
    #     "awaiting_input": False
    # }
    
    # # We only run until market_analyst to verify routing
    # async for event in graph.astream(initial_state_2):
    #     for key, value in event.items():
    #         print(f"Node: {key}")
    #         if key == "director":
    #             print(f"Production Mode: {value.get('production_mode')}")
    #             if not value.get('awaiting_input'):
    #                 print("✅ Director correctly proceeded.")
    #         if key == "market_analyst":
    #             print("✅ Reached Market Analyst!")
    #             return # Stop here

if __name__ == "__main__":
    asyncio.run(test_director_flow())
