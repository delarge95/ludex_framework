import os
from typing import List, Dict, Optional, Any
from langchain.tools import tool
from igdb.wrapper import IGDBWrapper
import json
import requests
import structlog
from config.settings import settings

logger = structlog.get_logger(__name__)

class MockIGDBWrapper:
    """Mock wrapper for when IGDB keys are missing."""
    def api_request(self, endpoint: str, query: str) -> bytes:
        logger.warning("using_mock_igdb", endpoint=endpoint)
        if endpoint == 'games':
            # Return dummy game data
            return json.dumps([{
                "id": 1,
                "name": "Mock Game Title",
                "summary": "A simulated game for testing purposes.",
                "genres": [{"name": "Indie"}, {"name": "Strategy"}],
                "platforms": [{"name": "PC"}],
                "total_rating": 85.0,
                "first_release_date": 1672531200,
                "similar_games": [{"name": "Civilization VI"}, {"name": "Stellaris"}]
            }]).encode('utf-8')
        return b"[]"

class GameInfoTool:
    """
    Tool for retrieving game metadata, market trends, and details from IGDB and Steam.
    """
    
    def __init__(self):
        self.client_id = settings.IGDB_CLIENT_ID
        self.client_secret = settings.IGDB_CLIENT_SECRET
        self._wrapper = None
        self.is_mock = False
        
    @property
    def wrapper(self):
        if not self._wrapper:
            if not self.client_id or not self.client_secret:
                logger.warning("igdb_keys_missing", message="IGDB keys not found. Using MockIGDBWrapper.")
                self._wrapper = MockIGDBWrapper()
                self.is_mock = True
            else:
                try:
                    access_token = self._get_access_token()
                    self._wrapper = IGDBWrapper(self.client_id, access_token)
                except Exception as e:
                    logger.error("igdb_auth_failed", error=str(e))
                    self._wrapper = MockIGDBWrapper()
                    self.is_mock = True
        return self._wrapper

    def _get_access_token(self) -> str:
        url = f"https://id.twitch.tv/oauth2/token?client_id={self.client_id}&client_secret={self.client_secret}&grant_type=client_credentials"
        response = requests.post(url)
        response.raise_for_status()
        return response.json()["access_token"]

    @tool("search_games")
    def search_games(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for games by name on IGDB. Returns a list of games with basic metadata.
        Useful for finding similar games or checking if a title exists.
        """
        pass

    def search_games_logic(self, query: str) -> List[Dict[str, Any]]:
        try:
            byte_array = self.wrapper.api_request(
                'games',
                f'search "{query}"; fields name, summary, genres.name, platforms.name, total_rating, first_release_date; limit 10;'
            )
            return json.loads(byte_array)
        except Exception as e:
            logger.error("igdb_search_failed", error=str(e))
            return []

    def get_game_details(self, game_id: int) -> Dict[str, Any]:
        try:
            byte_array = self.wrapper.api_request(
                'games',
                f'fields name, summary, storyline, genres.name, themes.name, player_perspectives.name, similar_games.name, cover.url, screenshots.url; where id = {game_id};'
            )
            result = json.loads(byte_array)
            return result[0] if result else {}
        except Exception as e:
            logger.error("igdb_details_failed", error=str(e))
            return {}

    def get_similar_games(self, game_name: str) -> List[Dict[str, Any]]:
        """Finds similar games based on a game name."""
        search_results = self.search_games_logic(game_name)
        if not search_results:
            return []
        
        game_id = search_results[0]['id']
        return self.get_game_details(game_id).get('similar_games', [])

# Standalone functions for LangChain tools
def create_game_info_tools():
    tool_instance = GameInfoTool()
    
    @tool("search_games")
    def search_games(query: str):
        """Search for games by name to get metadata like genres, rating, and release date."""
        try:
            return tool_instance.search_games_logic(query)
        except Exception as e:
            return f"Error searching games: {str(e)}"

    @tool("get_game_details")
    def get_game_details(game_id: int):
        """Get detailed information about a specific game by its ID, including storyline and similar games."""
        try:
            return tool_instance.get_game_details(game_id)
        except Exception as e:
            return f"Error getting game details: {str(e)}"

    return [search_games, get_game_details]
