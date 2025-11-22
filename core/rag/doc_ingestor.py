import os
from typing import List, Dict
from core.rag.rag_engine import RAGEngine
# We'll use a simple text splitter for now, or markitdown if installed
# Assuming markitdown is for converting files, we might just read text files for now.

class DocIngestor:
    """
    Ingests documentation into the RAG Engine.
    """
    
    def __init__(self, rag_engine: RAGEngine):
        self.rag_engine = rag_engine

    def ingest_text_file(self, file_path: str, source_type: str = "unity_docs"):
        """
        Ingests a single text/markdown file.
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple chunking (can be improved with LangChain TextSplitter)
        chunk_size = 1000
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        
        ids = [f"{os.path.basename(file_path)}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": source_type, "filename": os.path.basename(file_path), "chunk_index": i} for i in range(len(chunks))]
        
        self.rag_engine.add_documents(chunks, metadatas, ids)
        print(f"Ingested {len(chunks)} chunks from {file_path}")

    def ingest_directory(self, directory_path: str, source_type: str):
        """
        Ingests all .md and .txt files in a directory.
        """
        if not os.path.exists(directory_path):
            print(f"Directory not found: {directory_path}")
            return

        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".md") or file.endswith(".txt"):
                    full_path = os.path.join(root, file)
                    self.ingest_text_file(full_path, source_type)
