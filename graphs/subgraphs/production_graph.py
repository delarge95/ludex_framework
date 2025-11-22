import structlog
from langgraph.graph import StateGraph, END, START

from core.state_v2 import SpiralState
from agents.game_design.system_designer import system_designer_node
from agents.game_design.level_designer import level_designer_node
from agents.game_design.environment_artist import environment_artist_node
from agents.game_design.physics_engineer import physics_engineer_node
from agents.game_design.character_designer import character_designer_node

logger = structlog.get_logger(__name__)

def create_production_graph():
    """
    Creates the Sub-Graph for the 'Production' phase.
    Focus: Implementation, Systems, Assets.
    
    Flow:
    START -> SystemDesigner -> CharacterDesigner -> EnvironmentArtist -> PhysicsEngineer -> LevelDesigner -> END
    """
    workflow = StateGraph(SpiralState)

    # Add nodes
    workflow.add_node("system_designer", system_designer_node)
    workflow.add_node("character_designer", character_designer_node)
    workflow.add_node("environment_artist", environment_artist_node)
    workflow.add_node("physics_engineer", physics_engineer_node)
    workflow.add_node("level_designer", level_designer_node)

    # Define edges
    workflow.add_edge(START, "system_designer")
    workflow.add_edge("system_designer", "character_designer")
    workflow.add_edge("character_designer", "environment_artist")
    workflow.add_edge("environment_artist", "physics_engineer")
    workflow.add_edge("physics_engineer", "level_designer")
    workflow.add_edge("level_designer", END)

    return workflow.compile()

production_graph = create_production_graph()
