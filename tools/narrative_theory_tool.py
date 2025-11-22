"""
Narrative Theory RAG Tool for LUDEX Framework (Sprint 10)

Provides semantic search over indexed narrative theory frameworks
(Hero's Journey, Save the Cat, Story by Robert McKee, etc.)
"""

import structlog
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from pathlib import Path

logger = structlog.get_logger(__name__)

# Narrative theory database configuration
NARRATIVE_THEORY_COLLECTION = "narrative_theory"
CHROMADB_PATH = Path("data/chromadb")

@tool
def query_narrative_theory(query: str, top_k: int = 3) -> str:
    """
    Query narrative theory knowledge base for story structure guidance.
    
    Args:
        query: Natural language question about narrative frameworks
        top_k: Number of relevant passages to return
        
    Returns:
        Relevant narrative theory passages with source citations
        
    Examples:
        - "What is the hero's journey structure?"
        - "How to create a compelling character arc?"
        - "What are the beats in Save the Cat?"
    """
    try:
        logger.info("narrative_theory_query", query=query, top_k=top_k)
        
        # Initialize embeddings (same as used for indexing)
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
        # Load vector store
        vectorstore = Chroma(
            collection_name=NARRATIVE_THEORY_COLLECTION,
            embedding_function=embeddings,
            persist_directory=str(CHROMADB_PATH)
        )
        
        # Perform semantic search
        results = vectorstore.similarity_search_with_score(query, k=top_k)
        
        if not results:
            return "No relevant narrative theory found for this query."
        
        # Format results with citations
        formatted_results = []
        for doc, score in results:
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "N/A")
            framework = doc.metadata.get("framework", "General")
            
            formatted_results.append(
                f"**Source**: {source} (Page {page}, Framework: {framework})\n"
                f"**Relevance**: {1 - score:.2f}\n"
                f"**Content**: {doc.page_content}\n"
            )
        
        logger.info("narrative_theory_results", count=len(results))
        return "\n---\n".join(formatted_results)
    
    except Exception as e:
        logger.exception("narrative_theory_query_error", error=str(e))
        return f"Error querying narrative theory: {str(e)}"


@tool
def get_narrative_frameworks() -> str:
    """
    List all available narrative frameworks in the knowledge base.
    
    Returns:
        List of indexed narrative frameworks with brief descriptions
    """
    frameworks = {
        "Hero's Journey (Joseph Campbell)": "17-stage monomyth structure for epic adventures",
        "Three-Act Structure (Syd Field)": "Classic setup-confrontation-resolution screenplay structure",
        "Save the Cat (Blake Snyder)": "15 story beats for commercial screenwriting",
        "Story (Robert McKee)": "Principles of story structure and character design",
        "Writer's Journey (Christopher Vogler)": "12-stage adaptation of Hero's Journey for films",
        "Kishōtenketsu": "Four-act structure for non-Western narratives (intro-development-twist-conclusion)"
    }
    
    result = "# Available Narrative Frameworks\n\n"
    for name, description in frameworks.items():
        result += f"- **{name}**: {description}\n"
    
    return result


# Export tools for agent use
narrative_theory_tools = [
    query_narrative_theory,
    get_narrative_frameworks
]
