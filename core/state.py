from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage

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
    monte_carlo_score: int  # 0-100 (Higher is safer)
    budget_probability: str # "80% chance < $X"
    timeline_probability: str # "80% chance < Y months"
    risk_factors: List[Dict[str, Any]]

class ProductionRoadmap(TypedDict):
    estimated_timeline: str
    milestones: List[str]
    asset_count: Dict[str, int]
    risk_analysis: Optional[RiskAnalysis]

class ToolCall(TypedDict):
    """Metadata for a tool execution"""
    tool_name: str
    args: Dict[str, Any]
    timestamp: str
    result_summary: str
    raw_data_ref: Optional[str]

class AgentReasoning(TypedDict):
    """Documented reasoning process for an agent"""
    agent_name: str
    input_state_snapshot: Dict[str, Any]
    tool_calls: List[ToolCall]
    llm_reasoning: str
    sources_cited: List[str]
    output_created: Dict[str, Any]
    timestamp: str
    execution_time_ms: int

class GameDesignState(TypedDict):
    """
    Shared state for the Game Design Automation graph.
    Replaces the old ResearchState.
    """
    # Input
    concept: str
    genre: str
    
    # Agent Outputs
    market_analysis: Optional[MarketReport]
    mechanics: List[Mechanic]
    technical_stack: Optional[TechStack]
    production_plan: Optional[ProductionRoadmap]
    
    # Final Output
    gdd_content: Dict[str, str]  # Sections of the GDD
    
    # Conversation & Meta
    messages: List[BaseMessage]
    current_step: str
    errors: List[str]
    
    # Director / Interactive State
    awaiting_input: bool
    director_questions: List[str]
    production_mode: str  # "prototype" | "full" | "module_market" | "module_mechanics"
    refined_concept: Optional[str]
    
    # Transparency & Reasoning (Sprint 7)
    reasoning_log: List[AgentReasoning]
    tool_execution_log: List[ToolCall]
    
    # Validation & Data Inspector (Sprint 9)
    enable_validation: bool  # User toggle for optional Validator
    validation_warnings: List[Dict[str, Any]]  # Warnings from Validator
    validation_passed: Optional[bool]  # Overall validation result
    validation_confidence: Optional[int]  # 0-100 confidence score
    raw_data_cache: Dict[str, Any]  # Raw API responses (IGDB, Steam, SteamSpy)
    
    # LLM Provider Selection (Sprint 8)
    llm_provider: str  # "github" | "ollama" | "groq" | "anthropic"
    
    # Narrative Design (Sprint 10)
    narrative_structure: Optional[Dict[str, Any]]  # From NarrativeArchitect
    characters: Optional[Dict[str, Any]]  # From CharacterDesigner
    world_lore: Optional[Dict[str, Any]]  # From WorldBuilder
    dialogue_system: Optional[Dict[str, Any]]  # From DialogueSystemDesigner
    
    # Technical Validation (Sprint 10)
    technical_feasibility: Optional[Dict[str, Any]]  # From TechnicalFeasibilityValidator
    
    # UI/UX & Visual Design (Sprint 11)
    ui_ux_design: Optional[Dict[str, Any]]  # From UIUXDesigner
    art_direction: Optional[Dict[str, Any]]  # From ArtDirector
    character_visuals: Optional[Dict[str, Any]]  # From CharacterArtist
    
    # Environment, Animation & Camera (Sprint 12)
    environment_design: Optional[Dict[str, Any]]  # From EnvironmentArtist
    animation_plan: Optional[Dict[str, Any]]  # From AnimationDirector
    camera_systems: Optional[Dict[str, Any]]  # From CameraDesigner
    
    # Audio & Physics (Sprint 13)
    audio_design: Optional[Dict[str, Any]]  # From AudioDirector
    physics_spec: Optional[Dict[str, Any]]  # From PhysicsEngineer
    
    # Level Design & Performance (Sprint 15)
    level_design: Optional[Dict[str, Any]]  # From LevelDesigner
    performance_spec: Optional[Dict[str, Any]]  # From PerformanceAnalyst
    
    # Economy & Networking (Sprint 14 - Conditional)
    economy_spec: Optional[Dict[str, Any]]  # From EconomyBalancer (F2P only)
    networking_spec: Optional[Dict[str, Any]]  # From NetworkArchitect (Multiplayer only)
    
    # QA Planning (Sprint 16)
    qa_plan: Optional[Dict[str, Any]]  # From QAPlanner
