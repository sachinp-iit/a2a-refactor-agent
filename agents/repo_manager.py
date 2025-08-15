import os
import git

class RepoManager:
    def __init__(self, base_path="workspace"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def clone_repo(self, repo_url):
        """
        Clone a GitHub repo into base_path.
        Supports private repos via GITHUB_TOKEN env var.
        Returns the local repo path.
        """
        token = os.environ.get("GITHUB_TOKEN")
        
        # Inject token for private repos
        if token and repo_url.startswith("https://github.com/"):
            # Avoid leaking token in printed logs
            safe_url = repo_url
            repo_url = repo_url.replace(
                "https://github.com/",
                f"https://{token}@github.com/"
            )
            print(f"[RepoManager] Cloning (with token) {safe_url}...")
        else:
            print(f"[RepoManager] Cloning {repo_url}...")

        repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        repo_path = os.path.join(self.base_path, repo_name)

        if os.path.exists(repo_path):
            print(f"[RepoManager] Repo already exists at {repo_path}")
        else:
            git.Repo.clone_from(repo_url, repo_path)

        return repo_path

    def list_csharp_files(self, repo_path):
        """
        Recursively find all .cs files in the repo.
        """
        csharp_files = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".cs"):
                    csharp_files.append(os.path.join(root, file))
        return csharp_files
