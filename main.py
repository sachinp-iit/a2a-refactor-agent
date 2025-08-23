import os
import sys
import shutil
import subprocess
import json
from chromadb import Client
from chromadb.config import Settings

# Suppress TensorFlow CUDA warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["XLA_FLAGS"] = "--xla_gpu_cuda_data_dir=/dev/null"

# --- Agents imports ---
from agents.repo_manager import RepoManager
from agents.roslynator_agent import RoslynatorAgent
from agents.embedding_agent import EmbeddingAgent
from agents.query_agent import QueryAgent
from agents.refactor_agent import RefactorAgent
from agents.approval_agent import ApprovalAgent
from agents.reporting_agent import ReportingAgent

# --- Globals ---
DB_DIR = "chroma_db"
COLLECTION_NAME = "roslynator_issues"  # Define a default collection name

# Initialize shared Chroma client
try:
    SHARED_CHROMA_CLIENT = Client(Settings(persist_directory=DB_DIR))
except ValueError:
    SHARED_CHROMA_CLIENT = Client(Settings())

def is_chromadb_ready(client, collection_name=COLLECTION_NAME) -> bool:
    try:
        col = client.get_collection(collection_name)
        return col.count() > 0
    except Exception:
        return False
        
def main_menu():
    repo_manager = RepoManager()
    query_agent = None
    repo_path = None  # track last cloned repo path

    while True:
        print("\n===== C# Auto-Refactor Agent Menu =====")
        print("1. Clone GitHub repo and run Roslynator analysis")
        print("2. Query code issues by keyword")
        print("3. Show Roslynator report")
        print("4. Run approval and auto-refactor loop")        
        print("5. Exit")

        choice = input("Select an option [1-5]: ").strip()

        if choice == "1":
            repo_url = input("Enter the GitHub repo URL to clone: ").strip()
            
            if not repo_url:
                print("Repository URL is required.")
                continue
    
            repo_path = repo_manager.clone_repo(repo_url)
            cs_files = repo_manager.list_csharp_files(repo_path)
            
            if not cs_files:
                print("No C# files found in the repository.")
                continue
    
            roslynator_agent = RoslynatorAgent(
                repo_path=repo_path,
                output_dir=os.path.join(repo_path, "analysis")
            )
            
            # run analysis → get issues list (not JSON path anymore)
            issues = roslynator_agent.run_analysis()
            if not issues or len(issues) == 0:
                print("No issues found in Roslynator analysis. Skipping embedding.")
                continue
    
            # store issues in ChromaDB
            embedding_agent = EmbeddingAgent(
                issues=issues,
                chroma_client=SHARED_CHROMA_CLIENT,
                repo_root=repo_path
            )
            embedding_agent.store_embeddings()
    
            # prepare query agent bound to this repo
            query_agent = QueryAgent(
                db_dir=os.path.join(repo_path, "chroma_db"),
                chroma_client=SHARED_CHROMA_CLIENT
            )
    
            print("Clone and analysis complete.")

        elif choice == "2":
            if query_agent is None:
                repo_db_dir = os.path.join(repo_path, "chroma_db") if repo_path else DB_DIR
                if is_chromadb_ready(SHARED_CHROMA_CLIENT):
                    query_agent = QueryAgent(db_dir=repo_db_dir, chroma_client=SHARED_CHROMA_CLIENT)
                    repo_path = repo_path or DB_DIR
                else:
                    print("No ChromaDB data found. Please run clone and analysis first.")
                    continue

            query_text = input("Enter your search query (or blank to cancel): ").strip()
            if not query_text:
                print("Query cancelled.")
                continue

            results = query_agent.search_issues(query_text)
            if not results:
                print("No matching issues found.")
                continue

            print(f"\nTop {len(results)} matching issues:")
            for i, res in enumerate(results, 1):
                print(f"{i}. File: {res.get('file')}\n   Issue: {res.get('issue')}\n")

        elif choice == "3":
            if not repo_path:
                print("No repository analyzed yet.")
                continue
            # pass the shared Chroma client into ReportingAgent (do NOT pass a path string)
            reporting_agent = ReportingAgent(chroma_client=SHARED_CHROMA_CLIENT)
            reporting_agent.show_all()

        elif choice == "4":
            if not repo_path:
                print("No repository analyzed yet.")
                continue
        
            refactor_agent = RefactorAgent(
                chroma_client=SHARED_CHROMA_CLIENT,
                repo_root=repo_path
            )
            refactor_agent.approval_and_refactor_loop()        
            
        elif choice == "5":
            print("Exiting. Goodbye!")
            break
            
        else:
            print("Invalid option. Please enter 1, 2, 3, 4 or 5.")

if __name__ == "__main__":
    main_menu()
