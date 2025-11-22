import os
from typing import List, Dict, Any
import structlog

logger = structlog.get_logger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("chromadb_not_found", message="ChromaDB not installed. Using MockRAGEngine.")

class RealRAGEngine:
    """
    Retrieval-Augmented Generation Engine for ARA Framework.
    Stores and retrieves technical documentation (Unity/Unreal) to prevent hallucinations.
    """
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = "game_engine_docs"
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        results = self.collection.query(query_texts=[query_text], n_results=n_results)
        formatted_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "id": results['ids'][0][i]
                })
        return formatted_results

    def count_documents(self) -> int:
        return self.collection.count()

class MockRAGEngine:
    """
    Mock RAG Engine for environments where ChromaDB cannot be installed.
    Returns simulated results to keep the system functional.
    """
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        logger.info("mock_rag_engine_initialized")

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        logger.info("mock_add_documents", count=len(documents))

    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        logger.info("mock_query", query=query_text)
        # Return simulated results based on query keywords
        if "unity" in query_text.lower():
            return [{"content": "Unity uses C# for scripting. The main update loop is Update().", "metadata": {"source": "Unity Docs"}, "id": "1"}]
        elif "unreal" in query_text.lower():
            return [{"content": "Unreal Engine uses C++ and Blueprints. Actors are the base class for objects in the level.", "metadata": {"source": "Unreal Docs"}, "id": "2"}]
        elif "pattern" in query_text.lower():
            return [{"content": "The Observer pattern is useful for event handling in games.", "metadata": {"source": "Game Programming Patterns"}, "id": "3"}]
        return [{"content": "Simulated RAG result for: " + query_text, "metadata": {"source": "MockDB"}, "id": "0"}]

    def count_documents(self) -> int:
        return 100

# Export the appropriate engine
if CHROMADB_AVAILABLE:
    RAGEngine = RealRAGEngine
else:
    RAGEngine = MockRAGEngine

