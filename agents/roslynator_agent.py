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
        Output will be saved as roslynator_analysis.json inside output_dir.
        """
        print(f"[RoslynatorAgent] Running analysis on {self.repo_path}...")
    
        cs_files = list(self.repo_path.rglob("*.cs"))
        if not cs_files:
            print("[RoslynatorAgent] No C# files found.")
            return None
    
        report_path = self.output_dir / "roslynator_analysis.txt"
        json_path = self.output_dir / "roslynator_analysis.json"
    
        try:
            # Run Roslynator CLI with comprehensive settings
            cmd = [
                "roslynator", "analyze",
                str(self.repo_path),  # Analyze entire directory
                "--output", str(json_path),
                "--format", "json",
                "--severity-level", "Info",  # Include all diagnostics
                "--verbosity", "detailed",
                "--no-ignore"  # Ensure no diagnostics are ignored
            ]
    
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
    
            # Save raw output to text file for debugging
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(result.stdout)
    
            print(f"[RoslynatorAgent] Analysis complete. Report saved to {report_path}")
    
            # Verify JSON report
            if not os.path.exists(json_path):
                print(f"[RoslynatorAgent] JSON report not generated at {json_path}")
                return None
    
            with open(json_path, "r", encoding="utf-8") as f:
                analysis_data = json.load(f)
    
            # Ensure JSON has valid structure
            if not analysis_data or (isinstance(analysis_data, list) and not analysis_data):
                print("[RoslynatorAgent] No issues found in JSON report.")
                return json_path
    
            print(f"[RoslynatorAgent] JSON report saved to {json_path}")
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
