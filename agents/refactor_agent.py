import os
import json
from openai import OpenAI
from agents.approval_agent import ApprovalAgent

class RefactorAgent:
    def __init__(self, api_key: str):
        os.environ["OPENAI_API_KEY"] = api_key
        self.client = OpenAI()
        self.approval_agent = ApprovalAgent()

    def propose_fix(self, file_path: str, issue_description: str):
        """
        Reads the C# file and uses GPT-4o-mini to propose a fix for the given issue.
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

    def approval_and_refactor_loop(self, json_report_path: str):
        """
        Handles the full loop of proposing fixes and requesting human approval.
        """
        if not json_report_path or not os.path.exists(json_report_path):
            print("No analysis report available. Please run clone and analysis first.")
            return

        with open(json_report_path, "r", encoding="utf-8") as f:
            issues = json.load(f)

        for idx, issue in enumerate(issues):
            issue_id = f"issue_{idx}"
            file_path = issue.get("file")
            issue_description = issue.get("issue")

            print(f"\nProcessing {issue_id} in {file_path}")

            proposed_fix = self.propose_fix(file_path, issue_description)
            approved = self.approval_agent.request_approval(issue_id, issue_description, proposed_fix)

            if approved:
                self.apply_fix(file_path, proposed_fix)
                print(f"[APPLIED] Fix applied to {file_path}")
            else:
                print(f"[SKIPPED] Fix skipped for {file_path}")
