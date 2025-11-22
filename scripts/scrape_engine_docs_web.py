"""
Web Documentation Scraper for LUDEX Framework

Scrapes documentation directly from official game engine websites:
- Unity Docs: https://docs.unity3d.com/
- Unreal Docs: https://docs.unrealengine.com/
- Godot Docs: https://docs.godotengine.org/

Complements local documentation indexing with fresh web content.

Usage:
    python scripts/scrape_engine_docs_web.py --engine unity --limit 500
    python scripts/scrape_engine_docs_web.py --all --limit 1000
"""

import argparse
import asyncio
import structlog
from pathlib import Path
from typing import List
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

logger = structlog.get_logger(__name__)

# Configuration
CHROMADB_PATH = Path("data/chromadb")
WEB_CACHE_PATH = Path("data/web_docs_cache")
WEB_CACHE_PATH.mkdir(parents=True, exist_ok=True)

ENGINE_WEB_CONFIGS = {
    "unity": {
        "name": "Unity Documentation",
        "base_url": "https://docs.unity3d.com/Manual/",
        "start_urls": [
            "https://docs.unity3d.com/Manual/index.html",
            "https://docs.unity3d.com/Manual/ScriptingSection.html",
            "https://docs.unity3d.com/Manual/Graphics.html",
            "https://docs.unity3d.com/Manual/PhysicsSection.html"
        ],
        "collection": "unity_docs",
        "allowed_domains": ["docs.unity3d.com"]
    },
    "unreal": {
        "name": "Unreal Engine Documentation",
        "base_url": "https://docs.unrealengine.com/5.3/en-US/",
        "start_urls": [
            "https://docs.unrealengine.com/5.3/en-US/unreal-engine-programming-and-scripting/",
            "https://docs.unrealengine.com/5.3/en-US/designing-visuals-rendering-and-graphics-with-unreal-engine/",
            "https://docs.unrealengine.com/5.3/en-US/building-virtual-worlds-in-unreal-engine/"
        ],
        "collection": "unreal_docs",
        "allowed_domains": ["docs.unrealengine.com"]
    },
    "godot": {
        "name": "Godot Engine Documentation",
        "base_url": "https://docs.godotengine.org/en/stable/",
        "start_urls": [
            "https://docs.godotengine.org/en/stable/tutorials/scripting/index.html",
            "https://docs.godotengine.org/en/stable/tutorials/3d/index.html",
            "https://docs.godotengine.org/en/stable/tutorials/physics/index.html"
        ],
        "collection": "godot_docs",
        "allowed_domains": ["docs.godotengine.org"]
    }
}


async def fetch_page(session: aiohttp.ClientSession, url: str) -> str:
    """Fetch HTML content from URL"""
    try:
        headers = {"User-Agent": "LUDEX-DocsScraper/1.0"}
        async with session.get(url, headers=headers, timeout=10) as resp:
            if resp.status == 200:
                return await resp.text()
    except Exception as e:
        logger.warning("page_fetch_failed", url=url, error=str(e))
    return ""


def extract_links(html: str, base_url: str, allowed_domains: List[str]) -> List[str]:
    """Extract valid documentation links from HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        
        # Filter to allowed domains and avoid anchors/external links
        if any(domain in parsed.netloc for domain in allowed_domains):
            # Remove fragment (anchor)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if clean_url not in links and not clean_url.endswith(('.pdf', '.zip', '.png', '.jpg')):
                links.append(clean_url)
    
    return links


def extract_content(html: str, url: str) -> str:
    """Extract main content text from documentation page"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script, style, nav elements
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        tag.decompose()
    
    # Try to find main content area (common patterns)
    main_content = (
        soup.find('main') or 
        soup.find('article') or 
        soup.find('div', class_='content') or
        soup.find('div', id='content') or
        soup.body
    )
    
    if main_content:
        text = main_content.get_text(separator='\n', strip=True)
        return text
    
    return ""


