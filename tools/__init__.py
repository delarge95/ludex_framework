"""
Tools package for LUDEX Framework (Game Design Automation)

Active tools for LUDEX v3.0:
- GameInfoTool: IGDB API integration for game metadata
- SteamScraper: Steam market data scraping
- RetrievalTool: RAG engine for Unity/Unreal documentation (planned)

Legacy tools from academic research phase (v1-v2.2) have been deprecated:
- SearchTool (Semantic Scholar)
- PDFTool (Academic paper processing)
- DatabaseTool (Supabase persistence)
"""

# Active tools for LUDEX v3.0 (Game Design Automation)
from tools.game_info.game_info_tool import GameInfoTool
from tools.game_info.steam_scraper import SteamScraper
# from tools.retrieval_tool import RetrievalTool  # RAG tool - to be implemented

__all__ = [
    "GameInfoTool",
    "SteamScraper",
]
