from langchain.tools import tool
from core.rag.rag_engine import RAGEngine
import structlog

logger = structlog.get_logger(__name__)

# Singleton instance for RAG Engine to be used by tools
_rag_engine = None

def get_rag_engine():
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine

@tool("search_game_design_patterns")
def search_design_patterns(query: str) -> str:
    """
    Search for game design patterns and mechanics in the knowledge base.
    Useful for finding standard solutions to gameplay problems.
    """
    try:
        rag = get_rag_engine()
        results = rag.query(query, n_results=3)
        if not results:
            return "No relevant design patterns found."
        
        formatted_output = "Found the following design patterns:\n"
        for res in results:
            formatted_output += f"- {res['content']} (Source: {res['metadata'].get('source', 'Unknown')})\n"
        return formatted_output
    except Exception as e:
        logger.error("rag_search_failed", error=str(e))
        return f"Error searching design patterns: {str(e)}"

@tool("search_engine_docs")
def search_engine_docs(query: str) -> str:
    """
    Search official Unity/Unreal documentation for technical implementation details.
    ALWAYS use this before suggesting code or technical architecture.
    """
    try:
        rag = get_rag_engine()
        results = rag.query(query, n_results=3)
        if not results:
            return "No relevant documentation found."
        
        formatted_output = "Found the following documentation:\n"
        for res in results:
            formatted_output += f"- {res['content']} (Source: {res['metadata'].get('source', 'Unknown')})\n"
        return formatted_output
    except Exception as e:
        logger.error("rag_search_failed", error=str(e))
        return f"Error searching documentation: {str(e)}"

class RetrievalTool:
    """
    Wrapper class to expose tools to agents in the expected format.
    """
    def __init__(self):
        self.search_design_patterns = search_design_patterns
        self.search_engine_docs = search_engine_docs

