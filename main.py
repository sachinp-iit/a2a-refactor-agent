import os
import sys
import json
import shutil
import subprocess

from agents.repo_manager import RepoManager
from agents.roslynator_agent import RoslynatorAgent
from agents.embedding_agent import EmbeddingAgent
from agents.query_agent import QueryAgent
from agents.refactor_agent import RefactorAgent
from agents.approval_agent import ApprovalAgent


def clone_and_analyze(repo_manager):
    repo_url = input("Enter the GitHub repo URL to clone: ").strip()
    if not repo_url:
        print("Repository URL is required.")
        return None, None, None

    repo_path = repo_manager.clone_repo(repo_url)
    cs_files = repo_manager.list_csharp_files(repo_path)
    if not cs_files:
        print("No C# files found in the repository.")
        return repo_path, None, None

    # Auto-install Roslynator if missing
    if not shutil.which("roslynator"):
        print("[Main] Roslynator CLI not found. Installing...")
        if not os.path.exists("install_dotnet_roslynator.sh"):
            print("[Main] ERROR: install_dotnet_roslynator.sh not found.")
            return repo_path, None, None
        subprocess.run(["bash", "install_dotnet_roslynator.sh"], check=True)
        os.environ["DOTNET_ROOT"] = os.path.expanduser("~/.dotnet")
        os.environ["PATH"] += ":" + os.path.expanduser("~/.dotnet") + ":" + os.path.expanduser("~/.dotnet/tools")

    roslynator_agent = RoslynatorAgent(repo_path=repo_path, output_dir=os.path.join(repo_path, "analysis"))
    json_report_path = roslynator_agent.run_analysis()
    if not json_report_path:
        print("Roslynator analysis failed or no report generated.")
        return repo_path, None, None

    embedding_agent = EmbeddingAgent(json_report_path=json_report_path, db_dir=os.path.join(repo_path, "chroma_db"))
    embedding_agent.store_embeddings()

    print("Clone and analysis complete.")
    return repo_path, json_report_path, embedding_agent.db_dir


def query_issues(query_agent):
    query_text = input("Enter your search query (or blank to cancel): ").strip()
    if not query_text:
        print("Query cancelled.")
        return
    results = query_agent.search_issues(query_text)
    if not results:
        print("No matching issues found.")
        return
    print(f"\nTop {len(results)} matching issues:")
    for i, res in enumerate(results, 1):
        print(f"{i}. File: {res['file']}\n   Issue: {res['issue']}\n")


def approval_and_refactor_loop(json_report_path):
    if not json_report_path or not os.path.exists(json_report_path):
        print("No analysis report available. Please run clone and analysis first.")
        return

    with open(json_report_path, "r", encoding="utf-8") as f:
        issues = json.load(f)

    refactor_agent = RefactorAgent(api_key=os.environ.get("OPENAI_API_KEY", ""))
    approval_agent = ApprovalAgent()

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


def main_menu():
    repo_manager = RepoManager()
    repo_path = None
    json_report_path = None
    chroma_db_dir = None
    query_agent = None

    while True:
        print("\n===== C# Auto-Refactor Agent Menu =====")
        print("1. Clone GitHub repo and run Roslynator analysis")
        print("2. Query code issues by keyword")
        print("3. Run approval and auto-refactor loop")
        print("4. Exit")

        choice = input("Select an option [1-4]: ").strip()

        if choice == "1":
            repo_path, json_report_path, chroma_db_dir = clone_and_analyze(repo_manager)
            if chroma_db_dir:
                query_agent = QueryAgent(db_dir=chroma_db_dir)
        elif choice == "2":
            if query_agent:
                query_issues(query_agent)
            else:
                print("No ChromaDB loaded. Please run clone and analysis first.")
        elif choice == "3":
            approval_and_refactor_loop(json_report_path)
        elif choice == "4":
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid option. Please enter 1, 2, 3 or 4.")

if __name__ == "__main__":
    main_menu()
