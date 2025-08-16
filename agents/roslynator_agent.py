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
    
        text_path = self.output_dir / "roslynator_analysis.txt"
        json_path = self.output_dir / "roslynator_analysis.json"
    
        try:
            cmd = [
                "roslynator", "analyze",
                "--severity-level", "info",
                "--verbosity", "d"
            ] + [str(p) for p in project_files]
    
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(result.stdout)
            print(f"[RoslynatorAgent] Analysis complete. Text report saved to {text_path}")
    
            # Parse text report to JSON
            issues = self.parse_text_report_to_json(text_path)
    
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(issues, f, indent=2)
    
            if not issues:
                print("[RoslynatorAgent] No issues found in analysis.")
                return json_path
    
            print(f"[RoslynatorAgent] JSON report saved to {json_path}")
            return json_path
    
        except subprocess.CalledProcessError as e:
            print(f"[RoslynatorAgent] Roslynator analysis failed: {e.stderr}")
            print(f"[Debug] STDOUT: {e.stdout}")
            return None
        except FileNotFoundError:
            print("[RoslynatorAgent] Roslynator CLI not found. Please install it first.")
            return None

    def parse_text_report_to_json(self, report_path: Path):
        """
        Parse Roslynator text output to structured JSON list of issues.
        """
        issues = []
        with open(report_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Match lines like: filepath(line,col): severity ID: message
                match = re.match(r'^(.+)\((\d+),\d+\): (\w+) (\w+): (.+)$', line)
                if match:
                    file_path, line_num, severity, diag_id, message = match.groups()
                    issues.append({
                        "file": file_path,
                        "line": int(line_num),
                        "severity": severity,
                        "id": diag_id,
                        "issue": message
                    })
        return issues
