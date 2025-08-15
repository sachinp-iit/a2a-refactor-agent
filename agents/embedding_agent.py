# agents/embedding_agent.py

import json
from pathlib import Path
from chromadb import Client
from chromadb.config import Settings

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
            metadata = {
                "file": issue["file"],
                "id": issue["id"],
                "severity": issue["severity"],
                "message": issue["message"],
                "line": issue["line"]
            }

            # Construct verbose, contextual document text
            document_text = (
                f"This is a code analysis issue with ID {issue['id']}. "
                f"It occurs in the file {issue['file']} on line {issue['line']}. "
                f"The severity of the issue is {issue['severity']}. "
                f"The message describing the issue is: {issue['message']}. "
                f"This might relate to C# compiler warnings or best practices violations."
            ).lower()

            collection.add(
                documents=[document_text],
                metadatas=[metadata],
                ids=[f"issue_{i}"],
                embeddings=[embeddings[i]]
            )

        print(f"[EmbeddingAgent] Stored {len(issues)} issues into ChromaDB (dummy embeddings).")
