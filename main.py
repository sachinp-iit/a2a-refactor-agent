#!/usr/bin/env python3
"""
main.py - Orchestrator for C# Auto-Refactor Agent (multi-agent local simulator)

Flow (local/A2A-ready simulation):
  1. Repo Manager -> clones repo, returns repo_path + cs_files
  2. Analyzer -> runs Roslynator (or simulated analysis), returns issues artifact
  3. Approval -> interactive loop: for each issue ask user Approve/Skip.
       - If Approved: call Refactor agent to produce fixed code artifact
       - Approval agent applies the returned fix into working tree (simulated)
  4. Commit -> if any changes, ask user to commit & push

Agent contract:
  Each agent is expected to expose: handle_task(payload: dict) -> dict
"""

import sys
import argparse
from typing import Callable

# --- Safe imports for agents (will raise friendly message if file not present) ---
def import_agent(module_path: str, module_alias: str):
    try:
        module = __import__(module_path, fromlist=['handle_task'])
        if not hasattr(module, 'handle_task'):
            raise ImportError(f"Module '{module_path}' missing required 'handle_task' function.")
        return module
    except Exception as e:
        print(f"[ERROR] Could not import {module_alias} ('{module_path}').\n  -> {e}")
        print("  Make sure the file exists and defines `def handle_task(payload: dict) -> dict`.")
        sys.exit(1)

repo_manager = import_agent('agents.repo_manager', 'Repo Manager')
analyzer = import_agent('agents.analyzer', 'Analyzer')
refactor = import_agent('agents.refactor', 'Refactor')
approval = import_agent('agents.approval', 'Approval')
commit_agent = import_agent('agents.commit', 'Commit')

# --- Orchestrator functions ---

def run_pipeline(repo_url: str):
    print(f"\n[Orchestrator] Starting pipeline for repo: {repo_url}\n")

    # 1) Repo Manager
    print("[Orchestrator] Calling Repo Manager...")
    repo_payload = {"repo_url": repo_url}
    repo_result = repo_manager.handle_task(repo_payload)
    repo_output = repo_result.get("output", {})
    repo_path = repo_output.get("repo_path")
    cs_files = repo_output.get("cs_files", [])
    print(f"[Orchestrator] Repo at: {repo_path}, C# files found: {len(cs_files)}")

    if not cs_files:
        print("[Orchestrator] No .cs files found. Exiting.")
        return

    # 2) Analyzer
    print("\n[Orchestrator] Calling Analyzer (Roslynator)...")
    analyze_payload = {"repo_path": repo_path, "cs_files": cs_files}
    analysis_result = analyzer.handle_task(analyze_payload)
    issues = analysis_result.get("output", {}).get("issues", [])
    print(f"[Orchestrator] Analyzer returned {len(issues)} issue(s).")

    if not issues:
        print("[Orchestrator] No issues found. Nothing to do.")
        return

    # 3) Approval loop
    print("\n[Orchestrator] Entering Approval loop...")
    # Approval agent should accept (analysis_result, refactor_callable) or similar contract.
    # We'll pass the analysis_result and a callable wrapper to call the refactor agent.
    def refactor_call(payload: dict) -> dict:
        """Wrapper to call the refactor agent; keeps contract simple."""
        return refactor.handle_task(payload)

    approval_payload = {"analysis": analysis_result, "repo_path": repo_path}
    # The approval agent is expected to call refactor_call when user approves a fix,
    # apply the returned fix to the working files and return a summary payload.
    approval_result = approval.handle_task({"analysis": analysis_result, "repo_path": repo_path, "refactor_callable": refactor_call})
    approval_output = approval_result.get("output", {})
    changes_applied = approval_output.get("changes_applied", False)
    changed_files = approval_output.get("changed_files", [])

    print(f"[Orchestrator] Approval complete. Changes applied: {changes_applied}. Files changed: {len(changed_files)}")

    # 4) Commit step
    if changes_applied:
        print("\n[Orchestrator] Calling Commit agent...")
        commit_payload = {"repo_path": repo_path, "changed_files": changed_files}
        commit_result = commit_agent.handle_task(commit_payload)
        print(f"[Orchestrator] Commit agent result: {commit_result.get('status')}")
    else:
        print("[Orchestrator] No changes to commit.")

    print("\n[Orchestrator] Pipeline finished.\n")


# --- CLI ---
def parse_args():
    parser = argparse.ArgumentParser(description="Run Program 34 multi-agent refactor pipeline (local simulation).")
    parser.add_argument("--repo", "-r", type=str, help="GitHub repo URL to analyze (e.g., https://github.com/owner/repo.git)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if not args.repo:
        repo_url = input("Enter GitHub repo URL to clone and analyze: ").strip()
    else:
        repo_url = args.repo.strip()

    if not repo_url:
        print("No repository URL supplied. Exiting.")
        sys.exit(1)

    run_pipeline(repo_url)
