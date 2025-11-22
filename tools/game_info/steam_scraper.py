from langchain.tools import tool
from playwright.async_api import async_playwright
from typing import Dict, Any, List
import asyncio

class SteamScraper:
    """
    Scrapes Steam Storefront for data not available in IGDB (e.g., user tags, recent review sentiment, pricing).
    """
    
    async def scrape_game_data(self, app_id: str) -> Dict[str, Any]:
        url = f"https://store.steampowered.com/app/{app_id}/"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Bypass age gate if necessary (cookies)
            await page.context.add_cookies([{
                'name': 'wants_mature_content',
                'value': '1',
                'domain': 'store.steampowered.com',
                'path': '/'
            }, {
                'name': 'birthtime',
                'value': '568022401',
                'domain': 'store.steampowered.com',
                'path': '/'
            }, {
                'name': 'lastagecheckage',
                'value': '1-0-1988',
                'domain': 'store.steampowered.com',
                'path': '/'
            }])
            
            try:
                await page.goto(url, wait_until="domcontentloaded")
                
                data = {}
                
                # Title
                data['title'] = await page.locator('#appHubAppName').inner_text()
                
                # Tags
                tags = await page.locator('.app_tag').all_inner_texts()
                data['tags'] = [t.strip() for t in tags if t.strip() != '+']
                
                # Review Sentiment
                sentiment = await page.locator('.game_review_summary').first.inner_text()
                data['sentiment'] = sentiment
                
                # Price
                try:
                    price = await page.locator('.game_purchase_price').first.inner_text()
                    data['price'] = price.strip()
                except:
                    data['price'] = "Free / Owned / Sale"

                return data
                
            except Exception as e:
                return {"error": str(e)}
            finally:
                await browser.close()

# Wrapper for synchronous tool execution
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@tool("get_steam_data")
def get_steam_data(app_id: str):
    """
    Get real-time data from Steam for a specific App ID (tags, sentiment, price).
    Useful for market validation.
    """
    scraper = SteamScraper()
    return run_async(scraper.scrape_game_data(app_id))
