import os
import json
from agents.repo_manager import RepoManager
from agents.query_agent import QueryAgent
from agents.refactor_agent import RefactorAgent
from agents.approval_agent import ApprovalAgent

def install_dependencies():
    print("Installing dependencies...")
    os.system("pip install -r requirements.txt")
    print("Dependencies installed.")

def main():
    print("=== Welcome to C# Repo Refactor Assistant ===")
    install_dependencies()

    repo_manager = RepoManager(base_path="workspace")
    query_agent = QueryAgent(db_dir="db")
    approval_agent = ApprovalAgent()
    refactor_agent = RefactorAgent(api_key=os.environ.get("OPENAI_API_KEY", ""))

    while True:
        print("\nMain Menu:")
        print("1. Clone a repository")
        print("2. List C# files")
        print("3. Check database readiness")
        print("4. Search issues")
        print("5. Approval & refactor loop")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            repo_url = input("Enter repository URL: ").strip()
            repo_path = repo_manager.clone_repo(repo_url)
            print(f"Repository ready at: {repo_path}")

        elif choice == "2":
            repo_path = input("Enter repository path: ").strip()
            cs_files = repo_manager.list_csharp_files(repo_path)
            print(f"Found {len(cs_files)} C# files:")
            for f in cs_files:
                print(f" - {f}")

        elif choice == "3":
            if query_agent.is_ready():
                print("ChromaDB is ready.")
            else:
                print("ChromaDB is not ready.")

        elif choice == "4":
            query = input("Enter query for issues: ").strip()
            top_k = input("Enter number of top results: ").strip()
            top_k = int(top_k) if top_k.isdigit() else 5
            results = query_agent.search_issues(query, top_k=top_k)
            print("Query Results:")
            for r in results:
                print(r)

        elif choice == "5":
            json_report_path = input("Enter JSON report path: ").strip()
            refactor_agent.approval_and_refactor_loop(json_report_path)

        elif choice == "0":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
