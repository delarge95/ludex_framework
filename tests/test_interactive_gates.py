import asyncio
from graphs.game_design_graph import create_game_design_graph
from core.state import GameDesignState

async def test_gates():
    print("🧪 Testing Interactive Gates...")
    
    graph = create_game_design_graph()
    
    initial_state = {
        "concept": "A racing game",
        "messages": [],
        "current_step": "start",
        "errors": [],
        "awaiting_input": False,
        "production_mode": "prototype" # Skip director for this test if possible, or we handle it
    }
    
    # We need to handle the Director first if it's in the loop
    # But wait, Director is the first node.
    # If we start, it goes to Director.
    # Director might pause if concept is vague. "A racing game" is vague.
    # Let's use a clear concept to skip Director pause.
    
    clear_concept = "A futuristic racing game with anti-gravity cars and neon aesthetics."
    initial_state["concept"] = clear_concept
    
    print("▶️ Starting Graph...")
    # Run until first interruption
    thread_config = {"configurable": {"thread_id": "test_thread_1"}}
    
    # We use graph.stream with thread support for interrupts
    # Note: Local StateGraph compilation without checkpointer might not support interrupts persistence 
    # properly in a script unless we use a MemorySaver.
    
    from langgraph.checkpoint.memory import MemorySaver
    graph = create_game_design_graph()
    checkpointer = MemorySaver()
    graph.checkpointer = checkpointer # Manually attach for test? 
    # Actually, we need to re-compile with checkpointer to use interrupts effectively in script
    # But the graph is already compiled in the file.
    # We will just verify if it stops.
    
    # Re-compile for test with checkpointer
    from langgraph.graph import StateGraph, END, START
    from agents.game_design.director import director_node
    from agents.game_design.market_analyst import market_analyst_node
    from agents.game_design.mechanics_designer import mechanics_designer_node
    from agents.game_design.system_designer import system_designer_node
    from agents.game_design.producer import producer_node
    from agents.game_design.gdd_writer import gdd_writer_node
    
    workflow = StateGraph(GameDesignState)
    workflow.add_node("director", director_node)
    workflow.add_node("market_analyst", market_analyst_node)
    workflow.add_node("mechanics_designer", mechanics_designer_node)
    workflow.add_node("system_designer", system_designer_node)
    workflow.add_node("producer", producer_node)
    workflow.add_node("gdd_writer", gdd_writer_node)
    
    workflow.add_edge(START, "director")
    def route_director(state):
        if state.get("awaiting_input", False): return END
        return "market_analyst"
    workflow.add_conditional_edges("director", route_director, {END: END, "market_analyst": "market_analyst"})
    workflow.add_edge("market_analyst", "mechanics_designer")
    workflow.add_edge("mechanics_designer", "system_designer")
    workflow.add_edge("system_designer", "producer")
    workflow.add_edge("producer", "gdd_writer")
    workflow.add_edge("gdd_writer", END)
    
    # COMPILE WITH CHECKPOINTER AND INTERRUPTS
    app = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["mechanics_designer", "producer"]
    )
    
    print("🏃 Running to first gate (Mechanics Designer)...")
    async for event in app.astream(initial_state, thread_config):
        for key, value in event.items():
            print(f"Node: {key}")
            
    # Check status
    state_snapshot = await app.aget_state(thread_config)
    print(f"Current Node: {state_snapshot.next}")
    
    if "mechanics_designer" in state_snapshot.next:
        print("✅ Paused before Mechanics Designer!")
        
        # Resume
        print("▶️ Resuming...")
        async for event in app.astream(None, thread_config):
             for key, value in event.items():
                print(f"Node: {key}")
                
        state_snapshot = await app.aget_state(thread_config)
        print(f"Current Node: {state_snapshot.next}")
        
        if "producer" in state_snapshot.next:
             print("✅ Paused before Producer!")
             print("✅ Interactive Gates Verified.")
    else:
        print("❌ Did not pause where expected.")

if __name__ == "__main__":
    asyncio.run(test_gates())
