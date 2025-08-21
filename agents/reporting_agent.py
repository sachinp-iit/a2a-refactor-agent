import os
import json

class ReportingAgent:
    def __init__(self, report_path: str):
        self.report_path = report_path
        self.issues = []
        self._load_report()

    def _load_report(self):
        if not os.path.exists(self.report_path):
            print(f"[ReportingAgent] No report found at {self.report_path}")
            return
        try:
            with open(self.report_path, "r", encoding="utf-8") as f:
                self.issues = json.load(f)
        except Exception as e:
            print(f"[ReportingAgent] Failed to load report: {e}")
            self.issues = []

    def show_summary(self):
        print(f"\n[ReportingAgent] Total issues: {len(self.issues)}")

    def show_all(self):
        if not self.issues:
            print("[ReportingAgent] No issues to display.")
            return

        print(f"\n=== Roslynator Report ({len(self.issues)} issues) ===")
        for i, issue in enumerate(self.issues, 1):
            print(
                f"{i}. File: {issue.get('file')}\n"
                f"   Line: {issue.get('line')}, Column: {issue.get('column')}\n"
                f"   Severity: {issue.get('severity')}\n"
                f"   Rule: {issue.get('id')}\n"
                f"   Message: {issue.get('issue')}\n"
            )

    def show_by_severity(self, severity: str):
        filtered = [i for i in self.issues if i.get("severity", "").lower() == severity.lower()]
        print(f"\n=== {severity.capitalize()} Issues ({len(filtered)}) ===")
        for i, issue in enumerate(filtered, 1):
            print(
                f"{i}. File: {issue.get('file')}\n"
                f"   Line: {issue.get('line')}, Column: {issue.get('column')}\n"
                f"   Rule: {issue.get('id')}\n"
                f"   Message: {issue.get('issue')}\n"
            )
