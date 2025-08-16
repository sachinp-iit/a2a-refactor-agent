import os
import subprocess
import json
from pathlib import Path
import shutil

class RoslynatorAgent:
    def __init__(self, repo_path: str, output_dir: str):
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_analysis(self):
        """
        Runs Roslynator analysis on all C# files in the repo.
        Output will be saved as roslynator_analysis.json inside output_dir.
        """
        print(f"[RoslynatorAgent] Running analysis on {self.repo_path}...")
    
        project_files = list(self.repo_path.rglob("*.csproj")) + list(self.repo_path.rglob("*.sln"))
        if not project_files:
            print("[RoslynatorAgent] No C# project or solution files found.")
            return None
    
        json_path = self.output_dir / "roslynator_analysis.json"
    
        try:
            cmd = [
                "roslynator", "analyze",
                "--msbuild-path", os.path.dirname(shutil.which("dotnet")),
                "--output", str(json_path),
                "--output-format", "gitlab",
                "--severity-level", "info",
                "--report-suppressed-diagnostics"
            ] + [str(p) for p in project_files]
    
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"[RoslynatorAgent] Analysis complete. Report saved to {json_path}")
    
            # Load GitLab format (JSON lines) and transform to list of dicts [{"file": "...", "issue": "..."}]
            issues = []
            with open(json_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        gitlab_issue = json.loads(line)
                        if "path" in gitlab_issue and "description" in gitlab_issue:
                            issues.append({
                                "file": gitlab_issue["path"],
                                "issue": gitlab_issue["description"]
                            })
    
            # Overwrite with transformed JSON
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(issues, f, indent=2)
    
            if not issues:
                print("[RoslynatorAgent] No issues found in analysis.")
                return json_path
    
            print(f"[RoslynatorAgent] JSON report transformed and saved to {json_path}")
            return json_path
    
        except subprocess.CalledProcessError as e:
            print(f"[RoslynatorAgent] Roslynator analysis failed: {e.stderr}")
            return None
        except FileNotFoundError:
            print("[RoslynatorAgent] Roslynator CLI not found. Please install it first.")
            return None
        except json.JSONDecodeError:
            print("[RoslynatorAgent] Invalid JSON report generated.")
            return None

    def _parse_report_to_json(self, report_path: Path):
        """
        Convert plain text Roslynator output into structured JSON.
        """
        analysis_results = []
        with open(report_path, "r", encoding="utf-8") as f:
            current_file = None
            for line in f:
                line = line.strip()
                if line.startswith("===") and line.endswith("==="):
                    current_file = line.strip("=").strip()
                elif line and current_file:
                    analysis_results.append({"file": current_file, "issue": line})
        return analysis_results
