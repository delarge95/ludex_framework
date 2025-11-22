import structlog
from typing import Literal
from langgraph.graph import StateGraph, END, START

from core.state import GameDesignState
from agents.game_design.director import director_node
from agents.game_design.market_analyst import market_analyst_node
from agents.game_design.validator import validator_node
from agents.game_design.mechanics_designer import mechanics_designer_node
from agents.game_design.system_designer import system_designer_node
from agents.game_design.producer import producer_node
from agents.game_design.gdd_writer import gdd_writer_node

# Sprint 10: Narrative & Technical Validation agents
from agents.game_design.narrative_architect import narrative_architect_node
from agents.game_design.character_designer import character_designer_node
from agents.game_design.world_builder import world_builder_node
from agents.game_design.dialogue_system_designer import dialogue_system_designer_node
from agents.game_design.technical_feasibility_validator import technical_feasibility_validator_node

# Sprint 11: UI/UX & Visual agents
from agents.game_design.ui_ux_designer import ui_ux_designer_node
from agents.game_design.art_director import art_director_node
from agents.game_design.character_artist import character_artist_node

# Sprint 12: Environment, Animation & Camera agents
from agents.game_design.environment_artist import environment_artist_node
from agents.game_design.animation_director import animation_director_node
from agents.game_design.camera_designer import camera_designer_node

# Sprint 13: Audio & Physics agents
from agents.game_design.audio_director import audio_director_node
from agents.game_design.physics_engineer import physics_engineer_node

# Sprint 15: Level Design & Performance agents
from agents.game_design.level_designer import level_designer_node
from agents.game_design.performance_analyst import performance_analyst_node

# Sprint 14: Economy & Networking agents (Conditional)
from agents.game_design.economy_balancer import economy_balancer_node
from agents.game_design.network_architect import network_architect_node

# Sprint 16: QA Planning
from agents.game_design.qa_planner import qa_planner_node

logger = structlog.get_logger(__name__)

def create_game_design_graph():
    """
    Creates the LangGraph for the Game Design Automation pipeline.
    
    Flow:
    START -> MarketAnalyst -> MechanicsDesigner -> SystemDesigner -> Producer -> GDDWriter -> END
    """
    workflow = StateGraph(GameDesignState)

    # Add nodes
    workflow.add_node("director", director_node)
    workflow.add_node("market_analyst", market_analyst_node)
    workflow.add_node("validator", validator_node)  # Sprint 9 - Optional
    workflow.add_node("mechanics_designer", mechanics_designer_node)
    workflow.add_node("system_designer", system_designer_node)
    workflow.add_node("producer", producer_node)
    
    # Sprint 10: Narrative agents
    workflow.add_node("narrative_architect", narrative_architect_node)
    workflow.add_node("character_designer", character_designer_node)
    workflow.add_node("world_builder", world_builder_node)
    workflow.add_node("dialogue_system_designer", dialogue_system_designer_node)
    workflow.add_node("technical_feasibility_validator", technical_feasibility_validator_node)
    
    # Sprint 11: UI/UX & Visual agents
    workflow.add_node("ui_ux_designer", ui_ux_designer_node)
    workflow.add_node("art_director", art_director_node)
    workflow.add_node("character_artist", character_artist_node)
    
    # Sprint 12: Environment, Animation & Camera agents
    workflow.add_node("environment_artist", environment_artist_node)
    workflow.add_node("animation_director", animation_director_node)
    workflow.add_node("camera_designer", camera_designer_node)
    
    # Sprint 13: Audio & Physics agents
    workflow.add_node("audio_director", audio_director_node)
    workflow.add_node("physics_engineer", physics_engineer_node)
    
    # Sprint 15: Level Design & Performance agents
    workflow.add_node("level_designer", level_designer_node)
    workflow.add_node("performance_analyst", performance_analyst_node)
    
    # Sprint 14: Economy & Networking (Conditional)
    workflow.add_node("economy_balancer", economy_balancer_node)
    workflow.add_node("network_architect", network_architect_node)
    
    # Sprint 16: QA Planning
    workflow.add_node("qa_planner", qa_planner_node)
    
    workflow.add_node("gdd_writer", gdd_writer_node)

    # Define edges
    workflow.add_edge(START, "director")
    
    # Conditional edge for Director
    def route_director(state: GameDesignState):
        if state.get("awaiting_input", False):
            return END
        return "market_analyst"

    workflow.add_conditional_edges(
        "director",
        route_director,
        {
            END: END,
            "market_analyst": "market_analyst"
        }
    )

    # Conditional routing after market_analyst (Sprint 9)
    def route_after_market(state: GameDesignState):
        """Route to validator if enabled, otherwise skip to mechanics_designer."""
        if state.get("enable_validation", False):
            return "validator"
        return "mechanics_designer"
    
    workflow.add_conditional_edges(
        "market_analyst",
        route_after_market,
        {
            "validator": "validator",
            "mechanics_designer": "mechanics_designer"
        }
    )
    
    # Validator always continues to mechanics_designer
    workflow.add_edge("validator", "mechanics_designer")
    workflow.add_edge("mechanics_designer", "system_designer")
    workflow.add_edge("system_designer", "producer")
    
    # Sprint 10: Narrative flow after producer
    workflow.add_edge("producer", "narrative_architect")
    workflow.add_edge("narrative_architect", "character_designer")
    workflow.add_edge("character_designer", "world_builder")
    workflow.add_edge("world_builder", "dialogue_system_designer")
    workflow.add_edge("dialogue_system_designer", "technical_feasibility_validator")
    
    # Sprint 11: Visual flow after technical validation
    workflow.add_edge("technical_feasibility_validator", "ui_ux_designer")
    workflow.add_edge("ui_ux_designer", "art_director")
    workflow.add_edge("art_director", "character_artist")
    
    # Sprint 12: Environment/Animation/Camera flow
    workflow.add_edge("character_artist", "environment_artist")
    workflow.add_edge("environment_artist", "animation_director")
    workflow.add_edge("animation_director", "camera_designer")
    
    # Sprint 13: Audio & Physics flow
    workflow.add_edge("camera_designer", "audio_director")
    workflow.add_edge("audio_director", "physics_engineer")
    
    # Sprint 15: Level Design & Performance flow
    workflow.add_edge("physics_engineer", "level_designer")
    workflow.add_edge("level_designer", "performance_analyst")
    
    # Sprint 14: Conditional Economy/Networking (simple sequential for now)
    # TODO: Add conditional routing based on game type
    workflow.add_edge("performance_analyst", "economy_balancer")
    workflow.add_edge("economy_balancer", "network_architect")
    
    # Sprint 16: QA Planning
    workflow.add_edge("network_architect", "qa_planner")
    workflow.add_edge("qa_planner", "gdd_writer")
    
    workflow.add_edge("gdd_writer", END)

    # Compile with interrupts
    return workflow.compile(
        interrupt_before=["mechanics_designer", "producer"]
    )

# Export graph instance for LangGraph Studio
graph = create_game_design_graph()
