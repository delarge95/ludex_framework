# 🔧 ARA Framework - Technical Specifications

**Version**: 3.0.0 (Pivot)
**Status**: Specification for Game Design Automation Pivot

    def get_steam_trends(self, tag: str) -> TrendData: ...
```

### 2. RAG Engine (`core/rag/`) - NEW

**Purpose**: Ground technical advice in official documentation to prevent hallucinations.

**Components**:
*   **DocIngestor**: Scripts to scrape and index Unity 6 / Unreal 5 docs.
*   **VectorDB**: ChromaDB or Supabase pgvector for storing embeddings.
*   **Retriever**: Semantic search to find relevant docs based on user query.

**Workflow**:
1.  Agent asks: "How to implement fog?"
2.  Retriever finds: "Volumetric Fog in HDRP (Unity Docs)"
3.  LLM generates answer *using* the retrieved context.

### 3. AdaptiveRouter (`core/router/`) - REUSED (Hybrid)

**Purpose**: Route tasks to the best model (Creative vs Technical).

**Configuration**:
*   **Creative Tasks** (Narrative, Mechanics): Route to **Claude 3.5 Sonnet**.
*   **Technical Tasks** (Architecture, Code): Route to **GPT-4o** or **DeepSeek Coder**.
*   **Simple Tasks** (Formatting): Route to **Haiku** or **Flash**.

### 4. GDD Generator (`agents/gdd_writer.py`) - REFACTORED

**Purpose**: Assemble the final GDD.

**Output Formats**:
*   **Markdown**: Standard format for git versioning.
*   **JSON**: For the interactive Web Viewer.
*   **Notion**: (Optional) Direct export to Notion.

---

## 🔄 Data Structures

### `GameDesignState` (Replaces `ResearchState`)

```python
class GameDesignState(TypedDict):
    concept: str
    genre: str
    target_audience: str
    market_analysis: MarketReport
    mechanics: List[Mechanic]
    technical_stack: TechStack
    production_plan: ProductionRoadmap
    gdd_content: Dict[str, str]
    messages: List[BaseMessage]
```

---

## 🧪 Testing Strategy

*   **Hallucination Test**: Ask for non-existent API methods. System should say "I don't know" or cite correct alternatives.
*   **Market Validation**: Verify that "Similar Games" returned by the tool actually exist and match the genre.
*   **End-to-End**: Generate a full GDD for a known genre (e.g., "2D Platformer") and review for coherence.
# 🔧 ARA Framework - Technical Specifications

**Version**: 3.2.0 (Agent Architecture Expansion)
**Status**: Specification for Game Design Automation with Comprehensive Agent Coverage
**Last Updated**: Nov 21, 2025

---

## Core Architecture Components

### 1. RAG Engine (`core/rag/`)
**Purpose**: Ground technical and narrative advice in official documentation to prevent hallucinations.

**Components**:
- **DocIngestor**: Scripts to scrape and index Unity 6 / Unreal 5 / Godot docs + narrative theory books
- **VectorDB**: ChromaDB for storing embeddings
- **Retriever**: Semantic search to find relevant docs based on user query

**Expanded Coverage** (Sprint 10+):
- Unity/Unreal/Godot complete documentation
- Narrative theory (Save the Cat, Story, Writer's Journey)
- Game postmortems (Hades, Last of Us, Disco Elysium)
- UX best practices (Don't Make Me Think)
- Audio design resources

### 2. Multi-Provider LLM Support (`core/model_factory.py`)
**Purpose**: Allow flexible LLM provider selection.

**Supported Providers**:
- GitHub Models (gpt-4o, gpt-4o-mini, Llama-3.3-70B, Phi-4)
- Ollama (local models: mistral:7b, llama3:8b, qwen2.5:7b)
- Groq (llama3-70b-8192, mixtral-8x7b-32768)
- Anthropic (claude-3-5-sonnet, claude-3-opus)

### 3. Agent Specialization Framework

#### Existing Agents (v3.1)
- **Director**: Concept clarification router
- **MarketAnalyst**: Market research, competitive analysis, monetization
- **MechanicsDesigner**: Core loop design, genre-specific mechanics
- **SystemDesigner**: Technical architecture (to be upgraded to TechnicalArchitect)
- **Producer**: Scoping, budgeting, risk analysis (Monte Carlo)
- **GDDWriter**: Document synthesis

#### New Specialized Agents (Sprints 10-17)

**Narrative Domain (Sprint 10)**:
- `NarrativeArchitect`: Story structure application (Hero's Journey, Three-Act)
- `CharacterDesigner`: Character arcs, protagonist/antagonist design
- `WorldBuilder`: Lore, factions, geography, environmental storytelling
- `DialogueSystemDesigner`: Conversation architecture, localization

**Technical Validation (Sprint 10)**:
- `TechnicalFeasibilityValidator`: Validate mechanics against engine docs, forum intelligence

**Visual Design (Sprints 11-12)**:
- `ArtDirector`: Art style definition, visual pillars
- `CharacterArtist`: Character visual design, silhouettes
- `EnvironmentArtist`: Biome design, modular kits
- `AnimationDirector`: Animation catalog, state machines
- `CameraDesigner`: Camera systems (third-person, first-person, cinematic)

**UI/UX (Sprint 11)**:
- `UIUXDesigner`: Menu architecture, HUD, onboarding, accessibility

**Audio (Sprint 13)**:
- `AudioDirector`: Music style, SFX catalog, VO planning

**Physics (Sprint 13)**:
- `PhysicsEngineer`: Physics style, gameplay physics, optimization

**Economy (Sprint 14, conditional)**:
- `EconomyBalancer`: Currency design, progression curves (F2P only)

**Networking (Sprint 14, conditional)**:
- `NetworkArchitect`: Netcode strategy, server infrastructure (multiplayer only)

**Level Design (Sprint 15)**:
- `LevelDesigner`: Level flow, pacing, environmental storytelling

**Performance (Sprint 15)**:
- `PerformanceAnalyst`: FPS targets, memory budgets, LOD strategies

**QA (Sprint 16)**:
- `QAPlanner`: Test phases, playtesting strategy

---

## Data Structures

### `GameDesignState` (Comprehensive)

```python
class GameDesignState(TypedDict):
    # Core Concept
    concept: str
    genre: str
    target_audience: str
    
    # Market & Business
    market_analysis: MarketReport
    monetization_strategy: MonetizationPlan
    
    # Gameplay
    mechanics: List[Mechanic]
    physics_spec: PhysicsSpec
    
    # Narrative (NEW - Sprint 10)
    narrative_structure: NarrativeFramework
    characters: CharacterCatalog
    world_lore: WorldBuildingDoc
    dialogue_system: DialogueSystemSpec
    
    # Visual Design (NEW - Sprints 11-12)
    art_direction: ArtStyleGuide
    character_visuals: CharacterArtSpec
    environment_design: EnvironmentArtSpec
    animation_plan: AnimationCatalog
    camera_systems: CameraSpec
    
    # UI/UX (NEW - Sprint 11)
    ui_ux_design: UIUXSpec
    
    # Audio (NEW - Sprint 13)
    audio_design: AudioPlan
    
    # Technical
    technical_stack: TechStack
    feasibility_validation: FeasibilityReport
    performance_budgets: PerformanceBudgets
    
    # Level Design (NEW - Sprint 15)
    level_design: LevelDesignDoc
    
    # Production
    production_plan: ProductionRoadmap
    qa_plan: QAPlan
    
    # Optional (conditional)
    economy_design: Optional[EconomySpec]  # F2P only
    network_architecture: Optional[NetworkSpec]  # Multiplayer only
    
    # Validation
    enable_validation: bool
    validation_warnings: List[ValidationWarning]
    raw_data_cache: Dict[str, Any]
    
    # Meta
    gdd_content: Dict[str, str]
    reasoning_log: List[AgentReasoning]
    messages: List[BaseMessage]
