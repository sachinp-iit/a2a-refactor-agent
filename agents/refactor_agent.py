# agents/refactor_agent.py
import os
from openai import OpenAI
from agents.approval_agent import ApprovalAgent
from agents.query_agent import QueryAgent

class RefactorAgent:
    def __init__(self, chroma_client, repo_root: str, collection_name: str = "roslynator_issues"):
        self.client = OpenAI()
        self.approval_agent = ApprovalAgent()
        self.query_agent = QueryAgent(collection_name=collection_name, chroma_client=chroma_client)
        self.repo_root = os.path.abspath(repo_root)
        self._repo_index = None  # built lazily for robust path matching

    # ---------- path helpers ----------
    def _index_repo(self):
        if self._repo_index is not None:
            return
        index = {}
        for root, _, files in os.walk(self.repo_root):
            for fn in files:
                if not fn.endswith(".cs"):
                    continue
                full = os.path.abspath(os.path.join(root, fn))
                parts = full.split(os.sep)
                # map multiple tail paths to the same file for suffix matching
                for i in range(len(parts)):
                    tail = os.sep.join(parts[i:])
                    index[tail] = full
        self._repo_index = index

    def _resolve_file(self, path_hint: str):
        if not path_hint:
            return None
        hint = os.path.normpath(path_hint)

        # 1) absolute and exists
        if os.path.isabs(hint) and os.path.exists(hint):
            return hint

        # 2) relative to repo_root
        candidate = os.path.abspath(os.path.join(self.repo_root, hint))
        if os.path.exists(candidate):
            return candidate

        # 3) try repo index + suffix match (handles stale absolute paths)
        self._index_repo()
        tail = os.path.normpath(hint)
        if tail in self._repo_index:
            return self._repo_index[tail]
        for k, v in self._repo_index.items():
            if k.endswith(os.sep + os.path.basename(hint)) or k.endswith(tail):
                return v

        return None
    # ----------------------------------

    def propose_fix(self, file_path: str, issue_description: str):
        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()

        prompt = f"""
You are a C# code refactoring assistant.
The following code has an issue reported by Roslynator:
Issue: {issue_description}

Your task:
1) Fix the issue without altering unrelated functionality.
2) Maintain coding conventions.
3) Output only the modified code.

C# file content:
{code_content}
"""
        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert C# refactoring assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        return resp.choices[0].message.content

    def apply_fix(self, file_path: str, fixed_code: str):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_code)
        return True

    def approval_and_refactor_loop(self):
        # Pull all issues from Chroma via QueryAgent (no JSON)
        issues = self.query_agent._get_all_issues()
        if not issues:
            print("No issues found in ChromaDB.")
            return

        for idx, issue in enumerate(issues):
            issue_id = f"issue_{idx}"
            file_hint = issue.get("file") or ""
            file_path = self._resolve_file(file_hint)
            issue_description = issue.get("issue") or ""

            if not file_path or not os.path.exists(file_path):
                print(f"[SKIPPED] Invalid file path for {issue_id}: {file_hint}")
                continue

            print(f"\nProcessing {issue_id} in {file_path}")

            proposed_fix = self.propose_fix(file_path, issue_description)
            approved = self.approval_agent.request_approval(issue_id, issue_description, proposed_fix)

            if approved:
                self.apply_fix(file_path, proposed_fix)
                print(f"[APPLIED] Fix applied to {file_path}")
            else:
                print(f"[SKIPPED] Fix skipped for {file_path}")
