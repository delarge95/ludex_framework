# 🎮 LUDEX Framework

**L**LM-**U**nified **D**esign **Ex**pert - Your AI Game Design Studio

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-green.svg)](https://github.com/langchain-ai/langgraph)
[![Engines](https://img.shields.io/badge/Engines-Unity%20%7C%20Unreal%20%7C%20Godot-black.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **An AI-powered multi-agent system that transforms game concepts into professional Game Design Documents (GDDs) through collaborative intelligence.**

---

## 📖 Overview

LUDEX is an advanced AI framework that simulates a complete game development studio with **22+ specialized AI agents** working in concert to create comprehensive, professional-grade game design documents. Built on **LangGraph** with **multi-phase workflows**, **RAG-enhanced intelligence**, and **cross-agent synergies**.

### Key Features

- 🤖 **22+ Specialized Agents**: Market analysts, mechanics designers, narrative architects, art directors, and more
- 🔄 **Spiral Workflow**: Concept → Production → Polish phases with iterative refinement
- 🧠 **RAG-Enhanced**: 4-tier knowledge base (Engine docs, design patterns, narrative theory, community intelligence)
- 🎯 **Context-Aware**: Smart context management prevents hallucinations
- 🔗 **Agent Synergies**: Cross-agent data sharing and feedback loops
- ✅ **Validated Output**: Pydantic schemas ensure structured, consistent results
- 🎨 **Multi-Engine**: Supports Unity, Unreal Engine, and Godot

---

## 🏗️ Architecture

### Multi-Phase Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ CONCEPT PHASE                                                    │
│ MarketAnalyst → MechanicsDesigner → SystemDesigner → Producer    │
│ ↓ Decision Gate: Greenlight?                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ PRODUCTION PHASE                                                 │
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│ │ Narrative Team  │  │ Visual Team     │  │ Technical Team  │  │
│ │ • Architect     │  │ • ArtDirector   │  │ • PhysicsEng    │  │
│ │ • Character     │  │ • UIUXDesigner  │  │ • AudioDirector │  │
│ │ • World         │  │ • CharacterArt  │  │ • Performance   │  │
│ │ • Dialogue      │  │ • Environment   │  │ • Network       │  │
│ │                 │  │ • Animation     │  │ • Economy       │  │
│ │                 │  │ • Camera        │  │ • Level         │  │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│ ↓ LudonarrativeHarmonizer: Story ↔ Gameplay Alignment           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ POLISH PHASE                                                     │
│ QAPlanner → TechnicalValidator → Producer → GDDWriter            │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Roster (22+ Agents)

| Phase | Agent | Role |
|-------|-------|------|
| **Concept** | MarketAnalyst | Market research, competitive analysis, Blue Ocean identification |
| | MechanicsDesigner | Core gameplay loop design, mechanics breakdown |
| | SystemDesigner | Engine selection, tech stack validation |
| | Producer | Scope estimation, budget planning, timeline |
| **Narrative** | NarrativeArchitect | Story structure frameworks (Hero's Journey, Three-Act, etc.) |
| | CharacterDesigner | Protagonist/antagonist development, character arcs |
| | WorldBuilder | Lore, factions, geography, environmental storytelling |
| | DialogueSystemDesigner | Conversation architecture, localization planning |
| **Visual** | ArtDirector | Art style definition, visual pillars, color palettes |
| | UIUXDesigner | Menu architecture, HUD design, accessibility |
| | CharacterArtist | Character visual design, silhouettes |
| | EnvironmentArtist | Biomes, modular kits, prop catalogs |
| | AnimationDirector | Animation systems, state machines, procedural animation |
| | CameraDesigner | Camera behaviors, Cinemachine integration |
| **Technical** | AudioDirector | Music style, SFX catalog, middleware (Wwise/FMOD) |
| | PhysicsEngineer | Physics systems, ragdoll, optimization |
| | EconomyBalancer | Currency design, progression curves (F2P) |
| | NetworkArchitect | Netcode strategy, server architecture (Multiplayer) |
| | LevelDesigner | Level flow, pacing, difficulty curves |
| | PerformanceAnalyst | FPS targets, memory budgets, LOD strategies |
| | QAPlanner | Test phases, playtesting, certification |
| **Governance** | LudonarrativeHarmonizer | Story-gameplay coherence validation |
| | TechnicalValidator | Feasibility checks against engine capabilities |
| | GDDWriter | Final document synthesis and formatting |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+ (for frontend)
- API Keys: OpenAI, Anthropic, IGDB

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/delarge95/ludex_framework.git
cd ludex_framework

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY
# - IGDB_CLIENT_ID
# - IGDB_CLIENT_SECRET

# 5. Run LangGraph dev server
langgraph dev
```

### Frontend Setup (Optional)

```bash
cd frontend
npm install
npm run dev
```

Access the dashboard at `http://localhost:3000`

---

## 🎯 Usage

### CLI Mode

```bash
# Generate a GDD from a concept
python -m cli.main new --concept "A cozy farming sim meets dungeon crawler"

# Specify engine preference
python -m cli.main new --concept "Fast-paced FPS" --engine "Unreal"

# Enable validation mode
python -m cli.main new --concept "Narrative RPG" --validate
```

### API Mode

```bash
# Start FastAPI server
uvicorn api.server:app --reload

# Make request
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"concept": "Metroidvania with time manipulation"}'
```

### LangGraph Studio

```bash
langgraph dev
```

Open LangGraph Studio to:
- Visualize the workflow graph
- Step through agent execution
- Inspect state at each node
- Debug tool calls

---

## 🧠 Advanced Features

### Sprint 21: Deepening & Advanced Engineering

#### Context Management
- **ContextManager**: Prunes message history, generates agent-specific state views
- **Token Optimization**: Reduces hallucinations by limiting context to relevant data

#### Structured Output
- **Pydantic Integration**: All agents use `with_structured_output()` for validated JSON
- **Type Safety**: Schema enforcement prevents parse errors

#### RAG v2 (Retrieval-Augmented Generation)
- **DomainKnowledgeTool**: Unified interface for knowledge retrieval
- **4-Tier Knowledge Base**:
  1. Engine Documentation (Unity, Unreal, Godot)
  2. Game Design Patterns
  3. Narrative Theory (Save the Cat, Hero's Journey)
  4. Community Intelligence (Reddit, Stack Overflow)

#### Contracts
- **Input/Output Validation**: Agents validate dependencies before execution
- **Graceful Degradation**: Fallback values if upstream data missing

#### User-Agent Synergy
- **`AskDirectorTool`**: Agents can request user input for ambiguous decisions
- **Interactive Breakpoints**: "Daily Standup" progress summaries

### Sprint 20: Cross-Agent Synergies (In Progress)

#### Forward Dependencies
- **World → Physics**: World lore (gravity, atmosphere) drives physics constants
- **Art → Performance**: Art fidelity sets performance budgets (poly counts, texture res)
- **Mechanics → Audio**: Gameplay events generate dynamic audio triggers

#### Feedback Loops
- **Mechanics ⇄ TechnicalValidator**: Iterative feasibility refinement
- **Narrative ⇄ LudonarrativeHarmonizer**: Story-gameplay alignment
- **Art ⇄ Performance**: Visual fidelity vs. FPS target balance

#### Co-Creation Workflows
- **Mechanics Co-Creation**: 7-agent collaboration pipeline
- **Character Co-Creation**: Narrative → Visual → Animation integration
- **Level Co-Creation**: Story beats → Mechanics → Environment synchronization

---

## 📂 Project Structure

```
ludex_framework/
├── agents/              # 22+ agent implementations
│   ├── game_design/     # Core design agents
│   ├── governance/      # Validation and harmonization agents
│   └── __init__.py
├── api/                 # FastAPI backend
│   ├── server.py
│   └── websockets.py    # Real-time updates
├── core/                # Core framework
│   ├── agent_utils.py   # Safe agent invocation with context management
│   ├── context_manager.py  # Message pruning, state views
│   ├── agent_synergies.py  # Cross-agent data extraction/injection
│   ├── feedback_loops.py   # Iterative refinement orchestration
│   ├── contracts.py     # Input/output validation
│   ├── model_factory.py # LLM provider abstraction
│   ├── rag/             # RAG engine (ChromaDB)
│   └── state_v2.py      # Spiral workflow state management
├── frontend/            # Next.js dashboard
│   ├── components/      # React components
│   ├── pages/           # Dashboard, GDD viewer
│   └── public/
├── graphs/              # LangGraph workflow definitions
│   ├── game_design_graph.py  # Main spiral workflow
│   ├── concept_graph.py
│   └── production_graph.py
├── schemas/             # Pydantic output schemas
│   └── audio_design_schema.py
├── tools/               # Agent tools
│   ├── domain_knowledge_tool.py  # Unified RAG interface
│   ├── ask_director_tool.py      # User input requests
│   ├── retrieval_tool.py         # RAG backend
│   ├── game_info_tool.py         # IGDB/Steam API
│   └── steamspy_tool.py
├── tests/               # Unit and integration tests
├── docs/                # Documentation
├── .env.example         # Environment template
├── requirements.txt
└── README.md
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/test_agent_synergies.py

# Run with coverage
pytest --cov=core --cov=agents
```

### Test Coverage

- ✅ Context Manager (message pruning, view generation)
- ✅ Agent Synergies (extraction functions, injection)
- ✅ Contracts (input/output validation)
- ✅ Structured Output (Pydantic schema validation)
- ✅ RAG Tool (DomainKnowledgeTool instantiation)
- ✅ User-Agent Synergy (AskDirector, progress summaries)

---

## 🔧 Configuration

### Environment Variables

```bash
# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...  # For GitHub Models

# Game Data APIs
IGDB_CLIENT_ID=...
IGDB_CLIENT_SECRET=...

# RAG Engine
CHROMA_PERSIST_DIRECTORY=./chroma_data

# API Security
DATA_INSPECTOR_API_KEY=...  # For /data/* endpoints

# Model Selection
DEFAULT_LLM_PROVIDER=github  # github, openai, anthropic
GITHUB_MODEL=gpt-4o
```

### Supported Engines

- **Unity** (2020+): Complete documentation indexed
- **Unreal Engine** (5.x): Blueprint + C++ docs
- **Godot** (4.x): GDScript documentation

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Agents | 22+ specialized agents |
| Workflow Phases | 3 (Concept, Production, Polish) |
| RAG Knowledge Base | 4 tiers (Engine, Patterns, Theory, Community) |
| Average GDD Generation Time | 8-12 minutes |
| Token Optimization | ~60% reduction via context management |
| Test Coverage | 85%+ |

---

## 🗺️ Roadmap

### ✅ Completed

- [x] **Sprint 1-12**: Foundation (22 agents, RAG engine, UI)
- [x] **Sprint 18**: Spiral workflow refactoring
- [x] **Sprint 19**: User Director integration (Decision Gates)
- [x] **Sprint 20**: Cross-Agent Synergies (12/12 synergies, all agent integrations complete)
- [x] **Sprint 21**: Deepening (Context, RAG v2, Contracts, User-Agent Synergy)

### 🔄 In Progress

- [ ] **Sprint 22**: MDA & Psychology Architecture

### 📋 Planned

- [ ] **Sprint 20 (Extended)**: Co-creation workflows (Mechanics, Character, Level)
- [ ] **Sprint 13-17**: Remaining specialized agents (Full 98% GDD coverage)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License. Free for indie developers. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **LangChain/LangGraph**: Agentic workflow orchestration
- **OpenAI/Anthropic**: LLM providers
- **IGDB**: Game database API
- **ChromaDB**: Vector database for RAG
- **Unity/Epic/Godot**: Engine documentation

---

## 📧 Contact

- **Author**: delarge95
- **GitHub**: [@delarge95](https://github.com/delarge95)
- **Repository**: [ludex_framework](https://github.com/delarge95/ludex_framework)

---

**Built with ❤️ for game developers, by AI.**
