"""
Forum Content Indexer for LUDEX Framework

Scrapes and indexes game development forum content from:
- Unity Forum (forum.unity.com)
- Unreal Forum (forums.unrealengine.com)  
- Reddit (r/Unity3D, r/unrealengine, r/godot)
- Stack Overflow (unity3d, unreal-engine, godot tags)

Indexed content enables semantic search for community solutions,
complementing real-time API searches.

Usage:
    python scripts/index_forum_content.py --source unity_forum --limit 1000
    python scripts/index_forum_content.py --source reddit_unity --limit 500
    python scripts/index_forum_content.py --all --limit 5000
"""

import argparse
import asyncio
import structlog
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import aiohttp
import json
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

logger = structlog.get_logger(__name__)

# Configuration
CHROMADB_PATH = Path("data/chromadb")
FORUM_CACHE_PATH = Path("data/forum_cache")
FORUM_CACHE_PATH.mkdir(parents=True, exist_ok=True)

FORUM_SOURCES = {
    "reddit_unity": {
        "name": "Reddit r/Unity3D",
        "api": "https://www.reddit.com/r/Unity3D/top.json",
        "collection": "forum_unity"
    },
    "reddit_unreal": {
        "name": "Reddit r/unrealengine",
        "api": "https://www.reddit.com/r/unrealengine/top.json",
        "collection": "forum_unreal"
    },
    "reddit_godot": {
        "name": "Reddit r/godot",
        "api": "https://www.reddit.com/r/godot/top.json",
        "collection": "forum_godot"
    },
    "stackoverflow_unity": {
        "name": "Stack Overflow (unity3d tag)",
        "api": "https://api.stackexchange.com/2.3/questions",
        "collection": "forum_unity",
        "params": {"tagged": "unity3d", "site": "stackoverflow"}
    },
    "stackoverflow_unreal": {
        "name": "Stack Overflow (unreal-engine tag)",
        "api": "https://api.stackexchange.com/2.3/questions",
        "collection": "forum_unreal",
        "params": {"tagged": "unreal-engine", "site": "stackoverflow"}
    }
}


async def scrape_reddit(source_key: str, limit: int = 500) -> List[Dict[str, Any]]:
    """Scrape Reddit posts"""
    config = FORUM_SOURCES[source_key]
    logger.info("scraping_reddit", source=source_key, limit=limit)
    
    posts = []
    after = None
    
    async with aiohttp.ClientSession() as session:
        while len(posts) < limit:
            params = {
                "limit": min(100, limit - len(posts)),
                "t": "all",  # All time top posts
                "after": after
            }
            
            headers = {"User-Agent": "LUDEX-Indexer/1.0"}
            
            async with session.get(config["api"], params=params, headers=headers) as resp:
                if resp.status != 200:
                    logger.warning("reddit_api_error", status=resp.status)
                    break
                
                data = await resp.json()
                children = data.get("data", {}).get("children", [])
                
                if not children:
                    break
                
                for child in children:
                    post_data = child.get("data", {})
                    posts.append({
                        "title": post_data.get("title", ""),
                        "selftext": post_data.get("selftext", ""),
                        "url": f"https://reddit.com{post_data.get('permalink', '')}",
                        "score": post_data.get("score", 0),
                        "num_comments": post_data.get("num_comments", 0),
                        "created_utc": post_data.get("created_utc", 0),
                        "source": config["name"]
                    })
                
                after = data.get("data", {}).get("after")
                if not after:
                    break
                
                # Rate limiting
                await asyncio.sleep(2)
    
    logger.info("reddit_scraping_complete", posts=len(posts))
    return posts


