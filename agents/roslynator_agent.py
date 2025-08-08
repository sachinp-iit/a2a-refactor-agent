import os
import subprocess
import json
from pathlib import Path

class RoslynatorAgent:
    def __init__(self, repo_path: str, output_dir: str):
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_analysis(self):
        """
        Runs Roslynator analysis on all C# files in the repo.
        Output will be saved as analysis_report.json inside output_dir.
        """
        print(f"[RoslynatorAgent] Running analysis on {self.repo_path}...")

        cs_files = list(self.repo_path.rglob("*.cs"))
        if not cs_files:
            print("[RoslynatorAgent] No C# files found.")
            return None

        report_path = self.output_dir / "roslynator_analysis.txt"

        try:
            # Run Roslynator CLI for each file
            with open(report_path, "w", encoding="utf-8") as f:
                for cs_file in cs_files:
                    cmd = ["roslynator", "analyze", str(cs_file)]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    f.write(f"=== {cs_file} ===\n")
                    f.write(result.stdout)
                    f.write("\n\n")

            print(f"[RoslynatorAgent] Analysis complete. Report saved to {report_path}")

            # Optionally parse to JSON (simple split)
            json_path = self.output_dir / "roslynator_analysis.json"
            analysis_data = self._parse_report_to_json(report_path)
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(analysis_data, jf, indent=2)

            print(f"[RoslynatorAgent] JSON report saved to {json_path}")
            return json_path

        except FileNotFoundError:
            print("[RoslynatorAgent] Roslynator CLI not found. Please install it first.")
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
