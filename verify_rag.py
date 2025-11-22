from core.rag.rag_engine import RAGEngine
import shutil
import os

def test_rag():
    # Setup
    persist_dir = "./data/test_chroma_db"
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
    
    print("Initializing RAG Engine...")
    rag = RAGEngine(persist_directory=persist_dir)
    
    # Add documents
    docs = ["Unity uses C# for scripting.", "Unreal Engine uses C++ and Blueprints."]
    metadatas = [{"source": "unity"}, {"source": "unreal"}]
    ids = ["doc1", "doc2"]
    
    print("Adding documents...")
    rag.add_documents(docs, metadatas, ids)
    
    # Query
    print("Querying 'scripting language'...")
    results = rag.query("scripting language", n_results=1)
    
    print("Results:", results)
    
    # Verify
    if results and "C#" in results[0]['content']:
        print("SUCCESS: Retrieved correct document.")
    else:
        print("FAILURE: Did not retrieve expected document.")

if __name__ == "__main__":
    test_rag()
