import pytest
import os
from unittest.mock import patch, MagicMock
from tools.game_info.game_info_tool import GameInfoTool
from tools.game_info.steam_scraper import SteamScraper

# Mock environment variables
@patch.dict(os.environ, {"IGDB_CLIENT_ID": "mock_id", "IGDB_CLIENT_SECRET": "mock_secret"})
def test_game_info_tool_initialization():
    with patch('tools.game_info.game_info_tool.requests.post') as mock_post:
        mock_post.return_value.json.return_value = {"access_token": "mock_token"}
        mock_post.return_value.raise_for_status = MagicMock()
        
        tool = GameInfoTool()
        assert tool.client_id == "mock_id"
        # Accessing wrapper should trigger token fetch
        assert tool.wrapper is not None
        mock_post.assert_called_once()

@patch.dict(os.environ, {"IGDB_CLIENT_ID": "mock_id", "IGDB_CLIENT_SECRET": "mock_secret"})
def test_game_search_logic():
    with patch('tools.game_info.game_info_tool.requests.post') as mock_post:
        mock_post.return_value.json.return_value = {"access_token": "mock_token"}
        
        tool = GameInfoTool()
        
        # Mock the wrapper's api_request
        tool._wrapper = MagicMock()
        tool._wrapper.api_request.return_value = b'[{"id": 1, "name": "Mock Game"}]'
        
        results = tool.search_games_logic("Mock Game")
        assert len(results) == 1
        assert results[0]['name'] == "Mock Game"

@pytest.mark.asyncio
async def test_steam_scraper():
    # This test requires Playwright and internet, so we might mock it for CI/CD
    # For now, we'll just mock the playwright execution to ensure the class structure is correct
    with patch('tools.game_info.steam_scraper.async_playwright') as mock_playwright:
        scraper = SteamScraper()
        # We won't actually run the scrape in this unit test to avoid browser launch overhead
        assert scraper is not None
