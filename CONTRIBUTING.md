# Project Structure

This document describes the organized folder structure of the LUDEX Framework.

## 📁 Root Directory

The root contains only essential project files:

- `README.md` - Main project documentation
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template
- `langgraph.json` - LangGraph configuration
- `pyproject.toml` - Python project metadata
- `setup.py` - Package installation script
- `pytest.ini` - Test configuration

## 📂 Main Directories

### `/agents/`
All 22+ AI agent implementations organized by phase:
- `game_design/` - Core design agents (Market, Mechanics, Narrative, Art, etc.)
- `governance/` - Validation and harmonization agents

### `/api/`
FastAPI backend:
- `server.py` - Main API server
- `websockets.py` - Real-time updates

### `/core/`
Framework core:
- `agent_utils.py` - Safe agent invocation
- `context_manager.py` - Message pruning, state views
- `agent_synergies.py` - Cross-agent data flow
- `feedback_loops.py` - Iterative refinement
- `contracts.py` - Input/output validation
- `rag/` - RAG engine (ChromaDB)

### `/frontend/`
Next.js dashboard:
- `components/` - React components
- `pages/` - Dashboard pages

### `/graphs/`
LangGraph workflow definitions:
- `game_design_graph.py` - Main spiral workflow
- `concept_graph.py`, `production_graph.py`, etc.

### `/schemas/`
Pydantic output schemas for structured validation

### `/tools/`
Agent tools:
- `domain_knowledge_tool.py` - Unified RAG
- `game_info_tool.py` - IGDB/Steam API
- `ask_director_tool.py` - User input requests

### `/tests/`
Unit and integration tests:
- `test_*.py` - Unit tests
- `manual/` - Manual testing scripts

### `/scripts/`
Utility scripts organized by purpose:
- `dev/` - Development utilities (checks, debugging, visualization)
- `setup/` - Installation and configuration scripts

### `/docs/`
Documentation:
- Project guides
- RAG indexing documentation
- Architecture documents

### `/design_docs/`
Game design document outputs

### `/output/` & `/outputs/`
Generated GDD files

---

## 🗂️ Development Files Location

### Testing Scripts (`tests/manual/`)
- `test_api.py`, `test_pipeline.py`, etc.
- Manual testing and exploration scripts

### Development Tools (`scripts/dev/`)
- `check_ollama_setup.py` - Check Ollama configuration
- `discover_github_models.py` - List available GitHub models
- `visualize_graph.py` - Graph visualization
- `verify_rag.py` - Verify RAG engine
- `fix_*.py`, `refactor_*.py` - Code refactoring utilities

### Setup Scripts (`scripts/setup/`)
- `setup.ps1` - PowerShell setup script
- `setup_supabase*.py` - Supabase configuration
- `run_e2e_background.ps1` - E2E test runner

---

## 🚫 What's NOT in Version Control

The `.gitignore` excludes:
- `.venv/` - Virtual environments
- `__pycache__/` - Python cache
- `node_modules/` - Node dependencies
- `.env` - Environment secrets
- `chroma_data/` - RAG database
- `*.log` - Logs
- `.pytest_cache/` - Test cache

---

## 📝 Contributing

When adding new files:

1. **Tests**: Place in `tests/` (unit) or `tests/manual/` (manual)
2. **Scripts**: Place in `scripts/dev/` (dev utilities) or `scripts/setup/` (installation)
3. **Docs**: Place in `docs/`
4. **Agents**: Place in `agents/game_design/` or `agents/governance/`
5. **Tools**: Place in `tools/`

Keep the root directory clean!
