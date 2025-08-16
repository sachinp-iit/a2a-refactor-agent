from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class QueryAgent:
    def __init__(self, db_dir: str, collection_name: str = "roslynator_issues"):
        self.db_dir = db_dir
        self.collection_name = collection_name
        self.client = Client(Settings(persist_directory=str(self.db_dir)))
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def search_issues(self, query: str, top_k: int = 5):
        collection = self.client.get_collection(self.collection_name)
        query_embedding = self.model.encode([query])[0].tolist()
    
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
    
        # Summarize all stored issues (useful for count queries or broad ones)
        total_issues = collection.count()
    
        formatted_results = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            formatted_results.append({
                "file": meta.get("file", "unknown"),
                "line": meta.get("line", -1),
                "severity": meta.get("severity", "unknown"),
                "message": meta.get("message", ""),
                "match": doc
            })
    
        return {
            "query": query,
            "total_issues": total_issues,
            "top_matches": formatted_results
        }
