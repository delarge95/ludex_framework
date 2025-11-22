# RAG Indexing Guide for LUDEX Framework

This guide explains how to populate the ChromaDB vector store with game engine documentation and narrative theory for enhanced RAG capabilities.

## Prerequisites

```bash
# Install required dependencies
pip install langchain-community pypdf unstructured chromadb ollama

# Ensure Ollama is running with nomic-embed-text model
ollama pull nomic-embed-text
```

---

## 1. Engine Documentation Indexing

### Download Documentation

Create directory structure:
```bash
mkdir -p data/engine_docs/unity
mkdir -p data/engine_docs/unreal  
mkdir -p data/engine_docs/godot
```

### Unity Documentation
1. Visit: https://docs.unity3d.com/Manual/
2. Download manual as Markdown/HTML
3. Extract to `data/engine_docs/unity/`

**Alternative**: Use Unity's offline documentation package

### Unreal Documentation
1. Visit: https://docs.unrealengine.com/5.3/
2. Download documentation (requires Epic Games account)
3. Extract to `data/engine_docs/unreal/`

### Godot Documentation
1. Visit: https://docs.godotengine.org/en/stable/
2. Clone docs repo: `git clone https://github.com/godotengine/godot-docs.git`
3. Copy to `data/engine_docs/godot/`

### Run Indexing

```bash
# Index all engines (takes 30-60 minutes)
python scripts/index_engine_docs.py --all

# Or index individually
python scripts/index_engine_docs.py --engine unity
python scripts/index_engine_docs.py --engine unreal
python scripts/index_engine_docs.py --engine godot
```

**Expected Output**:
- Unity: ~15,000 chunks
- Unreal: ~20,000 chunks  
- Godot: ~10,000 chunks

---

## 2. Narrative Theory Indexing

### Acquire Books (PDF format)

Create directory:
```bash
mkdir -p data/narrative_theory
```

**Required Books** (place PDFs in `data/narrative_theory/`):
1. **Save the Cat!** by Blake Snyder
2. **Story** by Robert McKee
3. **The Writer's Journey** by Christopher Vogler
4. **The Hero with a Thousand Faces** by Joseph Campbell

**File naming** (flexible matching):
- `save_the_cat.pdf` or `Save the Cat - Blake Snyder.pdf`
- `story_mckee.pdf` or `Story by Robert McKee.pdf`
- `writers_journey.pdf` or `The Writers Journey - Vogler.pdf`
- `hero_thousand_faces.pdf` or `Hero with a Thousand Faces.pdf`

### Run Indexing

```bash
python scripts/index_narrative_theory.py
```

**Expected Output**:
- Total: ~3,000-5,000 chunks (depending on book lengths)
- Save the Cat: ~800 chunks
- Story: ~1,500 chunks
- Writer's Journey: ~900 chunks
- Hero's Journey: ~1,200 chunks

---

## 3. Verification

### Check ChromaDB Collections

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Check Unity docs
unity_db = Chroma(
    collection_name="unity_docs",
    embedding_function=embeddings,
    persist_directory="data/chromadb"
)
print(f"Unity chunks: {unity_db._collection.count()}")

# Check narrative theory
narrative_db = Chroma(
    collection_name="narrative_theory",
    embedding_function=embeddings,
    persist_directory="data/chromadb"
)
print(f"Narrative chunks: {narrative_db._collection.count()}")
```

### Test Queries

```python
# Test engine feasibility query
from tools.engine_feasibility_tool import validate_mechanic_feasibility

result = validate_mechanic_feasibility(
    "Third-person camera with lock-on targeting",
    engine="unity"
)
print(result)

# Test narrative theory query
from tools.narrative_theory_tool import query_narrative_theory

result = query_narrative_theory("What is the hero's journey structure?")
print(result)
```

---

## 4. Maintenance

### Update Documentation

When game engines release new versions:
```bash
# Re-download updated docs to data/engine_docs/{engine}/
# Re-run indexing script
python scripts/index_engine_docs.py --engine unity
```

### Clear and Re-index

```bash
# Remove existing ChromaDB data
rm -rf data/chromadb/

# Re-run all indexing scripts
python scripts/index_engine_docs.py --all
python scripts/index_narrative_theory.py
```

---

## Troubleshooting

### "Ollama not found" error
```bash
# Ensure Ollama is running
ollama serve

# Pull embedding model
ollama pull nomic-embed-text
```

### "Out of memory" during indexing
- Process one engine at a time instead of --all
- Reduce chunk_size in scripts (default: 1000 → 500)
- Close other applications

### Slow indexing
- Expected: 30-60 minutes for full engine docs
- Use SSD for data/chromadb/ directory
- Ensure Ollama has GPU access (if available)

---

## Storage Requirements

- **Engine Docs Raw**: ~500MB per engine
- **Narrative Theory PDFs**: ~50MB
- **ChromaDB Index**: ~2GB (all indexed)
- **Total**: ~3.5GB

---

## Next Steps

Once indexing is complete:
1. Agents will automatically use RAG for queries
2. Test with `TechnicalFeasibilityValidator`
3. Verify `NarrativeArchitect` cites frameworks correctly
4. Monitor query latency (<2 seconds target)
