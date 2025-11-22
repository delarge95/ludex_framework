import structlog
from typing import Literal
from langgraph.graph import StateGraph, END, START

from core.state_v2 import SpiralState, CoreState
from agents.game_design.director import director_node
from agents.game_design.market_analyst import market_analyst_node
from agents.game_design.narrative_architect import narrative_architect_node
from agents.game_design.art_director import art_director_node
from agents.game_design.mechanics_designer import mechanics_designer_node

logger = structlog.get_logger(__name__)

def create_concept_graph():
    """
    Creates the Sub-Graph for the 'Concept' phase.
    Focus: Ideation, Market Fit, Core Pillars.
    
    Flow:
    START -> Director -> MarketAnalyst -> NarrativeArchitect -> ArtDirector -> MechanicsDesigner -> END
    """
    # We use SpiralState as the schema, but agents will primarily read/write to 'core' and 'working'
    workflow = StateGraph(SpiralState)

    # Add nodes
    workflow.add_node("director", director_node)
    workflow.add_node("market_analyst", market_analyst_node)
    workflow.add_node("narrative_architect", narrative_architect_node)
    workflow.add_node("art_director", art_director_node)
    workflow.add_node("mechanics_designer", mechanics_designer_node)

    # Define edges
    workflow.add_edge(START, "director")
    
    # Conditional edge for Director (User Input)
    def route_director(state: SpiralState):
        if state.get("awaiting_input", False):
            return END # Wait for user
        return "market_analyst"

    workflow.add_conditional_edges(
        "director",
        route_director,
        {
            END: END,
            "market_analyst": "market_analyst"
        }
    )
    
    # Linear flow for Concept Phase
    workflow.add_edge("market_analyst", "narrative_architect")
    workflow.add_edge("narrative_architect", "art_director")
    workflow.add_edge("art_director", "mechanics_designer")
    workflow.add_edge("mechanics_designer", END)

    return workflow.compile()

concept_graph = create_concept_graph()
