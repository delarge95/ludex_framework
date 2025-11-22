# 🎮 ARA Framework - Game Design Automation

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-green.svg)](https://github.com/langchain-ai/langgraph)
[![Unity & Unreal](https://img.shields.io/badge/Engine-Unity%20%7C%20Unreal-black.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Your AI Co-Founder for Game Development.**
## 🏗️ The Virtual Studio (Agents)

ARA simulates a full game development team:

1.  **🕵️ Market Analyst**: Scours Steam and Reddit to find "Blue Oceans" and validate demand.
2.  **⚙️ Mechanics Designer**: Deconstructs game loops and references successful mechanics from similar games.
3.  **📐 System Architect**: Validates technical feasibility, selects the right engine, and warns about performance risks.
4.  **📅 Producer**: Estimates scope, asset lists, and production timelines.
5.  **✍️ GDD Writer**: Synthesizes everything into a professional, cohesive design document.

---

## 🛠️ Tech Stack

*   **Orchestration**: LangGraph (Stateful, cyclic graphs).
*   **Intelligence**: Hybrid routing (Claude 3.5 for Creativity, GPT-4o for Logic).
*   **Data Sources**: IGDB API, RAWG, Steam Storefront.
*   **Knowledge Base**: Local VectorDB (Chroma) with indexed Engine Documentation.
*   **Frontend**: React + Next.js for the Interactive GDD Viewer.

---

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/delarge95/ara-framework.git
cd ara-framework

# 2. Setup Environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure Keys (.env)
# Add OPENAI_API_KEY, ANTHROPIC_API_KEY, IGDB_CLIENT_ID, etc.

# 4. Run the CLI
python -m ara_framework.cli.main new --concept "A cozy metroidvania about baking"
```

---

## 🗺️ Roadmap

*   **Phase 1**: Foundation (Tools & RAG Engine) - *In Progress*
*   **Phase 2**: Agent Implementation (The Studio)
*   **Phase 3**: Interactive Web UI
*   **Phase 4**: Beta Launch

---

## 📄 License

MIT License. Free for Indie Developers.
