import os
import subprocess

class RepoManager:
    def __init__(self, github_repo_url=None, github_pat=None):
        self.github_repo_url = github_repo_url
        self.github_pat = github_pat

    def clone_private_repo(self):
        """
        Clone a private GitHub repo using a Personal Access Token (PAT).
        """
        if not self.github_repo_url or not self.github_pat:
            raise ValueError("GitHub repo URL and PAT must be provided.")

        repo_name = self.github_repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        repo_path = os.path.join("/content", repo_name)

        if os.path.exists(repo_path):
            print(f"Repo already exists at: {repo_path}")
            return repo_path

        safe_url = self.github_repo_url.replace("https://", f"https://{self.github_pat}@")

        env = os.environ.copy()
        env["GIT_ASKPASS"] = "echo"
        env["GIT_TERMINAL_PROMPT"] = "0"

        try:
            subprocess.run(
                ["git", "clone", safe_url, repo_path],
                check=True,
                capture_output=True,
                text=True,
                env=env
            )
            print(f"Successfully cloned to: {repo_path}")
        except subprocess.CalledProcessError as e:
            print("Git clone failed.")
            print("STDOUT:\n", e.stdout)
            print("STDERR:\n", e.stderr)
            raise

        return repo_path

    def list_csharp_files(self, repo_path):
        """
        Recursively find all .cs files in the repo.
        """
        csharp_files = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.lower().endswith(".cs"):
                    csharp_files.append(os.path.join(root, file))
        return csharp_files