```

---

## Agent Output Schemas

### NarrativeArchitect Output
```json
{
  "narrative_framework": "Hero's Journey / Three-Act / Kishōtenketsu",
  "act_structure": [
    {"act": 1, "title": "Setup", "gameplay_milestone": "Tutorial", "duration": "2 hours"}
  ],
  "themes": ["Primary: Redemption", "Secondary: Family"],
  "tone": "Dark & Gritty / Whimsical / Epic"
}
```

### TechnicalFeasibilityValidator Output
```json
{
  "feasibility_score": 85,
  "validated_mechanics": [
    {
      "mechanic": "AI Pathfinding",
      "engine_support": "Native (Unity NavMesh)",
      "complexity": "MEDIUM",
      "risks": ["Performance issues with 100+ agents"]
    }
  ],
  "red_flags": []
}
```

### ArtDirector Output
```json
{
  "art_style": "Stylized realism / Pixel art / Cel-shaded",
  "visual_pillars": ["Dark & Gothic", "Detailed Environments"],
  "color_palette": {
    "primary": ["#1A1A2E", "#16213E"],
    "accent": ["#E94560", "#F4A261"]
  }
}
```

---

## Tool Integration

### External APIs
- **IGDB**: Game market data
- **Steam Web API**: Pricing, tags, reviews
- **SteamSpy API**: Player count estimates, playtime data
- **Unity Asset Store API**: Asset availability checking
- **Forum Scraping**: Unity Forum, Reddit r/Unity3D, Stack Overflow

### RAG Tools
- **RetrievalTool**: Semantic search against indexed documentation
- **NarrativeTheoryTool**: Query narrative frameworks
- **EngineFeasibilityTool**: Validate against engine documentation

---

## Testing Strategy

### Hallucination Prevention
- **Narrative Test**: All story recommendations cite narrative theory source
- **Technical Test**: All mechanics validated against engine docs or flagged as "experimental"
- **Market Test**: All "similar games" actually exist and match genre

### End-to-End Validation
- Generate full GDD for known genre (e.g., "2D Metroidvania")
- Review for:
  - Narrative coherence (story aligns with mechanics)
  - Technical feasibility (all features implementable)
  - Visual consistency (art style uniform across sections)
  - Budget realism (estimates match industry standards)

---

## Performance Targets

- **RAG Query Latency**: <2 seconds for semantic search
- **Agent Response Time**: <30 seconds per agent (excluding tool calls)
- **Full GDD Generation**: <10 minutes (with all 20+ agents)
- **Memory Usage**: <4GB for complete RAG index

---

## Deployment Architecture

### Backend
- FastAPI server (port 9090)
- LangGraph workflow orchestration
- ChromaDB vector store
- WebSocket for real-time updates

### Frontend
- Next.js dashboard (port 3000)
- Settings Modal for provider configuration
- DataInspector for raw data viewing
- AgentActivityStream for transparency

### Data Storage
- ChromaDB: Vector embeddings
- Local cache: Raw API responses (24h TTL)
- Session state: In-memory (LangGraph checkpoints)