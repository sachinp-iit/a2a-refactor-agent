# agents/embedding_agent.py
import os
import uuid
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

class EmbeddingAgent:
    def __init__(
        self,
        issues: List[Dict],
        chroma_client,
        collection_name: str = "roslynator_issues",
        repo_root: Optional[str] = None,
    ):
        if chroma_client is None:
            raise ValueError("chroma_client must be provided")
        self.issues = issues or []
        self.chroma_client = chroma_client
        self.collection_name = collection_name
        self.repo_root = repo_root
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def _abs_path(self, file_path: str) -> str:
        if not file_path:
            return ""
        if self.repo_root and not os.path.isabs(file_path):
            return os.path.abspath(os.path.join(self.repo_root, file_path))
        return os.path.abspath(file_path)

    def store_embeddings(self, clear_existing: bool = False) -> int:
        """
        Store issues into ChromaDB using local embeddings.
        - No JSON reading.
        - Converts relative file paths to absolute using repo_root.
        - Skips duplicates based on (ruleId/id + abs path + line).
        """
        if not self.issues:
            print("[EmbeddingAgent] No issues provided.")
            return 0

        if clear_existing:
            try:
                self.chroma_client.delete_collection(self.collection_name)
            except Exception:
                pass

        collection = self.chroma_client.get_or_create_collection(self.collection_name)

        # Gather existing ids to prevent duplicates
        existing_ids = set()
        if collection.count() > 0:
            got = collection.get(include=["ids"])
            ids_field = got.get("ids", [])
            # Chroma can return flat or nested lists; normalize
            for item in ids_field:
                if isinstance(item, list):
                    existing_ids.update(item)
                else:
                    existing_ids.add(item)

        inserted = 0
        for issue in self.issues:
            rule = issue.get("id") or issue.get("ruleId") or str(uuid.uuid4())
            file_rel = issue.get("file", "")
            file_abs = self._abs_path(file_rel)
            line = issue.get("line", -1)
            unique_key = f"{rule}:{file_abs}:{line}"

            if unique_key in existing_ids:
                continue

            metadata = {
                "file": file_abs,
                "line": line,
                "column": issue.get("column", -1),
                "severity": issue.get("severity", ""),
                "id": rule,
                "issue":
