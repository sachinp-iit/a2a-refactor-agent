from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import re
from collections import Counter

class QueryAgent:
    def __init__(self, db_dir: str, collection_name: str = "roslynator_issues"):
        self.db_dir = db_dir
        self.collection_name = collection_name
        self.client = Client(Settings(persist_directory=str(self.db_dir)))
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def search_issues(self, query: str, top_k: int = 5):
        collection = self.client.get_collection(self.collection_name)
        all_data = collection.get(include=["documents", "metadatas"])
        issues = all_data["metadatas"]

        q = query.lower()
        filtered = issues

        if "warning" in q:
            filtered = [i for i in issues if i.get("severity", "").lower() == "warning"]
        elif "error" in q or "high severity" in q:
            filtered = [i for i in issues if i.get("severity", "").lower() in ["error", "high"]]
        elif "file with high number of issues" in q:
            files = [i.get("file", "unknown") for i in issues]
            counts = Counter(files)
            top_files = counts.most_common(top_k)
            return {"query": query, "top_files": top_files, "total_issues": len(issues)}

        if not filtered:
            return {"query": query, "top_matches": [], "total_issues": len(issues)}

        query_embedding = self.model.encode([query])[0].tolist()
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

        formatted_results = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            formatted_results.append({
                "file": meta.get("file", "unknown"),
                "line": meta.get("line", -1),
                "severity": meta.get("severity", "unknown"),
                "message": meta.get("message", ""),
                "match": doc
            })

        return {"query": query, "top_matches": formatted_results, "total_issues": len(filtered)}
