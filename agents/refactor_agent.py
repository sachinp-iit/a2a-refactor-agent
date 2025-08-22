import os
from openai import OpenAI
from agents.approval_agent import ApprovalAgent
from agents.query_agent import QueryAgent

class RefactorAgent:
    def __init__(self, chroma_client, repo_root: str, collection_name: str = "roslynator_issues"):
        self.client = OpenAI()
        self.approval_agent = ApprovalAgent()
        self.query_agent = QueryAgent(db_dir=None, collection_name=collection_name, chroma_client=chroma_client)
        self.repo_root = repo_root

    def propose_fix(self, file_path: str, issue_description: str):
        """
        Reads the C# file and uses GPT to propose a fix for the given issue.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()

        prompt = f"""
You are a C# code refactoring assistant.
The following code has an issue reported by Roslynator:
Issue: {issue_description}

Your task:
1. Fix the issue without altering unrelated functionality.
2. Maintain coding conventions.
3. Output only the modified code.

C# file content:
{code_content}
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert C# refactoring assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        return response.choices[0].message.content

    def apply_fix(self, file_path: str, fixed_code: str):
        """
        Overwrites the original file with the fixed code.
        """
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_code)
        return True

    def approval_and_refactor_loop(self):
        """
        Fetch issues from ChromaDB, propose fixes, and request approval.
        """
        issues = self.query_agent._get_all_issues()
        if not issues:
            print("No issues found in ChromaDB.")
            return

        for idx, issue in enumerate(issues):
            issue_id = f"issue_{idx}"
            relative_path = issue.get("file")
            file_path = os.path.join(self.repo_root, relative_path) if relative_path else None
            issue_description = issue.get("issue")

            if not file_path or not os.path.exists(file_path):
                print(f"[SKIPPED] Invalid file path for {issue_id}: {relative_path}")
                continue

            print(f"\nProcessing {issue_id} in {file_path}")

            proposed_fix = self.propose_fix(file_path, issue_description)
            approved = self.approval_agent.request_approval(issue_id, issue_description, proposed_fix)

            if approved:
                self.apply_fix(file_path, proposed_fix)
                print(f"[APPLIED] Fix applied to {file_path}")
            else:
                print(f"[SKIPPED] Fix skipped for {file_path}")
