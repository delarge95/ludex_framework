"""
Engine Feasibility RAG Tool for LUDEX Framework (Sprint 10)

Validates game mechanics against Unity/Unreal/Godot documentation
to prevent hallucinations and provide implementation guidance.
"""

import structlog
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from pathlib import Path

logger = structlog.get_logger(__name__)

# Engine documentation collections
ENGINE_COLLECTIONS = {
    "unity": "unity_docs",
    "unreal": "unreal_docs",
    "godot": "godot_docs"
}
CHROMADB_PATH = Path("data/chromadb")

@tool
def validate_mechanic_feasibility(mechanic: str, engine: str = "unity") -> str:
    """
    Validate if a game mechanic is feasible in the specified engine.
    
    Args:
        mechanic: Description of the game mechanic to validate
        engine: Target engine ("unity", "unreal", or "godot")
        
    Returns:
        Feasibility assessment with implementation guidance from official docs
        
    Examples:
        - validate_mechanic_feasibility("Third-person camera with lock-on targeting", "unity")
        - validate_mechanic_feasibility("Real-time ray-traced reflections", "unreal")
    """
    try:
        logger.info("engine_feasibility_check", mechanic=mechanic, engine=engine)
        
        engine_lower = engine.lower()
        if engine_lower not in ENGINE_COLLECTIONS:
            return f"Unsupported engine: {engine}. Use 'unity', 'unreal', or 'godot'."
        
        # Initialize embeddings
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
        # Load engine-specific vector store
        collection_name = ENGINE_COLLECTIONS[engine_lower]
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=str(CHROMADB_PATH)
        )
        
        # Search for relevant documentation
        query = f"How to implement {mechanic}"
        results = vectorstore.similarity_search_with_score(query, k=3)
        
        if not results:
            return f"⚠️ No official documentation found for '{mechanic}' in {engine.title()}. This feature may require custom implementation or third-party assets."
        
        # Format feasibility report
        report = f"# Feasibility Report: {mechanic} ({engine.title()})\n\n"
        
        for i, (doc, score) in enumerate(results, 1):
            source = doc.metadata.get("source", "Official Docs")
            url = doc.metadata.get("url", "N/A")
            
            report += f"## Result {i} (Relevance: {1 - score:.2f})\n"
            report += f"**Source**: {source}\n"
            report += f"**URL**: {url}\n\n"
            report += f"{doc.page_content}\n\n"
            report += "---\n\n"
        
        logger.info("engine_feasibility_results", count=len(results), engine=engine)
        return report
    
    except Exception as e:
        logger.exception("engine_feasibility_error", error=str(e))
        return f"Error validating feasibility: {str(e)}"


@tool
def get_engine_capabilities(engine: str) -> str:
    """
    Get high-level capabilities summary for a game engine.
    
    Args:
        engine: Engine name ("unity", "unreal", or "godot")
        
    Returns:
        Summary of engine strengths, weaknesses, and best use cases
    """
    capabilities = {
        "unity": {
            "strengths": [
                "Excellent 2D and 3D support",
                "Large Asset Store ecosystem",
                "Cross-platform deployment (30+ platforms)",
                "Strong mobile performance",
                "C# scripting (accessible for beginners)"
            ],
            "weaknesses": [
                "Lower visual fidelity than Unreal (out of the box)",
                "HDRP pipeline can be complex",
                "Asset Store quality varies"
            ],
            "best_for": "Mobile games, indie 2D/3D, VR/AR, prototyping"
        },
        "unreal": {
            "strengths": [
                "Industry-leading AAA graphics (Lumen, Nanite)",
                "Blueprint visual scripting (no code required)",
                "Free Marketplace assets",
                "Excellent for realistic visuals",
                "MetaHuman for character creation"
            ],
            "weaknesses": [
                "Steeper learning curve",
                "Heavy system requirements",
                "Longer compile times",
                "Overkill for simple 2D games"
            ],
            "best_for": "AAA games, photorealistic visuals, first-person shooters, open-world"
        },
        "godot": {
            "strengths": [
                "100% free and open-source",
                "Lightweight and fast iteration",
                "GDScript (Python-like) easy to learn",
                "Excellent for 2D games",
                "Node-based scene system"
            ],
            "weaknesses": [
                "Smaller community and asset library",
                "3D capabilities lag behind Unity/Unreal",
                "Fewer console export options"
            ],
            "best_for": "Indie 2D games, open-source projects, learning, prototyping"
        }
    }
    
    engine_lower = engine.lower()
    if engine_lower not in capabilities:
        return "Unsupported engine. Use: unity, unreal, or godot."
    
    cap = capabilities[engine_lower]
    
    report = f"# {engine.title()} Engine Capabilities\n\n"
    report += "## Strengths\n"
    for strength in cap["strengths"]:
        report += f"- {strength}\n"
    
    report += "\n## Weaknesses\n"
    for weakness in cap["weaknesses"]:
        report += f"- {weakness}\n"
    
    report += f"\n## Best For\n{cap['best_for']}\n"
    
    return report


# Export tools for agent use
engine_feasibility_tools = [
    validate_mechanic_feasibility,
    get_engine_capabilities
]
