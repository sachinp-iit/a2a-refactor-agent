import os
from agents.repo_clone_agent import RepoCloneAgent
from agents.roslynator_agent import RoslynatorAgent
from agents.chroma_agent import ChromaAgent
from agents.query_agent import QueryAgent
from agents.refactor_agent import RefactorAgent
from agents.approval_agent import ApprovalAgent

def main():
    # === Step 1: Clone GitHub Repo ===
    repo_url = input("Enter the GitHub repo URL to clone: ").strip()
    repo_clone_agent = RepoCloneAgent()
    repo_path = repo_clone_agent.clone_repo(repo_url)

    # Extract C# files
    cs_files = repo_clone_agent.extract_cs_files(repo_path)
    if not cs_files:
        print("No C# files found in the repository.")
        return

    # === Step 2: Run Roslynator Analysis ===
    roslynator_agent = RoslynatorAgent()
    analysis_results = roslynator_agent.run_analysis(cs_files)

    # === Step 3: Store in ChromaDB ===
    chroma_agent = ChromaAgent()
    chroma_agent.add_documents(analysis_results)

    # === Step 4: Query Code Issues ===
    query_agent = QueryAgent(chroma_agent)
    query_text = input("Enter a search query for issues (or press Enter to skip): ").strip()
    if query_text:
        matches = query_agent.query_issues(query_text)
        print("\nQuery Results:")
        for m in matches:
            print(m)

    # === Step 5 & 6: Auto-refactor with Approval Loop ===
    refactor_agent = RefactorAgent()
    approval_agent = ApprovalAgent()

    for issue in analysis_results:
        issue_id = issue.get("id", "N/A")
        description = issue.get("description", "")
        file_path = issue.get("file_path", "")

        proposed_fix = refactor_agent.propose_fix(file_path, description)

        if approval_agent.request_approval(issue_id, description, proposed_fix):
            refactor_agent.apply_fix_to_file(file_path, proposed_fix)
            print(f"[FIXED] {file_path}")
        else:
            print(f"[SKIPPED] {file_path}")

    print("\n=== Process Completed ===")

if __name__ == "__main__":
    main()
