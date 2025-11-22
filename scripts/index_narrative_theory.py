"""
Narrative Theory Indexer for LUDEX Framework

Indexes narrative theory books (Save the Cat, Story, Writer's Journey, etc.)
into ChromaDB for semantic search by NarrativeArchitect and related agents.

Usage:
    python scripts/index_narrative_theory.py
"""

import structlog
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

logger = structlog.get_logger(__name__)

# Configuration
CHROMADB_PATH = Path("data/chromadb")
NARRATIVE_BOOKS_PATH = Path("data/narrative_theory")

NARRATIVE_SOURCES = {
    "save_the_cat": {
        "title": "Save the Cat! by Blake Snyder",
        "framework": "Save the Cat (15 beats)",
        "file_pattern": "*save*cat*.pdf"
    },
    "story": {
        "title": "Story by Robert McKee",
        "framework": "McKee's Story Principles",
        "file_pattern": "*story*mckee*.pdf"
    },
    "writers_journey": {
        "title": "The Writer's Journey by Christopher Vogler",
        "framework": "Writer's Journey (12 stages)",
        "file_pattern": "*writer*journey*.pdf"
    },
    "heros_journey": {
        "title": "The Hero with a Thousand Faces by Joseph Campbell",
        "framework": "Hero's Journey (Monomyth)",
        "file_pattern": "*hero*thousand*.pdf"
    }
}


def index_narrative_theory():
    """Index narrative theory books into ChromaDB"""
    logger.info("indexing_narrative_theory")
    
    if not NARRATIVE_BOOKS_PATH.exists():
        logger.error("narrative_books_path_not_found", path=str(NARRATIVE_BOOKS_PATH))
        print(f"\n❌ Narrative theory books not found at {NARRATIVE_BOOKS_PATH}")
        print(f"📥 Please add PDF books to: {NARRATIVE_BOOKS_PATH}")
        print("\nExpected books:")
        for source in NARRATIVE_SOURCES.values():
            print(f"  - {source['title']}")
        return
    
    all_chunks = []
    
    # Process each narrative source
    for source_key, source_info in NARRATIVE_SOURCES.items():
        logger.info("processing_narrative_source", source=source_key)
        print(f"\n📖 Processing: {source_info['title']}")
        
        # Find PDF files matching pattern
        pdf_files = list(NARRATIVE_BOOKS_PATH.glob(source_info["file_pattern"]))
        
        if not pdf_files:
            print(f"   ⚠️  No files found matching: {source_info['file_pattern']}")
            continue
        
        for pdf_file in pdf_files:
            print(f"   📄 Loading: {pdf_file.name}")
            
            # Load PDF
            loader = PyPDFLoader(str(pdf_file))
            pages = loader.load()
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=150,
                length_function=len,
            )
            chunks = text_splitter.split_documents(pages)
            
            # Add metadata
            for chunk in chunks:
                chunk.metadata["source"] = source_info["title"]
                chunk.metadata["framework"] = source_info["framework"]
                chunk.metadata["source_key"] = source_key
            
            all_chunks.extend(chunks)
            print(f"   ✅ Created {len(chunks)} chunks")
    
    if not all_chunks:
        print("\n❌ No narrative theory documents found to index")
        return
    
    # Create embeddings and index
    logger.info("creating_embeddings", total_chunks=len(all_chunks))
    print(f"\n🔄 Creating embeddings for {len(all_chunks)} chunks...")
    print("   (This may take several minutes)")
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # Create vector store
    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        collection_name="narrative_theory",
        persist_directory=str(CHROMADB_PATH)
    )
    
    logger.info("indexing_complete", chunks=len(all_chunks))
    print(f"\n✅ Narrative theory indexed successfully!")
    print(f"   Collection: narrative_theory")
    print(f"   Total chunks: {len(all_chunks)}")
    print(f"   Storage: {CHROMADB_PATH}")
    
    # Print summary
    print("\n📊 Indexed frameworks:")
    framework_counts = {}
    for chunk in all_chunks:
        framework = chunk.metadata.get("framework", "Unknown")
        framework_counts[framework] = framework_counts.get(framework, 0) + 1
    
    for framework, count in framework_counts.items():
        print(f"   - {framework}: {count} chunks")


if __name__ == "__main__":
    index_narrative_theory()
