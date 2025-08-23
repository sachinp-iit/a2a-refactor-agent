import os
import subprocess
import json
from pathlib import Path
import re
import shutil

class RoslynatorAgent:
    def __init__(self, repo_path: str, output_dir: str):
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def restore_packages(self, project_file: Path):
        result = subprocess.run(
            ["dotnet", "restore", str(project_file)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"[RoslynatorAgent] Package restore failed for {project_file}")
            print(result.stdout)
            print(result.stderr)
            raise RuntimeError(f"dotnet restore failed for {project_file}")        

    def restore_all_packages(self, project_files):
        for proj in project_files:
            self.restore_packages(proj)

    def run_analysis(self):
        """
        Restores NuGet packages for all .csproj/.sln files then runs Roslynator.
        Writes a text and JSON report into output_dir and returns the issues list (or None on fatal errors).
        """
        print(f"[RoslynatorAgent] Running analysis on {self.repo_path}...")
        project_files = list(self.repo_path.rglob("*.csproj")) + list(self.repo_path.rglob("*.sln"))
        if not project_files:
            print("[RoslynatorAgent] No C# project or solution files found.")
            return None

        try:
            self.restore_all_packages(project_files)
        except FileNotFoundError:
            print("[RoslynatorAgent] dotnet CLI not found. Please install .NET SDK.")
            return None
        except RuntimeError as e:
            print(f"[RoslynatorAgent] Aborting analysis due to restore error: {e}")
            return None

        text_path = self.output_dir / "roslynator_analysis.txt"
        stderr_path = self.output_dir / "roslynator_analysis.stderr.txt"
        json_path = self.output_dir / "roslynator_analysis.json"

        cmd = [
            "roslynator", "analyze",
            "--severity-level", "info",
            "--verbosity", "d"
        ] + [str(p) for p in project_files]

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
        except FileNotFoundError:
            print("[RoslynatorAgent] Roslynator CLI not found. Please install it.")
            return None

        # Always save stdout/stderr for debugging and parsing
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(proc.stdout or "")
        with open(stderr_path, "w", encoding="utf-8") as f:
            f.write(proc.stderr or "")

        issues = self.parse_text_report_to_json(text_path)

        # Always write a JSON report (possibly empty) so callers can inspect
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(issues, f, indent=2)

        print(f"[RoslynatorAgent] Analysis text saved to {text_path}")
        print(f"[RoslynatorAgent] Analysis stderr saved to {stderr_path}")
        print(f"[RoslynatorAgent] JSON report saved to {json_path} ({len(issues)} issues)")

        return issues

    def parse_text_report_to_json(self, report_path: Path):
        """
        Robust parser for Roslynator textual output. Returns list of issues.
        Each issue: { file, line, column, severity, id, issue }
        - Handles single-line diagnostics and simple wrapped continuation lines.
        - Skips unrelated lines quietly.
        """
        issues = []
        pattern = re.compile(r'^(.+?)\((\d+),(\d+)\):\s*(\w+)\s+([A-Za-z0-9_.-]+):\s*(.+)$')
        with open(report_path, "r", encoding="utf-8", errors="replace") as f:
            for raw in f:
                line = raw.rstrip("\n")
                if not line.strip():
                    continue
                m = pattern.match(line.strip())
                if m:
                    file_path, line_num, col_num, severity, diag_id, message = m.groups()
                    issues.append({
                        "file": file_path,
                        "line": int(line_num),
                        "column": int(col_num),
                        "severity": severity,
                        "id": diag_id,
                        "issue": message.strip()
                    })
                else:
                    if (line.startswith(" ") or line.startswith("\t")) and issues:
                        issues[-1]["issue"] += " " + line.strip()
                    else:
                        continue
        return issues
