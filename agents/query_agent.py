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
    
        # safe get + flatten
        all_data = collection.get(include=["documents", "metadatas"])
        metadatas_batches = all_data.get("metadatas", []) or []
        documents_batches = all_data.get("documents", []) or []
        metadatas = [m for batch in metadatas_batches for m in batch]
        documents = [d for batch in documents_batches for d in batch]
    
        from collections import Counter
        q = query.lower()
    
        # rule-based -> file counts
        if "file with high" in q or "most issues" in q or "file with most" in q:
            files = [m.get("file", "unknown") for m in metadatas]
            top_files = Counter(files).most_common(top_k)
            return [{"file": f, "count": c} for f, c in top_files]
    
        # rule-based severity filtering (if mentioned)
        filtered_meta_ids = None
        if "warning" in q:
            filtered_meta_ids = {i for i,m in enumerate(metadatas) if m.get("severity","").lower()=="warning"}
        elif "error" in q or "high severity" in q:
            filtered_meta_ids = {i for i,m in enumerate(metadatas) if m.get("severity","").lower() in ("error","high")}
    
        # semantic search
        query_embedding = self.model.encode([query])[0].tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas"]
        )
    
        docs = (results.get("documents") or [[]])[0]
        metas = (results.get("metadatas") or [[]])[0]
    
        out = []
        for doc, meta in zip(docs, metas):
            # if a severity filter was set, skip non-matching entries
            if filtered_meta_ids is not None:
                # find index of this meta in the flattened metadatas list
                # (match by file+line+message fallback when ids not present)
                if meta not in metadatas:
                    continue
                idx = metadatas.index(meta)
                if idx not in filtered_meta_ids:
                    continue
            out.append({
                "file": meta.get("file", "unknown"),
                "line": meta.get("line", -1),
                "severity": meta.get("severity", "unknown"),
                "message": meta.get("message", ""),
                "match": doc
            })
    
        return out
