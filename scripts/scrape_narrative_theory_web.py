"""
Narrative Theory Web Scraper for LUDEX Framework

Scrapes narrative theory content from authoritative websites:
- TV Tropes (narrative devices and story structures)
- Helping Writers Become Authors (K.M. Weiland - structure analysis)
- The Story Grid (story structure methodology)
- Save the Cat Blog (beat sheet theory)
- Writing Excuses (educational writing content)
- Chuck Wendig (storytelling techniques)
- Ellen Brock (editing and story structure)

Complements PDF books with fresh web-based narrative theory.

Usage:
    python scripts/scrape_narrative_theory_web.py --source tvtropes --limit 100
    python scripts/scrape_narrative_theory_web.py --all --limit 500
"""

import argparse
import asyncio
import structlog
from pathlib import Path
from typing import List, Dict, Any
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
NARRATIVE_WEB_CACHE = Path("data/narrative_web_cache")
NARRATIVE_WEB_CACHE.mkdir(parents=True, exist_ok=True)

NARRATIVE_WEB_SOURCES = {
    "tvtropes": {
        "name": "TV Tropes - Narrative Devices",
        "base_url": "https://tvtropes.org",
        "start_urls": [
            "https://tvtropes.org/pmwiki/pmwiki.php/Main/TheHerosJourney",
            "https://tvtropes.org/pmwiki/pmwiki.php/Main/ThreeActStructure",
            "https://tvtropes.org/pmwiki/pmwiki.php/Main/Plots",
            "https://tvtropes.org/pmwiki/pmwiki.php/Main/NarrativeDevices",
            "https://tvtropes.org/pmwiki/pmwiki.php/Main/CharacterDevelopment"
        ],
        "allowed_domains": ["tvtropes.org"],
        "framework": "Various narrative devices"
    },
    "helping_writers": {
        "name": "Helping Writers Become Authors (K.M. Weiland)",
        "base_url": "https://www.helpingwritersbecomeauthors.com",
        "start_urls": [
            "https://www.helpingwritersbecomeauthors.com/secrets-story-structure-complete-series/",
            "https://www.helpingwritersbecomeauthors.com/character-arcs/",
            "https://www.helpingwritersbecomeauthors.com/three-act-structure/"
        ],
        "allowed_domains": ["helpingwritersbecomeauthors.com"],
        "framework": "Story structure and character arcs"
    },
    "story_grid": {
        "name": "The Story Grid",
        "base_url": "https://storygrid.com",
        "start_urls": [
            "https://storygrid.com/what-is-the-story-grid/",
            "https://storygrid.com/five-commandments-of-storytelling/",
            "https://storygrid.com/genre/"
        ],
        "allowed_domains": ["storygrid.com"],
        "framework": "Story Grid methodology"
    },
    "save_the_cat_blog": {
        "name": "Save the Cat! Blog",
        "base_url": "https://savethecat.com",
        "start_urls": [
            "https://savethecat.com/blog",
            "https://savethecat.com/beat-sheet",
            "https://savethecat.com/category/screenwriting"
        ],
        "allowed_domains": ["savethecat.com"],
        "framework": "Save the Cat beat sheets"
    },
    "ellen_brock": {
        "name": "Ellen Brock Editorial (Story Structure)",
        "base_url": "https://www.youtube.com/@EllenBrock",  # Also has blog
        "start_urls": [
            "https://ellenbrock.com/blog/"
        ],
        "allowed_domains": ["ellenbrock.com"],
        "framework": "Story structure and editing"
    },
    "chuck_wendig": {
        "name": "Terribleminds (Chuck Wendig)",
        "base_url": "https://terribleminds.com",
        "start_urls": [
            "https://terribleminds.com/ramble/blog/category/writing-advice/"
        ],
        "allowed_domains": ["terribleminds.com"],
        "framework": "Storytelling techniques"
    }
}


async def fetch_page(session: aiohttp.ClientSession, url: str) -> str:
    """Fetch HTML content from URL"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        async with session.get(url, headers=headers, timeout=15) as resp:
            if resp.status == 200:
                return await resp.text()
    except Exception as e:
        logger.warning("page_fetch_failed", url=url, error=str(e))
    return ""


def extract_links(html: str, base_url: str, allowed_domains: List[str], source_key: str) -> List[str]:
    """Extract valid links from HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        
        # Filter to allowed domains
        if any(domain in parsed.netloc for domain in allowed_domains):
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            # Source-specific filtering
            if source_key == "tvtropes":
                # Only narrative-related pages
                if "/Main/" in clean_url and not clean_url.endswith(('.jpg', '.png', '.gif')):
                    if clean_url not in links:
                        links.append(clean_url)
            else:
                # General filtering
                if not clean_url.endswith(('.pdf', '.zip', '.png', '.jpg', '.gif')):
                    if clean_url not in links:
                        links.append(clean_url)
    
    return links