async def scrape_engine_docs(engine: str, limit: int = 500):
    """Scrape documentation from engine website"""
    config = ENGINE_WEB_CONFIGS[engine]
    logger.info("scraping_engine_docs", engine=engine, limit=limit)
    
    print(f"\n{'='*60}")
    print(f"🌐 Scraping: {config['name']}")
    print('='*60)
    
    # Check cache
    cache_file = WEB_CACHE_PATH / f"{engine}_web.json"
    if cache_file.exists():
        print(f"   ℹ️  Found cached data from {datetime.fromtimestamp(cache_file.stat().st_mtime)}")
        with open(cache_file, 'r', encoding='utf-8') as f:
            pages = json.load(f)
    else:
        # Scrape fresh
        visited = set()
        to_visit = config["start_urls"].copy()
        pages = []
        
        async with aiohttp.ClientSession() as session:
            while to_visit and len(pages) < limit:
                url = to_visit.pop(0)
                
                if url in visited:
                    continue
                
                visited.add(url)
                
                print(f"   📄 Fetching [{len(pages)+1}/{limit}]: {url[:60]}...")
                
                html = await fetch_page(session, url)
                if not html:
                    continue
                
                # Extract content
                content = extract_content(html, url)
                if len(content) < 100:  # Skip pages with little content
                    continue
                
                pages.append({
                    "url": url,
                    "content": content,
                    "title": BeautifulSoup(html, 'html.parser').title.string if BeautifulSoup(html, 'html.parser').title else "Unknown"
                })
                
                # Find more links (only if we need more pages)
                if len(pages) < limit:
                    links = extract_links(html, url, config["allowed_domains"])
                    for link in links:
                        if link not in visited and link not in to_visit:
                            to_visit.append(link)
                
                # Rate limiting
                await asyncio.sleep(0.5)
        
        # Cache results
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(pages, f, indent=2)
        
        print(f"   ✅ Scraped {len(pages)} pages")
    
    # Convert to documents
    documents = []
    for page in pages:
        documents.append(Document(
            page_content=f"# {page['title']}\n\n{page['content']}",
            metadata={
                "source": config["name"],
                "url": page["url"],
                "engine": engine,
                "type": "web_docs"
            }
        ))
    
    print(f"   📄 Created {len(documents)} documents")
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"   🔪 Split into {len(chunks)} chunks")
    
    # Create embeddings and index
    print(f"   🔄 Creating embeddings...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    collection_name = config["collection"]
    
    # Append to existing or create new
    try:
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=str(CHROMADB_PATH)
        )
        vectorstore.add_documents(chunks)
        print(f"   ➕ Added to collection: {collection_name}")
    except:
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory=str(CHROMADB_PATH)
        )
        print(f"   ✅ Created collection: {collection_name}")
    
    print(f"   ✅ Indexed successfully!")


async def main():
    parser = argparse.ArgumentParser(description="Scrape game engine documentation from web")
    parser.add_argument(
        "--engine",
        choices=["unity", "unreal", "godot"],
        help="Engine docs to scrape"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Scrape all engine docs"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Max pages to scrape per engine (default: 500)"
    )
    
    args = parser.parse_args()
    
    if args.all:
        for engine in ENGINE_WEB_CONFIGS.keys():
            try:
                await scrape_engine_docs(engine, args.limit)
            except Exception as e:
                logger.exception("scraping_failed", engine=engine, error=str(e))
                print(f"❌ Failed to scrape {engine}: {e}")
    elif args.engine:
        await scrape_engine_docs(args.engine, args.limit)
    else:
        parser.print_help()
        print("\n💡 Example:")
        print("   python scripts/scrape_engine_docs_web.py --engine unity --limit 500")
        print("   python scripts/scrape_engine_docs_web.py --all --limit 1000")


if __name__ == "__main__":
    asyncio.run(main())
