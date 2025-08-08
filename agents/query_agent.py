from chromadb import Client
from chromadb.config import Settings
from openai import OpenAI

class QueryAgent:
    def __init__(self, db_dir: str, collection_name: str = "roslynator_issues"):
        self.db_dir = db_dir
        self.collection_name = collection_name
        self.client = Client(Settings(
            persist_directory=str(self.db_dir)
        ))
        self.openai_client = OpenAI()

    def search_issues(self, query: str, top_k: int = 5):
        collection = self.client.get_collection(self.collection_name)
        query_embedding = self._get_embedding(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        formatted_results = []
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            formatted_results.append({
                "file": meta['file'],
                "issue": doc
            })

        return formatted_results

    def _get_embedding(self, text: str):
        """
        Generates OpenAI embeddings for the given text.
        """
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
