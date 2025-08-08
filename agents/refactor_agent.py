import os
from openai import OpenAI

class RefactorAgent:
    def __init__(self, api_key: str):
        os.environ["OPENAI_API_KEY"] = api_key
        self.client = OpenAI()

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
