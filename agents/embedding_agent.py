import json
from pathlib import Path
from chromadb import Client
from chromadb.config import Settings
from openai import OpenAI

class EmbeddingAgent:
    def __init__(self, json_report_path: str, db_dir: str, collection_name: str = "roslynator_issues"):
        self.json_report_path = Path(json_report_path)
        self.db_dir = Path(db_dir)
        self.collection_name = collection_name

        # Initialize Chroma client
        self.chroma_client = Client(Settings(persist_directory=str(self.db_dir)))

        # Initialize OpenAI client
        self.openai_client = OpenAI()

    def store_embeddings(self):
        if not self.json_report_path.exists():
            print(f"[EmbeddingAgent] JSON report not found at {self.json_report_path}")
            return

        with open(self.json_report_path, "r", encoding="utf-8") as f:
            issues = json.load(f)

        if not issues:
            print("[EmbeddingAgent] No issues to embed.")
            return

        # Prepare embeddings list first
        embeddings = []
        for idx, issue in enumerate(issues):
            try:
                document_text = (
                    f"This is a code analysis issue with ID {issue.get('id', 'N/A')}. "
                    f"It occurs in the file {issue.get('file', 'unknown')} on line {issue.get('line', 'N/A')}. "
                    f"The severity of the issue is {issue.get('severity', 'unknown')}. "
                    f"The message describing the issue is: {issue.get('message', '')}. "
                    f"This might relate to C# compiler warnings or best practices violations."
                ).lower()
                embedding = self._get_embedding(document_text)
                embeddings.append(embedding)
            except Exception as e:
                print(f"[EmbeddingAgent] Failed to generate embedding for issue {idx}: {e}")
                embeddings.append([0.0] * 1536)  # fallback dummy embedding

        # Store in ChromaDB exactly like your earlier function
        collection = self.chroma_client.get_or_create_collection(name=self.collection_name)

        for i, issue in enumerate(issues):
            metadata = {
                "file": issue.get("file", ""),
                "id": issue.get("id", ""),
                "severity": issue.get("severity", ""),
                "message": issue.get("message", ""),
                "line": issue.get("line", "")
            }

            document_text = (
                f"This is a code analysis issue with ID {issue.get('id', 'N/A')}. "
                f"It occurs in the file {issue.get('file', 'unknown')} on line {issue.get('line', 'N/A')}. "
                f"The severity of the issue is {issue.get('severity', 'unknown')}. "
                f"The message describing the issue is: {issue.get('message', '')}. "
                f"This might relate to C# compiler warnings or best practices violations."
            ).lower()

            collection.add(
                documents=[document_text],
                metadatas=[metadata],
                ids=[f"issue_{i}"],
                embeddings=[embeddings[i]]
            )

        print(f"[EmbeddingAgent] Stored {len(issues)} issues into ChromaDB.")

    def _get_embedding(self, text: str):
        """
        Generates OpenAI embeddings for the given text.
        """
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
