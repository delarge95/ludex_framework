"""
Game Design Agents for LUDEX Framework

LangGraph node functions for the game design automation pipeline.
Each function is an async node that processes GameDesignState.
"""

# Core agents
from agents.game_design.market_analyst import market_analyst_node
from agents.game_design.validator import validator_node
from agents.game_design.mechanics_designer import mechanics_designer_node
from agents.game_design.system_designer import system_designer_node
from agents.game_design.producer import producer_node
from agents.game_design.gdd_writer import gdd_writer_node

# Sprint 10: Narrative & Technical Validation
from agents.game_design.narrative_architect import narrative_architect_node
from agents.game_design.character_designer import character_designer_node
from agents.game_design.world_builder import world_builder_node
from agents.game_design.dialogue_system_designer import dialogue_system_designer_node
from agents.game_design.technical_feasibility_validator import technical_feasibility_validator_node

# Sprint 11: UI/UX & Visual
from agents.game_design.ui_ux_designer import ui_ux_designer_node
from agents.game_design.art_director import art_director_node
from agents.game_design.character_artist import character_artist_node

# Sprint 12: Environment, Animation & Camera
from agents.game_design.environment_artist import environment_artist_node
from agents.game_design.animation_director import animation_director_node
from agents.game_design.camera_designer import camera_designer_node

# Sprint 13: Audio & Physics
from agents.game_design.audio_director import audio_director_node
from agents.game_design.physics_engineer import physics_engineer_node

# Sprint 14: Economy & Networking (Conditional)
from agents.game_design.economy_balancer import economy_balancer_node
from agents.game_design.network_architect import network_architect_node

# Sprint 15: Level Design & Performance
from agents.game_design.level_designer import level_designer_node
from agents.game_design.performance_analyst import performance_analyst_node

# Sprint 16: QA Planning
from agents.game_design.qa_planner import qa_planner_node

__all__ = [
    # Core
    "market_analyst_node",
    "validator_node",
    "mechanics_designer_node",
    "system_designer_node",
    "producer_node",
    "gdd_writer_node",
    # Sprint 10
    "narrative_architect_node",
    "character_designer_node",
    "world_builder_node",
    "dialogue_system_designer_node",
    "technical_feasibility_validator_node",
    # Sprint 11
    "ui_ux_designer_node",
    "art_director_node",
    "character_artist_node",
    # Sprint 12
    "environment_artist_node",
    "animation_director_node",
    "camera_designer_node",
    # Sprint 13
    "audio_director_node",
    "physics_engineer_node",
    # Sprint 14 (Conditional)
    "economy_balancer_node",
    "network_architect_node",
    # Sprint 15
    "level_designer_node",
    "performance_analyst_node",
    # Sprint 16
    "qa_planner_node",
]