async def scrape_stackoverflow(source_key: str, limit: int = 500) -> List[Dict[str, Any]]:
    """Scrape Stack Overflow questions"""
    config = FORUM_SOURCES[source_key]
    logger.info("scraping_stackoverflow", source=source_key, limit=limit)
    
    questions = []
    page = 1
    
    async with aiohttp.ClientSession() as session:
        while len(questions) < limit:
            params = {
                **config["params"],
                "order": "desc",
                "sort": "votes",
                "pagesize": min(100, limit - len(questions)),
                "page": page,
                "filter": "withbody"  # Include question body
            }
            
            async with session.get(config["api"], params=params) as resp:
                if resp.status != 200:
                    logger.warning("stackoverflow_api_error", status=resp.status)
                    break
                
                data = await resp.json()
                items = data.get("items", [])
                
                if not items:
                    break
                
                for item in items:
                    questions.append({
                        "title": item.get("title", ""),
                        "body": item.get("body", ""),
                        "url": item.get("link", ""),
                        "score": item.get("score", 0),
                        "answer_count": item.get("answer_count", 0),
                        "tags": item.get("tags", []),
                        "is_answered": item.get("is_answered", False),
                        "source": config["name"]
                    })
                
                page += 1
                
                # Respect rate limits
                if not data.get("has_more", False):
                    break
                
                await asyncio.sleep(1)
    
    logger.info("stackoverflow_scraping_complete", questions=len(questions))
    return questions


def convert_to_documents(posts: List[Dict[str, Any]], source_type: str) -> List[Document]:
    """Convert forum posts to LangChain documents"""
    documents = []
    
    for post in posts:
        if source_type == "reddit":
            content = f"# {post['title']}\n\n{post['selftext']}"
            metadata = {
                "source": post["source"],
                "url": post["url"],
                "score": post["score"],
                "num_comments": post["num_comments"],
                "type": "reddit_post"
            }
        else:  # stackoverflow
            content = f"# {post['title']}\n\n{post['body']}"
            metadata = {
                "source": post["source"],
                "url": post["url"],
                "score": post["score"],
                "answer_count": post["answer_count"],
                "tags": ",".join(post["tags"]),
                "type": "stackoverflow_question"
            }
        
        # Skip empty posts
        if len(content.strip()) < 50:
            continue
        
        documents.append(Document(page_content=content, metadata=metadata))
    
    return documents


async def index_forum_source(source_key: str, limit: int = 500):
    """Scrape and index a forum source"""
    config = FORUM_SOURCES[source_key]
    logger.info("indexing_forum_source", source=source_key, limit=limit)
    
    print(f"\n{'='*60}")
    print(f"📥 Scraping: {config['name']}")
    print('='*60)
    
    # Check cache
    cache_file = FORUM_CACHE_PATH / f"{source_key}.json"
    
    if cache_file.exists():
        print(f"   ℹ️  Found cached data from {datetime.fromtimestamp(cache_file.stat().st_mtime)}")
        with open(cache_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
    else:
        # Scrape fresh data
        if source_key.startswith("reddit"):
            posts = await scrape_reddit(source_key, limit)
        elif source_key.startswith("stackoverflow"):
            posts = await scrape_stackoverflow(source_key, limit)
        else:
            logger.error("unknown_source_type", source=source_key)
            return
        
        # Cache results
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2)
        
        print(f"   ✅ Scraped {len(posts)} posts")
    
    # Convert to documents
    source_type = "reddit" if source_key.startswith("reddit") else "stackoverflow"
    documents = convert_to_documents(posts, source_type)
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
    
    collection_name = config["collection"]
    
    # Check if collection exists, append if it does
    try:
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=str(CHROMADB_PATH)
        )
        vectorstore.add_documents(chunks)
        print(f"   ➕ Added to existing collection: {collection_name}")
    except:
        # Create new collection
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory=str(CHROMADB_PATH)
        )
        print(f"   ✅ Created new collection: {collection_name}")
    
    print(f"   ✅ Indexed successfully!")


async def main():
    parser = argparse.ArgumentParser(description="Index game dev forum content")
    parser.add_argument(
        "--source",
        choices=list(FORUM_SOURCES.keys()),
        help="Forum source to index"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Index all forum sources"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Number of posts to scrape per source (default: 500)"
    )
    
    args = parser.parse_args()
    
    if args.all:
        for source_key in FORUM_SOURCES.keys():
            try:
                await index_forum_source(source_key, args.limit)
            except Exception as e:
                logger.exception("indexing_failed", source=source_key, error=str(e))
                print(f"❌ Failed to index {source_key}: {e}")
    elif args.source:
        await index_forum_source(args.source, args.limit)
    else:
        parser.print_help()
        print("\n💡 Example:")
        print("   python scripts/index_forum_content.py --source reddit_unity --limit 1000")
        print("   python scripts/index_forum_content.py --all --limit 500")


if __name__ == "__main__":
    asyncio.run(main())
