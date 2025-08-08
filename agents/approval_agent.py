class ApprovalAgent:
    def request_approval(self, issue_id: str, issue_description: str, proposed_fix: str) -> bool:
        """
        Displays the issue and proposed fix, then asks the user for approval.
        Returns True if approved, False otherwise.
        """
        print("\n==============================")
        print(f"Issue ID: {issue_id}")
        print(f"Description: {issue_description}")
        print("\nProposed Fix:\n")
        print(proposed_fix)
        print("\n==============================")

        while True:
            user_input = input("Apply this fix? (yes/no): ").strip().lower()
            if user_input in ["yes", "y"]:
                return True
            elif user_input in ["no", "n"]:
                return False
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
