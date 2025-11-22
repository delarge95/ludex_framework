# Forum Content Indexing - Quick Start

## Overview

This script scrapes and indexes community content from:
- **Reddit**: r/Unity3D, r/unrealengine, r/godot
- **Stack Overflow**: unity3d, unreal-engine, godot tags

Indexed content enables semantic search for community wisdom alongside official documentation.

---

## Installation

```bash
# Required packages
pip install aiohttp langchain-community chromadb ollama

# Ensure Ollama is running with embedding model
ollama pull nomic-embed-text
```

---

## Usage

### Index Single Source

```bash
# Index top 1000 Reddit r/Unity3D posts
python scripts/index_forum_content.py --source reddit_unity --limit 1000

# Index top 500 Stack Overflow unity3d questions
python scripts/index_forum_content.py --source stackoverflow_unity --limit 500
```

### Index All Sources

```bash
# Index all forums (recommended: 500-1000 per source)
python scripts/index_forum_content.py --all --limit 500
```

**Available Sources**:
- `reddit_unity` - r/Unity3D top posts
- `reddit_unreal` - r/unrealengine top posts
- `reddit_godot` - r/godot top posts
- `stackoverflow_unity` - Stack Overflow unity3d tag
- `stackoverflow_unreal` - Stack Overflow unreal-engine tag

---

## How It Works

1. **Scrapes** top posts/questions from forums (all-time highest voted)
2. **Caches** raw JSON to `data/forum_cache/` for reuse
3. **Converts** to documents with metadata (score, tags, URL)
4. **Splits** into 800-char chunks with 150-char overlap
5. **Indexes** into ChromaDB collections by engine

### Collections

- `forum_unity` - Unity-related content (Reddit + Stack Overflow)
- `forum_unreal` - Unreal-related content
- `forum_godot` - Godot-related content

---

## Integration with RAG Tools

Once indexed, `EngineFeasibilityTool` and `ForumScrapingTool` will query both:
- **Official docs** (from `index_engine_docs.py`)
- **Community content** (from this script)

### Example Query Flow

```python
from tools.engine_feasibility_tool import validate_mechanic_feasibility

# This will search BOTH official Unity docs AND indexed community solutions
result = validate_mechanic_feasibility(
    "NavMesh baking performance optimization",
    engine="unity"
)
```

Result includes:
- Official Unity NavMesh documentation
- Top Reddit discussions on NavMesh performance
- Stack Overflow solutions for NavMesh baking

---

## Caching

- Raw scraped data saved to `data/forum_cache/{source}.json`
- Re-running script uses cache (fast)
- Delete cache files to re-scrape fresh data

---

## Rate Limiting

- **Reddit**: 2 seconds between requests
- **Stack Overflow**: 1 second between requests
- Total time: ~15-30 minutes for all sources (500 posts each)

---

## Expected Results

| Source | Posts | Chunks | Collection |
|--------|-------|--------|------------|
| Reddit r/Unity3D | 1000 | ~3000 | forum_unity |
| Reddit r/unrealengine | 1000 | ~3000 | forum_unreal |
| Reddit r/godot | 500 | ~1500 | forum_godot |
| SO unity3d | 500 | ~2000 | forum_unity |
| SO unreal-engine | 500 | ~2000 | forum_unreal |
| **Total** | **3500** | **~11,500** | 3 collections |

---

## Verification

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Check Unity forum collection
unity_forum = Chroma(
    collection_name="forum_unity",
    embedding_function=embeddings,
    persist_directory="data/chromadb"
)
print(f"Unity forum chunks: {unity_forum._collection.count()}")

# Test semantic search
results = unity_forum.similarity_search("NavMesh performance tips", k=3)
for doc in results:
    print(f"- {doc.metadata['source']}: {doc.metadata.get('url', 'N/A')}")
```

---

## Troubleshooting

### "Rate limit exceeded"
- Reddit/Stack Overflow have API limits
- Wait 1 hour and retry
- Reduce `--limit` to smaller batches

### "Empty results"
- Check internet connection
- Verify forum APIs are accessible
- Check firewall/proxy settings

### "Ollama not found"
```bash
ollama serve
ollama pull nomic-embed-text
```

---

## Maintenance

### Update Forum Content (Monthly)

```bash
# Delete cache to force fresh scrape
rm -rf data/forum_cache/

# Re-index all sources
python scripts/index_forum_content.py --all --limit 1000
```

### Clear and Re-index

```bash
# Remove ChromaDB forum collections
# (Manually delete forum_* collections or delete entire chromadb folder)

# Re-run indexing
python scripts/index_forum_content.py --all --limit 500
```

---

## Storage

- **Cached JSON**: ~50MB per 1000 posts
- **ChromaDB Index**: ~200MB for 10k chunks
- **Total**: ~500MB for full forum indexing
