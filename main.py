import os
import sys
import shutil
import subprocess
from chromadb import Client
from chromadb.config import Settings

# --- keep all agents imports ---
from agents.repo_manager import RepoManager
from agents.roslynator_agent import RoslynatorAgent
from agents.embedding_agent import EmbeddingAgent
from agents.query_agent import QueryAgent
from agents.refactor_agent import RefactorAgent
from agents.approval_agent import ApprovalAgent

# --- add globals ---
DB_DIR = "chroma_db"
COLLECTION_NAME = "roslynator_issues"

def is_chromadb_ready(db_dir: str = DB_DIR, collection_name: str = COLLECTION_NAME) -> bool:
    try:
        client = Client(Settings(persist_directory=db_dir))
        col = client.get_collection(collection_name)
        return col.count() > 0
    except Exception:
        return False

def ensure_roslynator_installed():
    """
    Ensures that Roslynator CLI is installed and available in PATH.
    If missing, installs it using the provided shell script.
    """
    if shutil.which("roslynator"):        
        return        

    if not os.path.exists("install_dotnet_roslynator.sh"):
        print("[Main] ERROR: install_dotnet_roslynator.sh not found.")
        return

    subprocess.run(["bash", "install_dotnet_roslynator.sh"], check=True)

    dotnet_root = os.path.expanduser("~/.dotnet")
    dotnet_tools = os.path.expanduser("~/.dotnet/tools")

    # Only add if not already in PATH
    path_parts = os.environ["PATH"].split(":")
    if dotnet_root not in path_parts:
        os.environ["PATH"] += f":{dotnet_root}"
    if dotnet_tools not in path_parts:
        os.environ["PATH"] += f":{dotnet_tools}"

    os.environ["DOTNET_ROOT"] = dotnet_root

def main_menu():
    repo_manager = RepoManager()
    query_agent = None

    while True:
        print("\n===== C# Auto-Refactor Agent Menu =====")
        print("1. Clone GitHub repo and run Roslynator analysis")
        print("2. Query code issues by keyword")
        print("3. Run approval and auto-refactor loop")
        print("4. Exit")

        choice = input("Select an option [1-4]: ").strip()

        if choice == "1":
            # Delegate to RepoManager and other agents
            repo_url = input("Enter the GitHub repo URL to clone: ").strip()
            if not repo_url:
                print("Repository URL is required.")
                continue

            repo_path = repo_manager.clone_repo(repo_url)
            cs_files = repo_manager.list_csharp_files(repo_path)
            if not cs_files:
                print("No C# files found in the repository.")
                continue

            ensure_roslynator_installed()

            roslynator_agent = RoslynatorAgent(repo_path=repo_path, output_dir=os.path.join(repo_path, "analysis"))
            json_report_path = roslynator_agent.run_analysis()
            if not json_report_path:
                print("Roslynator analysis failed or no report generated.")
                continue

            embedding_agent = EmbeddingAgent(json_report_path=json_report_path, db_dir=os.path.join(repo_path, "chroma_db"))
            embedding_agent.store_embeddings()
            query_agent = QueryAgent(db_dir=os.path.join(repo_path, "chroma_db"))
            print("Clone and analysis complete.")

        elif choice == "2":
            if query_agent is None and is_chromadb_ready():
                query_agent = QueryAgent(DB_DIR)  # lazy init if DB already populated
            if query_agent is None:
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
                print(f"{i}. File: {res['file']}\n   Issue: {res['issue']}\n")

        elif choice == "3":
            if query_agent is None and is_chromadb_ready():
                print("ChromaDB found. Ready for approval/refactor loop.")
            elif query_agent is None:
                print("No analysis found. Please run clone and analysis first.")
                continue

            json_report_path = os.path.join(query_agent.db_dir, "..", "analysis", "report.json")
            refactor_agent = RefactorAgent(api_key=os.environ.get("OPENAI_API_KEY", ""))
            approval_agent = ApprovalAgent()

            if not os.path.exists(json_report_path):
                print("No analysis report found for approval loop.")
                continue

            import json
            with open(json_report_path, "r", encoding="utf-8") as f:
                issues = json.load(f)

            for idx, issue in enumerate(issues):
                issue_id = f"issue_{idx}"
                file_path = issue.get("file")
                issue_description = issue.get("issue")

                print(f"\nProcessing {issue_id} in {file_path}")

                proposed_fix = refactor_agent.propose_fix(file_path, issue_description)
                approved = approval_agent.request_approval(issue_id, issue_description, proposed_fix)

                if approved:
                    refactor_agent.apply_fix(file_path, proposed_fix)
                    print(f"[APPLIED] Fix applied to {file_path}")
                else:
                    print(f"[SKIPPED] Fix skipped for {file_path}")

        elif choice == "4":
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid option. Please enter 1, 2, 3 or 4.")

if __name__ == "__main__":
    main_menu()
