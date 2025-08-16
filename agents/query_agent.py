from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from collections import Counter

class QueryAgent:
    def __init__(self, db_dir: str, collection_name: str = "roslynator_issues"):
        self.db_dir = db_dir
        self.collection_name = collection_name
        self.client = Client(Settings(persist_directory=str(self.db_dir)))
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def search_issues(self, query_text: str, top_k: int = 5):
        """
        Searches issues in ChromaDB based on a text query.
        Returns top_k matching issues with file, message, and severity.
        """
        collection = self.chroma_client.get_collection(self.collection_name)
        if collection.count() == 0:
            print("[QueryAgent] No issues found in the database.")
            return []
    
        # Generate embedding for the query
        query_embedding = self.model.encode([query_text])[0].tolist()
    
        # Perform similarity search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
    
        metadatas = results.get("metadatas", [[]])[0]
    
        # Filter only valid metadata dictionaries with high severity or errors
        filtered_meta_ids = {
            i for i, m in enumerate(metadatas)
            if isinstance(m, dict) and m.get("severity", "").lower() in ("error", "high")
        }
    
        # Build clean results list
        clean_results = [
            {
                "file": m.get("file", "unknown"),
                "issue": m.get("message", "unknown"),
                "severity": m.get("severity", "unknown")
            }
            for i, m in enumerate(metadatas)
            if i in filtered_meta_ids and isinstance(m, dict)
        ]
    
        return clean_results

    # New helper to handle user input and display
    def query_issues(self):
        query_text = input("Enter your search query (or blank to cancel): ").strip()
        if not query_text:
            print("Query cancelled.")
            return
        results = self.search_issues(query_text)
        if not results:
            print("No matching issues found.")
            return
        print(f"\nTop {len(results)} matching issues:")
        for i, res in enumerate(results, 1):
            if "count" in res:
                print(f"{i}. File: {res['file']} | Issues: {res['count']}")
            else:
                print(f"{i}. File: {res['file']}\n   Line: {res['line']}\n   Severity: {res['severity']}\n   Issue: {res['issue']}\n")

    # Check if the ChromaDB collection exists and has data.    
    def is_ready(self) -> bool:
        try:
            col = self.client.get_collection(self.collection_name)
            return col.count() > 0
        except Exception:
            return False
