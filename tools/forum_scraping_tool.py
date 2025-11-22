"""
Forum Scraping Tool for LUDEX Framework (Sprint 10)

Scrapes community solutions from Unity Forum, Reddit r/Unity3D, and Stack Overflow
to provide real-world implementation guidance and troubleshooting tips.
"""

import structlog
import asyncio
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
import aiohttp
from datetime import datetime, timedelta

logger = structlog.get_logger(__name__)

# Forum endpoints (read-only APIs)
REDDIT_API = "https://www.reddit.com/r/Unity3D/search.json"
STACKOVERFLOW_API = "https://api.stackexchange.com/2.3/search"

# Cache to avoid excessive API calls
_forum_cache: Dict[str, tuple[Any, datetime]] = {}
CACHE_TTL = timedelta(hours=6)


async def _fetch_reddit_solutions(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch solutions from Reddit r/Unity3D"""
    try:
        params = {
            "q": query,
            "limit": limit,
            "sort": "relevance",
            "restrict_sr": "on"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(REDDIT_API, params=params, headers={"User-Agent": "LUDEX/1.0"}) as resp:
                if resp.status != 200:
                    logger.warning("reddit_api_error", status=resp.status)
                    return []
                
                data = await resp.json()
                posts = data.get("data", {}).get("children", [])
                
                results = []
                for post in posts[:limit]:
                    post_data = post.get("data", {})
                    results.append({
                        "source": "Reddit r/Unity3D",
                        "title": post_data.get("title", ""),
                        "url": f"https://reddit.com{post_data.get('permalink', '')}",
                        "score": post_data.get("score", 0),
                        "num_comments": post_data.get("num_comments", 0),
                        "summary": post_data.get("selftext", "")[:300]
                    })
                
                return results
    
    except Exception as e:
        logger.exception("reddit_fetch_error", error=str(e))
        return []


async def _fetch_stackoverflow_solutions(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch solutions from Stack Overflow"""
    try:
        params = {
            "order": "desc",
            "sort": "relevance",
            "q": query,
            "tagged": "unity3d",
            "site": "stackoverflow",
            "pagesize": limit
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(STACKOVERFLOW_API, params=params) as resp:
                if resp.status != 200:
                    logger.warning("stackoverflow_api_error", status=resp.status)
                    return []
                
                data = await resp.json()
                questions = data.get("items", [])
                
                results = []
                for q in questions[:limit]:
                    results.append({
                        "source": "Stack Overflow",
                        "title": q.get("title", ""),
                        "url": q.get("link", ""),
                        "score": q.get("score", 0),
                        "answer_count": q.get("answer_count", 0),
                        "is_answered": q.get("is_answered", False),
                        "tags": q.get("tags", [])
                    })
                
                return results
    
    except Exception as e:
        logger.exception("stackoverflow_fetch_error", error=str(e))
        return []


@tool
async def search_unity_community(query: str, sources: str = "all") -> str:
    """
    Search Unity community forums for implementation guidance and solutions.
    
    Args:
        query: Search query (e.g., "NavMesh baking performance", "UI canvas scaling")
        sources: Which sources to search ("reddit", "stackoverflow", or "all")
        
    Returns:
        Community solutions with links, scores, and summaries
        
    Examples:
        - search_unity_community("How to optimize mobile performance")
        - search_unity_community("Cinemachine camera shake", sources="reddit")
    """
    try:
        logger.info("forum_search", query=query, sources=sources)
        
        # Check cache
        cache_key = f"{query}:{sources}"
        if cache_key in _forum_cache:
            cached_result, cached_time = _forum_cache[cache_key]
            if datetime.now() - cached_time < CACHE_TTL:
                logger.info("forum_cache_hit", query=query)
                return cached_result
        
        # Fetch from sources
        tasks = []
        if sources in ["all", "reddit"]:
            tasks.append(_fetch_reddit_solutions(query))
        if sources in ["all", "stackoverflow"]:
            tasks.append(_fetch_stackoverflow_solutions(query))
        
        results_lists = await asyncio.gather(*tasks)
        all_results = [item for sublist in results_lists for item in sublist]
        
        if not all_results:
            return f"No community solutions found for: {query}"
        
        # Format results
        report = f"# Community Solutions: {query}\n\n"
        report += f"**Found {len(all_results)} solutions**\n\n"
        
        for i, result in enumerate(all_results, 1):
            source = result.get("source", "Unknown")
            title = result.get("title", "")
            url = result.get("url", "")
            score = result.get("score", 0)
            
            report += f"## {i}. {title}\n"
            report += f"**Source**: {source} | **Score**: {score}\n"
            report += f"**URL**: {url}\n"
            
            if "answer_count" in result:
                report += f"**Answers**: {result['answer_count']} | **Solved**: {result.get('is_answered', False)}\n"
            if "num_comments" in result:
                report += f"**Comments**: {result['num_comments']}\n"
            if "summary" in result and result["summary"]:
                report += f"\n{result['summary'][:200]}...\n"
            
            report += "\n---\n\n"
        
        # Cache result
        _forum_cache[cache_key] = (report, datetime.now())
        
        logger.info("forum_search_complete", count=len(all_results))
        return report
    
    except Exception as e:
        logger.exception("forum_search_error", error=str(e))
        return f"Error searching forums: {str(e)}"


@tool
def get_unity_best_practices() -> str:
    """
    Get curated Unity best practices from community consensus.
    
    Returns:
        List of common Unity best practices and anti-patterns
    """
    practices = {
        "Performance": [
            "Use object pooling instead of Instantiate/Destroy in loops",
            "Bake lighting whenever possible (avoid realtime for static objects)",
            "Use LOD (Level of Detail) for distant objects",
            "Profile with Unity Profiler before optimizing (don't guess!)",
            "Avoid GetComponent in Update() - cache references"
        ],
        "Architecture": [
            "Use ScriptableObjects for game data (not MonoBehaviours)",
            "Implement event systems (UnityEvents or custom) instead of direct references",
            "Separate data from logic (Model-View-Presenter pattern)",
            "Use prefab variants for object hierarchies",
            "Avoid MonoBehaviour singletons (use dependency injection)"
        ],
        "UI": [
            "Use Canvas Groups for show/hide instead of SetActive",
            "Set 'Pixel Perfect' on UI Canvas for crisp sprites",
            "Use TextMeshPro instead of legacy Text component",
            "Anchor UI elements correctly for multi-resolution support",
            "Minimize Canvas rebuilds (group static UI separately)"
        ],
        "Mobile": [
            "Target 30 FPS for mid-range devices, 60 FPS for high-end",
            "Use texture atlases to reduce draw calls",
            "Avoid alpha blending (expensive on mobile GPU)",
            "Test on actual devices, not just emulators",
            "Use Unity's Mobile Optimization guide"
        ]
    }
    
    report = "# Unity Best Practices (Community Consensus)\n\n"
    for category, tips in practices.items():
        report += f"## {category}\n"
        for tip in tips:
            report += f"- {tip}\n"
        report += "\n"
    
    return report


# Export tools for agent use
forum_tools = [
    search_unity_community,
    get_unity_best_practices
]
