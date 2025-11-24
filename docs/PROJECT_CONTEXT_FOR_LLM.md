# LUDEX Framework - Project Context for NotebookLM

## 1. Project Overview
**LUDEX** is an AI-powered game design automation framework that uses a multi-agent system to generate professional Game Design Documents (GDDs). It simulates a complete game studio with 24 specialized AI agents (e.g., Creative Director, Mechanics Designer, Narrative Architect) working in a collaborative "Spiral" workflow.

**Core Technologies**:
- **LangGraph**: Orchestrates the stateful multi-agent workflow.
- **FastAPI**: Provides the backend API and WebSocket real-time updates.
- **Next.js (React)**: Powers the frontend dashboard.
- **RAG (Retrieval-Augmented Generation)**: Enhances agents with knowledge from engine docs (Unity/Unreal), design patterns, and community forums.

## 2. Key Architecture

### The "Spiral" Workflow
The generation process is divided into three phases, mimicking real-world iterative design:
1.  **Concept Phase**: High-level ideation. Market analysis, core mechanics, and art style definition.
    *   *Agents*: Director, Market Analyst, Mechanics Designer, System Designer, Producer.
    *   *Gate*: "Greenlight" decision (User approval required).
2.  **Production Phase**: Detailed elaboration. Parallel execution of specialized teams.
    *   *Narrative Team*: Narrative Architect, Character Designer, World Builder, Dialogue Designer.
    *   *Visual Team*: Art Director, Character Artist, Environment Artist, Animation Director, Camera Designer, UI/UX Designer.
    *   *Technical Team*: Technical Validator, Audio Director, Physics Engineer, Network Architect, Level Designer, Performance Analyst, Economy Balancer.
    *   *Gate*: "Visual Review" decision.
3.  **Polish Phase**: Refinement and compilation.
    *   *Agents*: QA Planner, GDD Writer.
    *   *Output*: Final Markdown GDD.

### State Management
The system uses a global `GameDesignState` (defined in `core/state.py`) that acts as the "blackboard" for all agents. It contains:
-   `game_concept`: The initial user idea.
-   `mechanics`, `narrative`, `visuals`, `technical`, `world`, `characters`, `levels`, `audio`, `ui`: Structured dictionaries for each domain.
-   `logs`: Chain-of-Thought reasoning logs.
-   `llm_provider`: The active LLM (OpenAI, Anthropic, or Mock).

## 3. Critical Files & Directories

### Backend (`/`)
-   `api/server.py`: Main entry point for the LangGraph application. Defines the graph and WebSocket handlers.
-   `api/main.py`: FastAPI server setup (CORS, middleware).
-   `core/state.py`: Definition of `GameDesignState` and sub-state schemas.
-   `core/mock_llm.py`: Implementation of the Mock LLM for zero-cost testing.
-   `graphs/game_design_graph.py`: The master graph definition wiring all 24 agents together.

### Agents (`agents/`)
-   `agents/game_design/`: Contains the logic for each specific agent (e.g., `mechanics_designer.py`, `narrative_architect.py`).
-   Each agent file typically contains a `node` function that takes `GameDesignState`, calls the LLM, and returns a state update.

### Frontend (`frontend/`)
-   `components/Dashboard.tsx`: The main UI controller. Manages WebSocket connection and layout.
-   `components/AgentStatus.tsx`: Visualizes the status (Idle/Working/Done) of the 24 agents.
-   `components/LogViewer.tsx`: Displays real-time system logs.
-   `components/GDDViewer.tsx`: Renders the generated Markdown GDD.

## 4. Recent Updates (Sprint 23)
-   **Mock LLM**: Added a simulation mode to test the entire pipeline without API costs.
-   **3-Column Layout**: Optimized the Dashboard to show Controls, Agent Status, and Output simultaneously.
-   **Full Roster**: Expanded from 5 to 24 active agents in the UI.

## 5. How to Run
1.  **Backend**: `uvicorn api.main:app --reload` (Port 9090) or `langgraph dev`.
2.  **Frontend**: `npm run dev` (Port 3000).
3.  **Testing**: Select "Mock LLM" in Settings and click "Start Generation".
