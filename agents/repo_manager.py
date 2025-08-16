import os
import subprocess
import shutil
from agents.roslynator_agent import RoslynatorAgent
from agents.embedding_agent import EmbeddingAgent

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
            safe_url = repo_url  # for logging
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

    def clone_and_analyze(self):
        """
        Full pipeline: clone repo, analyze with Roslynator, store embeddings.
        """
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_DIR = os.path.join(BASE_DIR, "chroma_db")

        repo_url = input("Enter the GitHub repo URL to clone: ").strip()
        if not repo_url:
            print("Repository URL is required.")
            return None, None, None

        repo_path = self.clone_repo(repo_url)
        cs_files = self.list_csharp_files(repo_path)
        if not cs_files:
            print("No C# files found in the repository.")
            return repo_path, None, None

        # Ensure Roslynator CLI installed
        if shutil.which("roslynator") is None:
            if not os.path.exists("install_dotnet_roslynator.sh"):
                print("[RepoManager] ERROR: install_dotnet_roslynator.sh not found.")
                return repo_path, None, None
            subprocess.run(["bash", "install_dotnet_roslynator.sh"], check=True)
            dotnet_root = os.path.expanduser("~/.dotnet")
            dotnet_tools = os.path.expanduser("~/.dotnet/tools")
            path_parts = os.environ["PATH"].split(":")
            if dotnet_root not in path_parts:
                os.environ["PATH"] += f":{dotnet_root}"
            if dotnet_tools not in path_parts:
                os.environ["PATH"] += f":{dotnet_tools}"
            os.environ["DOTNET_ROOT"] = dotnet_root

        roslynator_agent = RoslynatorAgent(
            repo_path=repo_path,
            output_dir=os.path.join(repo_path, "analysis")
        )
        json_report_path = roslynator_agent.run_analysis()
        if not json_report_path:
            print("Roslynator analysis failed or no report generated.")
            return repo_path, None, None

        embedding_agent = EmbeddingAgent(
            json_report_path=json_report_path,
            db_dir=DB_DIR
        )
        embedding_agent.store_embeddings()

        print("Clone and analysis complete.")
        return repo_path, json_report_path, DB_DIR
