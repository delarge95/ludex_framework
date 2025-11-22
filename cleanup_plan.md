# Cleanup Plan - ARA Framework Pivot

## 1. Archive Strategy
We will create an `_archive` directory to store all legacy academic components and documentation. This ensures no data is lost but keeps the workspace clean.

### Directories to Create
- `_archive/docs/`
- `_archive/agents/`
- `_archive/tools/`
- `_archive/root_docs/`

## 2. Files to Move

### Root Documentation (Move to `_archive/root_docs/`)
- `ANALISIS_APIS_PREMIUM.md`
- `ANALISIS_ULTRATHINK_2025.md`
- `AUDIT_COMPLETO_LIMPIEZA.md`
- `CONFIGURACION_APIS.md`
- `DEPENDENCY_FIX.md`
- `GETTING_STARTED.md`
- `GITHUB_MODELS_*.md`
- `GUIA_OLLAMA.md`
- `INDICE_DOCUMENTACION.md`
- `INICIO_RAPIDO.md`
- `INSTALLATION.md`
- `INTEGRACION_*.md`
- `LANGGRAPH_MIGRATION_COMPLETE.md`
- `LIMPIEZA_COMPLETADA_SUMARIO.md`
- `OLLAMA_QUICKSTART.md`
- `OPTIMIZACIONES_MODELOS.md`
- `PERMISOS_GITHUB_TOKEN.md`
- `PLAN_LIMPIEZA_DEFINITIVO.md`
- `PYTHON_COMPATIBILITY.md`
- `README_NEW.md`
- `REPORTE_LIMPIEZA_FINAL.md`
- `RESULTADOS_OPTIMIZACION_v2.2.md`
- `RESUMEN_*.md`
- `ROADMAP_*.md`
- `STATUS.md`
- `TOOL_CALLING_LIMITACION.md`

### Legacy `docs/` (Move to `_archive/docs/`)
- Move ALL files from `docs/` to `_archive/docs/` EXCEPT `TESTING_STRATEGY.md` (might be useful to adapt).
- The `.speckit` folder is now the source of truth.

### Legacy Agents (Move to `_archive/agents/`)
- `agents/literature_researcher.py`
- `agents/niche_analyst.py`
- `agents/technical_architect.py`
- `agents/implementation_specialist.py`
- `agents/content_synthesizer.py`

### Legacy Tools (Move to `_archive/tools/`)
- `tools/search_tool.py` (Semantic Scholar)
- `tools/pdf_tool.py` (Academic PDF processing)
- `tools/perplexity_tool.py` (If not needed for new flow)

## 3. New Structure Creation
- `core/rag/` (New)
- `tools/game_info/` (New)
- `agents/game_design/` (New - for new agents)

## 4. Verification
- Ensure `main.py` and `cli/` are updated to not import moved modules (will break temporarily until refactor).
