from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langchain_core.messages import BaseMessage
import operator

# --- Shared Types ---

class MarketReport(TypedDict):
    target_audience: str
    similar_games: List[str]
    market_gap: str
    steam_trends: Dict[str, Any]

class Mechanic(TypedDict):
    name: str
    description: str
    reference_game: str
    technical_complexity: str

class TechStack(TypedDict):
    engine: str
    language: str
    critical_packages: List[str]
    risks: List[str]

class RiskAnalysis(TypedDict):
    monte_carlo_score: int
    budget_probability: str
    timeline_probability: str
    risk_factors: List[Dict[str, Any]]

class ProductionRoadmap(TypedDict):
    estimated_timeline: str
    milestones: List[str]
    asset_count: Dict[str, int]
    risk_analysis: Optional[RiskAnalysis]

class ToolCall(TypedDict):
    tool_name: str
    args: Dict[str, Any]
    timestamp: str
    result_summary: str
    raw_data_ref: Optional[str]

class AgentReasoning(TypedDict):
    agent_name: str
    input_state_snapshot: Dict[str, Any]
    tool_calls: List[ToolCall]
    llm_reasoning: str
    sources_cited: List[str]
    output_created: Dict[str, Any]
    timestamp: str
    execution_time_ms: int

# --- New State Architecture (Sprint 18) ---

class CoreState(TypedDict):
    """
    Immutable constraints and foundational decisions.
    Once set in the 'Concept' phase, these rarely change without a major pivot.
    """
    # Initial Input
    concept: str
    genre: str
    
    # Market & Direction
    market_analysis: Optional[MarketReport]
    art_direction_pillars: List[str]  # High-level visual pillars
    narrative_theme: str              # Core theme (e.g. "Redemption")
    design_pillars: List[str]         # Core gameplay pillars (e.g. "Fast-paced combat")
    
    # Technical Constraints
    target_platform: List[str]        # PC, Console, Mobile
    engine_choice: str                # Unity, Unreal, Godot

class WorkingState(TypedDict):
    """
    Mutable artifacts that evolve during the spiral loop.
    Agents read CoreState but write to WorkingState.
    """
    # Mechanics & Systems
    mechanics: List[Mechanic]
    systems: Dict[str, Any]           # Detailed system specs
    
    # Narrative
    narrative_structure: Optional[Dict[str, Any]]
    characters: Dict[str, Any]
    world_lore: Dict[str, Any]
    dialogue_system: Optional[Dict[str, Any]]
    
    # Visuals
    art_style_guide: Optional[Dict[str, Any]]
    character_visuals: Dict[str, Any]
    environment_design: Dict[str, Any]
    ui_ux_design: Optional[Dict[str, Any]]
    animation_plan: Optional[Dict[str, Any]]
    
    # Technical & Audio
    technical_stack: Optional[TechStack]
    physics_spec: Optional[Dict[str, Any]]
    audio_design: Optional[Dict[str, Any]]
    
    # Production
    production_plan: Optional[ProductionRoadmap]
    level_design: Dict[str, Any]
    performance_spec: Optional[Dict[str, Any]]
    qa_plan: Optional[Dict[str, Any]]
    
    # Validation
    validation_warnings: List[Dict[str, Any]]
    technical_feasibility: Optional[Dict[str, Any]]

class DecisionOption(TypedDict):
    id: str
    label: str
    description: str
    risk_score: int  # 0-100
    projected_impact: str

class Decision(TypedDict):
    id: str
    title: str
    description: str
    options: List[DecisionOption]
    selected_option_id: Optional[str]
    timestamp: str

class SpiralState(TypedDict):
    """
    The top-level state that wraps Core and Working states.
    Manages the iteration loop.
    """
    # Sub-States
    core: CoreState
    working: WorkingState
    
    # Meta-State
    messages: Annotated[List[BaseMessage], operator.add]
    current_phase: str  # "concept" | "production" | "polish"
    iteration_count: int
    max_iterations: int
    
    # Transparency
    reasoning_log: Annotated[List[AgentReasoning], operator.add]
    tool_execution_log: Annotated[List[ToolCall], operator.add]
    
    # Director / Interactive
    awaiting_input: bool
    director_questions: List[str]
    pending_decision: Optional[Decision]  # Sprint 19: Decision Gate
    
    # Settings
    llm_provider: str
    enable_validation: bool
