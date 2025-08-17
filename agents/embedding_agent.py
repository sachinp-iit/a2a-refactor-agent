import json
import uuid
from pathlib import Path
from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class EmbeddingAgent:
    def __init__(self, json_report_path: str, db_dir: str, collection_name: str = "roslynator_issues"):
        self.json_report_path = Path(json_report_path)
        self.db_dir = Path(db_dir)
        self.collection_name = collection_name
        self.chroma_client = SHARED_CHROMA_CLIENT
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def store_embeddings(self, clear_existing: bool = False):
        """
        Store issues from JSON report into ChromaDB using local embeddings.
        Optionally clears existing issues to avoid duplicates.
        """
        if not self.json_report_path.exists():
            raise FileNotFoundError(f"JSON report not found at {self.json_report_path}")

        with open(self.json_report_path, "r", encoding="utf-8") as f:
            issues = json.load(f)

        if not issues:
            raise ValueError("No issues found in JSON report.")

        if clear_existing:
            self.chroma_client.delete_collection(name=self.collection_name)

        collection = self.chroma_client.get_or_create_collection(name=self.collection_name)

        existing_ids = set()
        if collection.count() > 0:
            ids_resp = collection.get(include=["ids"])
            existing_ids = set(ids_resp.get("ids", []))

        inserted = 0        
        for i, issue in enumerate(issues):
            issue_id = issue.get("id") or issue.get("ruleId") or str(uuid.uuid4())
            unique_key = f"issue_{issue_id}"

            if unique_key in existing_ids:
                continue  # skip duplicate

            metadata = {
                "file": issue.get("file", "unknown"),
                "id": issue_id,
                "severity": issue.get("severity", "unknown"),
                "message": issue.get("message", ""),
                "line": issue.get("line", -1)
            }

            document_text = (
                f"Issue {issue_id} in file {metadata['file']} line {metadata['line']}. "
                f"Severity: {metadata['severity']}. "
                f"Message: {metadata['message']}"
            ).lower()

            embedding = self.model.encode([document_text])[0].tolist()

            collection.add(
                documents=[document_text],
                metadatas=[metadata],
                ids=[unique_key],
                embeddings=[embedding]
            )
            inserted += 1

        print(f"[EmbeddingAgent] Stored {inserted} new issues (duplicates skipped).")
