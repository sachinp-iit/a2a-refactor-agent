# agents/embedding_agent.py

import json
from pathlib import Path
from chromadb import Client
from chromadb.config import Settings
import uuid

class EmbeddingAgent:
    def __init__(self, json_report_path: str, db_dir: str, collection_name: str = "roslynator_issues"):
        self.json_report_path = Path(json_report_path)
        self.db_dir = Path(db_dir)
        self.collection_name = collection_name

        # Initialize Chroma client
        self.chroma_client = Client(Settings(persist_directory=str(self.db_dir)))

    def store_embeddings(self):
        """
        Store issues from JSON report into ChromaDB.
        Embeddings are automatically generated as dummy vectors.
        """
        if not self.json_report_path.exists():
            raise FileNotFoundError(f"JSON report not found at {self.json_report_path}")

        with open(self.json_report_path, "r", encoding="utf-8") as f:
            issues = json.load(f)

        if not issues:
            raise ValueError("No issues found in JSON report.")

        # Generate placeholder embeddings (all zeros) for each issue
        embeddings = [[0.0] * 1536 for _ in issues]

        collection = self.chroma_client.get_or_create_collection(name=self.collection_name)

        for i, issue in enumerate(issues):
            # inside the for loop over issues:
            issue_id = issue.get("id") or issue.get("ruleId") or str(uuid.uuid4())
            severity = issue.get("severity") or issue.get("level") or "unknown"
            message = issue.get("message", "")

            # Extract file and line safely from SARIF-style locations
            file = (
                issue.get("file") or
                issue.get("locations", [{}])[0].get("physicalLocation", {}).get("artifactLocation", {}).get("uri", "unknown")
            )
            
            line = (
                issue.get("line") or
                issue.get("locations", [{}])[0].get("physicalLocation", {}).get("region", {}).get("startLine", -1)
            )
            
            metadata = {
                "id": issue_id,
                "file": file,
                "severity": severity,
                "message": message,
                "line": line
            }

            # Construct verbose, contextual document text
            document_text = (
                f"This is a code analysis issue with ID {issue_id}. "
                f"It occurs in the file {file} on line {line}. "
                f"The severity of the issue is {severity}. "
                f"The message describing the issue is: {message}. "
                f"This might relate to C# compiler warnings or best practices violations."
            ).lower()

            collection.add(
                documents=[document_text],
                metadatas=[metadata],
                ids=[f"issue_{i}"],
                embeddings=[embeddings[i]]
            )

        print(f"[EmbeddingAgent] Stored {len(issues)} issues into ChromaDB (dummy embeddings).")
