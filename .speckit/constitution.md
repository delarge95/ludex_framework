# 📜 ARA Framework - Project Constitution

**Version**: 3.0.0 (Pivot)
**Created**: 2025-11-20
**Status**: Active - Game Design Automation Pivot
**Strategy**: Hybrid (New Domain Core + Reused Infrastructure)

---

## 🎯 Project Vision

**Mission Statement**:
Build the ultimate **Game Design Automation Copilot** that empowers indie developers and studios to create professional, technically validated, and market-aware Game Design Documents (GDDs).

**Core Value Proposition**:
*   **Zero Hallucinations**: Every technical claim is backed by engine documentation (Unity/Unreal). Every market claim is backed by real data (Steam/IGDB).
*   **Living Documentation**: GDDs are not static PDFs, but interactive databases that evolve with the project.
*   **Risk Reduction**: Identify technical bottlenecks and market gaps *before* writing a line of code.

---

## 🏛️ Architectural Principles

### 1. **Trust & Verification (Zero Hallucinations)**
*   **RAG-First**: No technical advice is given without retrieving context from official documentation.
*   **Citation Mandatory**: Every assertion must link to a source (e.g., `[Source: Unity Docs]`, `[Source: SteamDB]`).
*   **Market Grounding**: Game concepts are validated against real-time market data.

### 2. **Interactive "Copilot" Workflow**
*   **Human-in-the-Loop**: The AI suggests, the Human decides. Critical checkpoints (Concept, Mechanics, Tech Stack) require user approval.
*   **Bidirectional Flow**: User feedback refines the context for subsequent agents.

### 3. **Hybrid Infrastructure Strategy**
*   **Reuse**: Leverage existing LangGraph orchestration, LLM routing (AdaptiveRouter), and Scraping tools.
*   **Refactor**: Change the "Brain" (Prompts) and "Eyes" (Tools) to focus on Game Design.

---

## 🎭 Agent Design Philosophy (The Game Studio)

### Agent Hierarchy

1.  **MarketAnalyst (The Scout)**
    *   *Role*: Identifies market gaps, analyzes Steam trends, and defines target audience.
    *   *Tools*: IGDB API, Steam Scraper, Reddit Trends.
2.  **MechanicsDesigner (The Designer)**
    *   *Role*: Deconstructs game loops, defines mechanics, and references similar games.
    *   *Tools*: Game Mechanics Wiki RAG, Youtube Analysis.
3.  **SystemDesigner (The Architect)**
    *   *Role*: Selects the engine (Unity/Unreal), designs systems, and validates technical feasibility.
    *   *Tools*: Unity/Unreal Docs RAG, Github Search.
4.  **Producer (The Manager)**
    *   *Role*: Estimates scope, creates asset lists, and defines the production roadmap.
    *   *Tools*: Budget Calculators, Asset Store Scrapers.
5.  **GDDWriter (The Scribe)**
    *   *Role*: Synthesizes all outputs into a cohesive, professional GDD.
    *   *Tools*: Markdown/Notion Generators.

---

## 🔒 Non-Negotiables

### Quality Standards
*   **No Generic Advice**: "Make it fun" is banned. Use specific terms like "Feedback Loops", "Juice", "Coyote Time".
*   **Technical Accuracy**: Code snippets must be valid for the specified engine version.

### Security & Ethics
*   **Data Privacy**: User ideas are proprietary. No training on user inputs without consent.
*   **Scraping Ethics**: Respect `robots.txt` and API rate limits.

---

## 📊 Success Metrics

*   **User Trust**: Users accept >80% of AI suggestions without major edits.
*   **Technical Validity**: Generated code/architecture snippets compile/work in >90% of cases.
*   **Market Relevance**: Identified "similar games" are actually relevant in >95% of cases.
