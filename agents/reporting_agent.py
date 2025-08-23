# agents/reporting_agent.py
from agents.query_agent import QueryAgent

class ReportingAgent:
    def __init__(self, chroma_client, collection_name="roslynator_issues"):
        if chroma_client is None:
            raise ValueError("chroma_client must be provided")
        # create QueryAgent with the shared chroma client
        self.query_agent = QueryAgent(collection_name=collection_name, chroma_client=chroma_client)

    def show_all(self):
        issues = self.query_agent._get_all_issues()
        if not issues:
            print("[ReportingAgent] No issues found in ChromaDB.")
            return

        print(f"\n[ReportingAgent] Total issues: {len(issues)}\n")
        for i, issue in enumerate(issues, 1):
            print(
                f"{i}. File: {issue.get('file','unknown')}\n"
                f"   Line: {issue.get('line','unknown')}, Column: {issue.get('column','unknown')}\n"
                f"   Severity: {issue.get('severity','unknown')}\n"
                f"   Issue: {issue.get('issue','unknown')}\n"
            )
