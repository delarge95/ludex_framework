# Complete RAG Indexing System - All Sources

## Overview

LUDEX now has a comprehensive 4-tier RAG indexing system:

### 1. Engine Documentation
- **Local**: `index_engine_docs.py` (offline docs)
- **Web**: `scrape_engine_docs_web.py` (live scraping)

### 2. Narrative Theory
- **PDF Books**: `index_narrative_theory.py` 
- **Web Sources**: `scrape_narrative_theory_web.py` ⭐ NEW

### 3. Community Forums
- **Forums**: `index_forum_content.py` (Reddit + Stack Overflow)

---

## Complete Indexing Workflow

### Quick Start (Recommended Order)

```bash
# 1. Engine docs via web scraping (fastest)
python scripts/scrape_engine_docs_web.py --all --limit 500

# 2. Narrative theory from web (no PDFs needed)
python scripts/scrape_narrative_theory_web.py --all --limit 100

# 3. Community forums
python scripts/index_forum_content.py --all --limit 500

# 4. (Optional) Local engine docs for offline
python scripts/index_engine_docs.py --all

# 5. (Optional) Narrative theory PDFs if you have them
python scripts/index_narrative_theory.py
```

---

## Narrative Theory Web Sources

### Included Websites

1. **TV Tropes** (`tvtropes`)
   - Narrative devices encyclopedia
   - Story structures (Hero's Journey, Three-Act, etc.)
   - Character archetypes

2. **Helping Writers Become Authors** (`helping_writers`)
   - K.M. Weiland's structure analysis
   - Character arc theory
   - Story beats breakdown

3. **The Story Grid** (`story_grid`)
   - Story Grid methodology
   - Five Commandments of Storytelling
   - Genre conventions

4. **Save the Cat! Blog** (`save_the_cat_blog`)
   - 15-beat structure
   - Genre analysis
   - Screenwriting techniques

5. **Ellen Brock** (`ellen_brock`)
   - Story structure editing
   - Manuscript analysis
   - Narrative pacing

6. **Terribleminds (Chuck Wendig)** (`chuck_wendig`)
   - Storytelling techniques
   - Writing advice
   - Creative process

### Usage Examples

```bash
# Scrape TV Tropes narrative pages
python scripts/scrape_narrative_theory_web.py --source tvtropes --limit 100

# Scrape all narrative sources (recommended)
python scripts/scrape_narrative_theory_web.py --all --limit 50
```

**Expected Output**: ~300-600 chunks across all sources

---

## Complete Coverage Summary

### Engine Documentation
- **Sources**: Unity, Unreal, Godot (web + local)
- **Chunks**: ~45k-50k total
- **Collection**: `unity_docs`, `unreal_docs`, `godot_docs`

### Narrative Theory
- **Sources**: PDFs (4 books) + Web (6 sites)
- **Chunks**: ~5k-8k total
- **Collection**: `narrative_theory`

### Community Forums
- **Sources**: Reddit (3 subs) + Stack Overflow (2 tags)
- **Chunks**: ~10k-12k total
- **Collection**: `forum_unity`, `forum_unreal`, `forum_godot`

### Total RAG Index
- **Total Chunks**: ~60k-70k
- **Storage**: ~3.5GB
- **Indexing Time**: 2-3 hours (all scripts)

---

## Verification

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Check narrative theory with web sources
narrative_db = Chroma(
    collection_name="narrative_theory",
    embedding_function=embeddings,
    persist_directory="data/chromadb"
)

# Test query
results = narrative_db.similarity_search(
    "What is the hero's journey 12 stages?",
    k=5
)

for doc in results:
    print(f"Source: {doc.metadata['source']}")
    print(f"Framework: {doc.metadata.get('framework', 'N/A')}")
    print(f"Content preview: {doc.page_content[:200]}...")
    print("---")
```

Expected sources in results:
- TV Tropes (Hero's Journey page)
- K.M. Weiland (Structure series)
- Save the Cat blog
- Possibly: Hero with a Thousand Faces (PDF)
- Possibly: The Writer's Journey (PDF)

---

## Benefits of Web Scraping Narrative Theory

### vs. PDFs Only
✅ **No manual PDF acquisition** - Legal web sources
✅ **Always up-to-date** - Latest blog posts and articles  
✅ **Diverse perspectives** - Multiple authors and frameworks
✅ **Practical examples** - Real-world story analysis
✅ **Accessible content** - Public domain and Creative Commons

### Quality Sources
All included sites are:
- Recognized authorities in narrative craft
- Actively maintained (updated content)
- Used by professional writers/game designers
- Complement academic books with practical advice

---

## Maintenance

### Update Narrative Theory Content (Quarterly)

```bash
# Delete cache to get fresh content
rm -rf data/narrative_web_cache/

# Re-scrape all narrative sources
python scripts/scrape_narrative_theory_web.py --all --limit 100
```

### Complete Re-index (Annual)

```bash
# Clear all caches
rm -rf data/web_docs_cache/
rm -rf data/narrative_web_cache/
rm -rf data/forum_cache/
rm -rf data/chromadb/

# Re-run all indexing scripts
python scripts/scrape_engine_docs_web.py --all --limit 500
python scripts/scrape_narrative_theory_web.py --all --limit 100
python scripts/index_forum_content.py --all --limit 500
```

---

## Installation

```bash
# Required packages
pip install beautifulsoup4 aiohttp langchain-community chromadb ollama pypdf unstructured

# Ollama embedding model
ollama pull nomic-embed-text
```

---

## Future Enhancements

Potential additional sources:
- **Game-specific narrative**: Gamasutra articles, GDC talks
- **Academic papers**: Google Scholar narrative theory
- **YouTube transcripts**: GDC narrative talks, Extra Credits
- **Game postmortems**: Hades, Last of Us, Disco Elysium
