import structlog
from langgraph.graph import StateGraph, END, START

from core.state_v2 import SpiralState
from agents.game_design.technical_feasibility_validator import technical_feasibility_validator_node
from agents.game_design.performance_analyst import performance_analyst_node
from agents.game_design.qa_planner import qa_planner_node
from agents.game_design.gdd_writer import gdd_writer_node

logger = structlog.get_logger(__name__)

def create_polish_graph():
    """
    Creates the Sub-Graph for the 'Polish' phase.
    Focus: Validation, Optimization, Documentation.
    
    Flow:
    START -> TechnicalValidator -> PerformanceAnalyst -> QAPlanner -> GDDWriter -> END
    """
    workflow = StateGraph(SpiralState)

    # Add nodes
    workflow.add_node("technical_feasibility_validator", technical_feasibility_validator_node)
    workflow.add_node("performance_analyst", performance_analyst_node)
    workflow.add_node("qa_planner", qa_planner_node)
    workflow.add_node("gdd_writer", gdd_writer_node)

    # Define edges
    workflow.add_edge(START, "technical_feasibility_validator")
    workflow.add_edge("technical_feasibility_validator", "performance_analyst")
    workflow.add_edge("performance_analyst", "qa_planner")
    workflow.add_edge("qa_planner", "gdd_writer")
    workflow.add_edge("gdd_writer", END)

    return workflow.compile()

polish_graph = create_polish_graph()
