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
        self.chroma_client = Client(Settings(persist_directory=str(self.db_dir)))
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def store_embeddings(self):
        """
        Store issues from JSON report into ChromaDB using local embeddings.
        """
        if not self.json_report_path.exists():
            raise FileNotFoundError(f"JSON report not found at {self.json_report_path}")

        with open(self.json_report_path, "r", encoding="utf-8") as f:
            issues = json.load(f)

        if not issues:
            raise ValueError("No issues found in JSON report.")

        collection = self.chroma_client.get_or_create_collection(name=self.collection_name)

        for i, issue in enumerate(issues):
            issue_id = issue.get("id") or issue.get("ruleId") or str(uuid.uuid4())

            metadata = {
                "file": issue.get("file", "unknown"),
                "id": issue_id,
                "severity": issue.get("severity", "unknown"),
                "message": issue.get("message", ""),
                "line": issue.get("line", -1)
            }

            # Rich contextual text
            document_text = (
                f"Issue {issue_id} in file {metadata['file']} line {metadata['line']}. "
                f"Severity: {metadata['severity']}. "
                f"Message: {metadata['message']}"
            ).lower()

            embedding = self.model.encode([document_text])[0].tolist()

            collection.add(
                documents=[document_text],
                metadatas=[metadata],
                ids=[f"issue_{i}"],
                embeddings=[embedding]
            )

        print(f"[EmbeddingAgent] Stored {len(issues)} issues into ChromaDB with local embeddings.")
