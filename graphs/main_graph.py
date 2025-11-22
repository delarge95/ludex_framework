import structlog
from langgraph.graph import StateGraph, END, START

from core.state_v2 import SpiralState
from graphs.subgraphs.concept_graph import concept_graph
from graphs.subgraphs.production_graph import production_graph
from graphs.subgraphs.polish_graph import polish_graph
from agents.harmonizers.ludonarrative_harmonizer import ludonarrative_harmonizer_node
from agents.harmonizers.technical_reality_check import technical_reality_check_node

from agents.governance.greenlight_gate import greenlight_gate_node
from agents.governance.visual_review_gate import visual_review_gate_node

logger = structlog.get_logger(__name__)

def create_main_graph():
    """
    The Master Graph for the LUDEX 'Spiral' Workflow.
    Orchestrates the transition between Concept, Production, and Polish phases.
    """
    workflow = StateGraph(SpiralState)

    # Add Sub-Graphs as Nodes
    workflow.add_node("concept_phase", concept_graph)
    workflow.add_node("ludonarrative_harmonizer", ludonarrative_harmonizer_node)
    
    # Sprint 19: Decision Gates
    workflow.add_node("greenlight_gate", greenlight_gate_node)
    workflow.add_node("visual_review_gate", visual_review_gate_node)
    
    workflow.add_node("production_phase", production_graph)
    workflow.add_node("technical_reality_check", technical_reality_check_node)
    
    workflow.add_node("polish_phase", polish_graph)

    # Define Edges
    # 1. Start with Concept
    workflow.add_edge(START, "concept_phase")
    
    # 2. Check Harmony
    workflow.add_edge("concept_phase", "ludonarrative_harmonizer")
    
    # 3. Greenlight Gate (Conditional Interrupt)
    workflow.add_edge("ludonarrative_harmonizer", "greenlight_gate")
    
    def route_gate(state: SpiralState):
        if state.get("awaiting_input", False):
            return END
        return "continue"
        
    workflow.add_conditional_edges(
        "greenlight_gate",
        route_gate,
        {
            END: END,
            "continue": "production_phase"
        }
    )
    
    # 4. Production
    # (Edge from greenlight_gate "continue" goes here)
    
    # 5. Visual Review Gate (Conditional Interrupt)
    workflow.add_edge("production_phase", "visual_review_gate")
    
    workflow.add_conditional_edges(
        "visual_review_gate",
        route_gate,
        {
            END: END,
            "continue": "technical_reality_check"
        }
    )
    
    # 6. Check Reality
    # (Edge from visual_review_gate "continue" goes here)
    
    # 7. Polish
    workflow.add_edge("technical_reality_check", "polish_phase")
    
    # 8. End
    workflow.add_edge("polish_phase", END)

    return workflow.compile()

# Export for LangGraph Studio
graph = create_main_graph()
