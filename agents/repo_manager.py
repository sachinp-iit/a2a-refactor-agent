import os
import subprocess

class RepoManager:
    def __init__(self, base_path="workspace"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def clone_repo(self, repo_url):
        """
        Clone a GitHub repo into base_path.
        Supports private repos via GITHUB_TOKEN env var.
        """
        token = os.environ.get("GITHUB_TOKEN", "")
        repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        repo_path = os.path.join(self.base_path, repo_name)

        if os.path.exists(repo_path):
            print(f"[RepoManager] Repo already exists at: {repo_path}")
            return repo_path

        if token and repo_url.startswith("https://github.com/"):
            safe_url = repo_url  # for logging without token
            clone_url = repo_url.replace("https://", f"https://{token}@")
            print(f"[RepoManager] Cloning (with token) {safe_url}...")
        else:
            clone_url = repo_url
            print(f"[RepoManager] Cloning {repo_url}...")

        env = os.environ.copy()
        env["GIT_ASKPASS"] = "echo"
        env["GIT_TERMINAL_PROMPT"] = "0"

        try:
            subprocess.run(
                ["git", "clone", clone_url, repo_path],
                check=True,
                capture_output=True,
                text=True,
                env=env
            )
            print(f"[RepoManager] Successfully cloned to: {repo_path}")
        except subprocess.CalledProcessError as e:
            print("[RepoManager] Git clone failed.")
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
