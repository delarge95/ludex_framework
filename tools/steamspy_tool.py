"""
SteamSpy API Integration Tool for LUDEX Framework.

SteamSpy provides estimated player count and ownership data that Steam's official API doesn't expose.
API Documentation: https://steamspy.com/api.php

Rate Limiting: 1 request per 4 seconds (free tier)
Data Accuracy: Estimates based on statistical sampling, not 100% accurate
"""

import httpx
import asyncio
import structlog
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from functools import lru_cache

logger = structlog.get_logger(__name__)

# Simple in-memory cache with expiry
_steamspy_cache: Dict[int, tuple[Dict[str, Any], datetime]] = {}
CACHE_TTL_HOURS = 24

class SteamSpyTool:
    """Tool for fetching SteamSpy data."""
    
    BASE_URL = "https://steamspy.com/api.php"
    RATE_LIMIT_SECONDS = 4  # SteamSpy allows 1 request per 4 seconds
    
    def __init__(self):
        self.last_request_time: Optional[datetime] = None
    
    async def _rate_limit(self):
        """Enforce rate limiting."""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.RATE_LIMIT_SECONDS:
                wait_time = self.RATE_LIMIT_SECONDS - elapsed
                logger.debug("steamspy_rate_limit", wait_seconds=wait_time)
                await asyncio.sleep(wait_time)
        self.last_request_time = datetime.now()
    
    def _get_cached(self, appid: int) -> Optional[Dict[str, Any]]:
        """Retrieve from cache if not expired."""
        if appid in _steamspy_cache:
            data, timestamp = _steamspy_cache[appid]
            age = datetime.now() - timestamp
            if age < timedelta(hours=CACHE_TTL_HOURS):
                logger.info("steamspy_cache_hit", appid=appid, age_hours=age.total_seconds() / 3600)
                return data
            else:
                # Expired, remove from cache
                del _steamspy_cache[appid]
        return None
    
    def _set_cache(self, appid: int, data: Dict[str, Any]):
        """Store in cache with timestamp."""
        _steamspy_cache[appid] = (data, datetime.now())
    
    async def get_game_details(self, appid: int) -> Dict[str, Any]:
        """
        Fetch SteamSpy data for a game by Steam App ID.
        
        Args:
            appid: Steam Application ID
        
        Returns:
            Dict containing:
                - appid: Steam App ID
                - name: Game name
                - owners: Estimated ownership range (e.g., "500,000 .. 1,000,000")
                - players_forever: Estimated total unique players
                - players_2weeks: Players in last 2 weeks
                - average_forever: Average playtime (minutes)
                - average_2weeks: Average playtime in last 2 weeks (minutes)
                - median_forever: Median playtime (minutes)
                - median_2weeks: Median playtime in last 2 weeks (minutes)
                - ccu: Estimated concurrent users
                - positive: Positive review count
                - negative: Negative review count
                - score_rank: Overall popularity rank
                - tags: Dict of tags and their vote counts
        """
        # Check cache first
        cached = self._get_cached(appid)
        if cached:
            return cached
        
        # Enforce rate limiting
        await self._rate_limit()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    "request": "appdetails",
                    "appid": appid
                }
                
                logger.info("steamspy_request", appid=appid)
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Validate response
                if not data or data.get("appid") != appid:
                    logger.warning("steamspy_invalid_response", appid=appid, data=data)
                    return self._empty_response(appid)
                
                # Cache the result
                self._set_cache(appid, data)
                
                logger.info(
                    "steamspy_success",
                    appid=appid,
                    name=data.get("name", "Unknown"),
                    owners=data.get("owners", "Unknown"),
                    players=data.get("players_forever", 0)
                )
                
                return data
        
        except httpx.HTTPStatusError as e:
            logger.error("steamspy_http_error", appid=appid, status=e.response.status_code)
            return self._empty_response(appid, error=f"HTTP {e.response.status_code}")
        
        except httpx.RequestError as e:
            logger.error("steamspy_request_error", appid=appid, error=str(e))
            return self._empty_response(appid, error=str(e))
        
        except Exception as e:
            logger.exception("steamspy_unexpected_error", appid=appid, error=str(e))
            return self._empty_response(appid, error=str(e))
    
    def _empty_response(self, appid: int, error: str = "No data available") -> Dict[str, Any]:
        """Return empty response structure."""
        return {
            "appid": appid,
            "name": "Unknown",
            "owners": "0",
            "players_forever": 0,
            "players_2weeks": 0,
            "average_forever": 0,
            "average_2weeks": 0,
            "median_forever": 0,
            "median_2weeks": 0,
            "ccu": 0,
            "positive": 0,
            "negative": 0,
            "score_rank": 0,
            "tags": {},
            "error": error
        }
    
    def get_ownership_estimate(self, owners_str: str) -> tuple[int, int]:
        """
        Parse ownership range string into min/max values.
        
        Example: "500,000 .. 1,000,000" -> (500000, 1000000)
        """
        try:
            parts = owners_str.replace(",", "").split("..")
            if len(parts) == 2:
                min_owners = int(parts[0].strip())
                max_owners = int(parts[1].strip())
                return (min_owners, max_owners)
            else:
                # Single value
                single = int(parts[0].strip())
                return (single, single)
        except Exception as e:
            logger.warning("ownership_parse_error", owners_str=owners_str, error=str(e))
            return (0, 0)


# Singleton instance
steamspy_tool = SteamSpyTool()


# LangChain-compatible tool wrapper
async def get_steamspy_data(appid: int) -> str:
    """
    Fetch SteamSpy data for a Steam game.
    
    Provides estimated player counts, ownership data, and playtime statistics
    that are not available through Steam's official API.
    
    Args:
        appid: Steam Application ID (e.g., 730 for CS:GO)
    
    Returns:
        JSON string with SteamSpy data
    """
    import json
    data = await steamspy_tool.get_game_details(appid)
    return json.dumps(data, indent=2)
