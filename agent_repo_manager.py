import os
import subprocess
from pathlib import Path
import uuid
import time

def handle_task(payload: dict) -> dict:
    """
    Simulates an A2A Repo Manager Agent task.
    In real A2A, this would be triggered via HTTP POST and respond with JSON.
    For Colab, we run it as a local function.
    
    Args:
        payload (dict): Expected to contain {"repo_url": "..."}
    
    Returns:
        dict: A2A-style task completion payload
    """
    repo_url = payload.get("repo_url")
    if not repo_url:
        raise ValueError("Missing 'repo_url' in payload")
    
    task_id = f"task-repo-manager-{uuid.uuid4()}"
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    repo_path = f"/content/{repo_name}"
    
    # Clone repo if not exists
    if not os.path.exists(repo_path):
        print(f"Cloning repository: {repo_url}")
        subprocess.run(["git", "clone", repo_url, repo_path], check=True)
    else:
        print(f"Repository already exists at {repo_path}, pulling latest changes...")
        subprocess.run(["git", "-C", repo_path, "pull"], check=True)
    
    # Find all .cs files
    cs_files = [str(p) for p in Path(repo_path).rglob("*.cs")]
    
    # Simulate A2A artifact
    result_payload = {
        "task_id": task_id,
        "status": "completed",
        "timestamp": int(time.time()),
        "output": {
            "repo_path": repo_path,
            "cs_files": cs_files
        },
        "artifacts": [
            {
                "type": "application/json",
                "content": {
                    "repo_path": repo_path,
                    "cs_files": cs_files
                }
            }
        ]
    }
    
    print(f"Repo Manager: Found {len(cs_files)} .cs files.")
    return result_payload