def extract_content(html: str, url: str, source_key: str) -> Dict[str, str]:
    """Extract title and main content from page"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove unwanted elements
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'form']):
        tag.decompose()
    
    # Extract title
    title = "Unknown"
    if soup.title:
        title = soup.title.string.strip()
    elif soup.find('h1'):
        title = soup.find('h1').get_text(strip=True)
    
    # Source-specific content extraction
    content = ""
    
    if source_key == "tvtropes":
        # TV Tropes uses div#main-article
        main = soup.find('div', id='main-article') or soup.find('article')
    elif source_key == "helping_writers":
        # K.M. Weiland uses article or main
        main = soup.find('article') or soup.find('div', class_='entry-content')
    else:
        # Generic fallback
        main = (
            soup.find('article') or 
            soup.find('main') or
            soup.find('div', class_='content') or
            soup.find('div', id='content')
        )
    
    if main:
        content = main.get_text(separator='\n', strip=True)
    
    return {"title": title, "content": content}


async def scrape_narrative_source(source_key: str, limit: int = 100):
    """Scrape narrative theory from a web source"""
    config = NARRATIVE_WEB_SOURCES[source_key]
    logger.info("scraping_narrative_source", source=source_key, limit=limit)
    
    print(f"\n{'='*60}")
    print(f"📚 Scraping: {config['name']}")
    print(f"   Framework: {config['framework']}")
    print('='*60)
    
    # Check cache
    cache_file = NARRATIVE_WEB_CACHE / f"{source_key}.json"
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
                
                print(f"   📄 Fetching [{len(pages)+1}/{limit}]: {url[:70]}...")
                
                html = await fetch_page(session, url)
                if not html:
                    continue
                
                # Extract content
                page_data = extract_content(html, url, source_key)
                
                # Skip pages with little content
                if len(page_data["content"]) < 200:
                    continue
                
                pages.append({
                    "url": url,
                    "title": page_data["title"],
                    "content": page_data["content"],
                    "framework": config["framework"]
                })
                
                # Find more links (if we need more pages)
                if len(pages) < limit:
                    links = extract_links(html, url, config["allowed_domains"], source_key)
                    for link in links[:10]:  # Limit link expansion
                        if link not in visited and link not in to_visit:
                            to_visit.append(link)
                
                # Rate limiting (be respectful)
                await asyncio.sleep(1)
        
        # Cache results
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(pages, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Scraped {len(pages)} pages")
    
    # Convert to documents
    documents = []
    for page in pages:
        documents.append(Document(
            page_content=f"# {page['title']}\n\n{page['content']}",
            metadata={
                "source": config["name"],
                "url": page["url"],
                "framework": page["framework"],
                "type": "narrative_web"
            }
        ))
    
    print(f"   📄 Created {len(documents)} documents")
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"   🔪 Split into {len(chunks)} chunks")
    
    # Create embeddings and index
    print(f"   🔄 Creating embeddings...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # Add to narrative_theory collection
    try:
        vectorstore = Chroma(
            collection_name="narrative_theory",
            embedding_function=embeddings,
            persist_directory=str(CHROMADB_PATH)
        )
        vectorstore.add_documents(chunks)
        print(f"   ➕ Added to narrative_theory collection")
    except:
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name="narrative_theory",
            persist_directory=str(CHROMADB_PATH)
        )
        print(f"   ✅ Created narrative_theory collection")
    
    print(f"   ✅ Indexed successfully!")


async def main():
    parser = argparse.ArgumentParser(description="Scrape narrative theory from web sources")
    parser.add_argument(
        "--source",
        choices=list(NARRATIVE_WEB_SOURCES.keys()),
        help="Narrative theory source to scrape"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Scrape all narrative theory sources"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Max pages to scrape per source (default: 100)"
    )
    
    args = parser.parse_args()
    
    if args.all:
        for source_key in NARRATIVE_WEB_SOURCES.keys():
            try:
                await scrape_narrative_source(source_key, args.limit)
            except Exception as e:
                logger.exception("scraping_failed", source=source_key, error=str(e))
                print(f"❌ Failed to scrape {source_key}: {e}")
    elif args.source:
        await scrape_narrative_source(args.source, args.limit)
    else:
        parser.print_help()
        print("\n💡 Examples:")
        print("   python scripts/scrape_narrative_theory_web.py --source tvtropes --limit 100")
        print("   python scripts/scrape_narrative_theory_web.py --all --limit 50")
        print("\n📚 Available sources:")
        for key, config in NARRATIVE_WEB_SOURCES.items():
            print(f"   - {key}: {config['name']}")


if __name__ == "__main__":
    asyncio.run(main())
