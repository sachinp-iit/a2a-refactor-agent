from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from collections import Counter

class QueryAgent:
    def __init__(self, collection_name: str = "roslynator_issues", chroma_client=None):
        self.collection_name = collection_name
        if chroma_client is None:
            raise ValueError("chroma_client must be provided")
        self.chroma_client = chroma_client
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def _get_all_issues(self):
        collection = self.chroma_client.get_collection(self.collection_name)
        if collection.count() == 0:
            return []
        results = collection.get(include=["metadatas"], limit=collection.count())
        issues = []
        for m in results.get("metadatas", []):
            if isinstance(m, dict):
                issues.append({
                    "file": m.get("file", "unknown"),
                    "line": m.get("line", -1),
                    "column": m.get("column", -1),
                    "severity": m.get("severity", "unknown"),
                    "issue": m.get("issue") or m.get("message", "unknown"),
                    "id": m.get("id", "unknown"),
                })
        return issues

    def search_issues(self, query_text: str, top_k: int = 5):
        query_text_l = (query_text or "").lower().strip()
        collection = self.chroma_client.get_collection(self.collection_name)
        if collection.count() == 0:
            print("[QueryAgent] No issues found in the database.")
            return []
        
        # Load all issues from collection
        issues = self._get_all_issues()
        total = len(issues)

        # --- Special queries ---
        if "which agent" in query_text_l or query_text_l == "agent" or " agent " in f" {query_text_l} ":
            unique_files = sorted(set(i["file"] for i in issues if i["file"]))
            return [{"file": "(summary)", "issue": f"Issues found in files: {unique_files}"}]

        if query_text_l in ("all", "show all issues", "list issues"):
            return issues

        if "how many" in query_text_l or "count" in query_text_l or query_text_l == "total":
            return [{"file": "(summary)", "issue": f"Total issues: {total}"}]

        if "categories" in query_text_l or "types" in query_text_l:
            cats = Counter(i["id"] for i in issues if i["id"])
            return [{"file": "(summary)", "issue": f"Issue categories: {dict(cats)}"}]

        if "high severity" in query_text_l or "errors" in query_text_l or "error" in query_text_l:
            return [i for i in issues if str(i["severity"]).lower() in ("error", "high")]

        # --- Default semantic search ---
        query_embedding = self.model.encode([query_text])[0].tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["metadatas", "distances"],
        )
    
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        clean_results = []
        for i, m in enumerate(metadatas):
            if not isinstance(m, dict):
                continue
            clean_results.append({
                "file": m.get("file", "unknown"),
                "line": m.get("line", -1),
                "column": m.get("column", -1),
                "severity": m.get("severity", "unknown"),
                "issue": m.get("issue") or m.get("message", "unknown"),
                "id": m.get("id", "unknown"),
                "distance": distances[i] if i < len(distances) else None,
            })

        clean_results.sort(key=lambda x: (x.get("distance") is None, x.get("distance", 0)))
        return clean_results

    def query_issues(self):
        query_text = input("Enter your search query (or blank to cancel): ").strip()
        if not query_text:
            print("Query cancelled.")
            return
        results = self.search_issues(query_text)
        if not results:
            print("No matching issues found.")
            return

        # Pretty print
        if results[0].get("file") == "(summary)":
            for r in results:
                print(r["issue"])
        else:
            print(f"\nTop {len(results)} issues:")
            for i, res in enumerate(results, 1):
                print(
                    f"{i}. File: {res.get('file','unknown')}\n"
                    f"   Line: {res.get('line','unknown')}, Column: {res.get('column','unknown')}\n"
                    f"   Severity: {res.get('severity','unknown')}\n"
                    f"   Issue: {res.get('issue','unknown')}\n"
                )

    def is_ready(self) -> bool:
        try:
            col = self.chroma_client.get_collection(self.collection_name)
            return col.count() > 0
        except Exception:
            return False
