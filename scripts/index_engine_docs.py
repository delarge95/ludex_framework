"""
Engine Documentation Indexer for LUDEX Framework

Indexes Unity, Unreal, and Godot documentation into ChromaDB
for semantic search by TechnicalFeasibilityValidator and other agents.

Usage:
    python scripts/index_engine_docs.py --engine unity
    python scripts/index_engine_docs.py --engine unreal
    python scripts/index_engine_docs.py --engine godot
    python scripts/index_engine_docs.py --all
"""

import argparse
import structlog
from pathlib import Path
from typing import List
from langchain_community.document_loaders import DirectoryLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

logger = structlog.get_logger(__name__)

# Configuration
CHROMADB_PATH = Path("data/chromadb")
DOCS_PATH = Path("data/engine_docs")

ENGINE_CONFIGS = {
    "unity": {
        "collection": "unity_docs",
        "docs_path": DOCS_PATH / "unity",
        "url_base": "https://docs.unity3d.com/Manual",
        "description": "Unity 6 Manual and Scripting API"
    },
    "unreal": {
        "collection": "unreal_docs",
        "docs_path": DOCS_PATH / "unreal",
        "url_base": "https://docs.unrealengine.com/5.3",
        "description": "Unreal Engine 5.3 Documentation"
    },
    "godot": {
        "collection": "godot_docs",
        "docs_path": DOCS_PATH / "godot",
        "url_base": "https://docs.godotengine.org/en/stable",
        "description": "Godot Engine 4.x Documentation"
    }
}


def index_engine_docs(engine: str):
    """Index documentation for a specific engine"""
    logger.info("indexing_engine_docs", engine=engine)
    
    if engine not in ENGINE_CONFIGS:
        raise ValueError(f"Unknown engine: {engine}. Use: unity, unreal, godot")
    
    config = ENGINE_CONFIGS[engine]
    docs_path = config["docs_path"]
    
    if not docs_path.exists():
        logger.error("docs_path_not_found", path=str(docs_path))
        print(f"\n❌ Documentation not found at {docs_path}")
        print(f"📥 Please download {engine.title()} docs to: {docs_path}")
        print(f"   URL: {config['url_base']}")
        return
    
    # Load documents
    logger.info("loading_documents", path=str(docs_path))
    loader = DirectoryLoader(
        str(docs_path),
        glob="**/*.md",
        loader_cls=UnstructuredMarkdownLoader,
        show_progress=True
    )
    documents = loader.load()
    
    logger.info("documents_loaded", count=len(documents))
    print(f"✅ Loaded {len(documents)} documents from {docs_path}")
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    
    logger.info("chunks_created", count=len(chunks))
    print(f"📄 Created {len(chunks)} chunks for indexing")
    
    # Add metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["engine"] = engine
        chunk.metadata["source"] = config["description"]
        chunk.metadata["chunk_id"] = i
    
    # Create embeddings and index
    logger.info("creating_embeddings")
    print("🔄 Creating embeddings (this may take a while)...")
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # Create or update vector store
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=config["collection"],
        persist_directory=str(CHROMADB_PATH)
    )
    
    logger.info("indexing_complete", engine=engine, chunks=len(chunks))
    print(f"✅ {engine.title()} documentation indexed successfully!")
    print(f"   Collection: {config['collection']}")
    print(f"   Chunks: {len(chunks)}")
    print(f"   Storage: {CHROMADB_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Index game engine documentation")
    parser.add_argument(
        "--engine",
        choices=["unity", "unreal", "godot"],
        help="Engine to index"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Index all engines"
    )
    
    args = parser.parse_args()
    
    if args.all:
        for engine in ENGINE_CONFIGS.keys():
            print(f"\n{'='*60}")
            print(f"Indexing {engine.title()} Documentation")
            print('='*60)
            try:
                index_engine_docs(engine)
            except Exception as e:
                logger.exception("indexing_failed", engine=engine, error=str(e))
                print(f"❌ Failed to index {engine}: {e}")
    elif args.engine:
        index_engine_docs(args.engine)
    else:
        parser.print_help()
        print("\n💡 Example: python scripts/index_engine_docs.py --engine unity")


if __name__ == "__main__":
    main()
