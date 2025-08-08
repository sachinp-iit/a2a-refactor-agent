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

        self.client = Client(Settings(
            persist_directory=str(self.db_dir)
        ))

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

        collection = self.client.get_or_create_collection(self.collection_name)

        for idx, item in enumerate(issues):
            text = f"File: {item['file']}\nIssue: {item['issue']}"
            embedding = self._get_embedding(text)

            collection.add(
                ids=[f"issue_{idx}"],
                documents=[text],
                embeddings=[embedding],
                metadatas=[{"file": item['file']}]
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
