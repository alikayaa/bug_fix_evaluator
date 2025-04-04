#!/usr/bin/env python3
"""
Example script demonstrating how to use the bug-fix PR evaluation system with mock data.
"""
import os
import sys
import json
import tempfile
from pprint import pprint

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluator import BugFixEvaluator

def create_mock_pr_file(pr_type):
    """Create a mock PR file with sample data."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    
    if pr_type == "engineer":
        data = {
            "metadata": {
                "number": 123,
                "title": "Fix null pointer exception in login method",
                "description": "When user is null, the login method throws NullPointerException",
                "state": "merged",
                "created_at": "2023-05-15T10:30:45Z",
                "merged_at": "2023-05-16T14:20:10Z",
                "author": "engineer",
                "labels": ["bug", "critical"],
                "milestone": "v1.2.0",
                "draft": False
            },
            "files": [
                {
                    "filename": "src/main/java/com/example/UserService.java",
                    "status": "modified",
                    "additions": 5,
                    "deletions": 2,
                    "changes": 7,
                    "patch": "@@ -45,7 +45,10 @@ public class UserService {\n     * @param user The user to authenticate\n     * @return true if authentication successful, false otherwise\n     */\n-    public boolean login(User user) {\n+    public boolean login(User user) {\n+        if (user == null) {\n+            return false;\n+        }\n         return userRepository.authenticate(user.getUsername(), user.getPassword());\n     }\n }"
                }
            ],
            "commits": [
                {
                    "sha": "abc123",
                    "message": "Fix null pointer exception in login method",
                    "author": "Engineer",
                    "email": "engineer@example.com",
                    "date": "2023-05-15T10:30:45Z"
                }
            ],
            "comments": [],
            "source": "mock_engineer_pr"
        }
    else:
        data = {
            "metadata": {
                "number": 456,
                "title": "Fix login method null pointer exception",
                "description": "This PR fixes the null pointer exception in the login method by adding a null check",
                "state": "open",
                "created_at": "2023-05-15T09:45:30Z",
                "merged_at": None,
                "author": "ai-assistant",
                "labels": ["bug", "ai-generated"],
                "milestone": "v1.2.0",
                "draft": False
            },
            "files": [
                {
                    "filename": "src/main/java/com/example/UserService.java",
                    "status": "modified",
                    "additions": 3,
                    "deletions": 1,
                    "changes": 4,
                    "patch": "@@ -45,7 +45,9 @@ public class UserService {\n     * @param user The user to authenticate\n     * @return true if authentication successful, false otherwise\n     */\n-    public boolean login(User user) {\n+    public boolean login(User user) {\n+        if (user == null) {\n+            throw new IllegalArgumentException(\"User cannot be null\");\n         return userRepository.authenticate(user.getUsername(), user.getPassword());\n     }\n }"
                }
            ],
            "commits": [
                {
                    "sha": "def456",
                    "message": "Fix login method null pointer exception",
                    "author": "AI Assistant",
                    "email": "ai@example.com",
                    "date": "2023-05-15T09:45:30Z"
                }
            ],
            "comments": [],
            "source": "mock_ai_pr"
        }
    
    with open(temp_file.name, 'w') as f:
        json.dump(data, f, indent=2)
    
    return temp_file.name

def main():
    """Run an example evaluation with mock data."""
    print("Bug-Fix PR Evaluation Example (Mock Data)")
    print("========================================")
    
    # Create mock PR files
    engineer_pr_file = create_mock_pr_file("engineer")
    ai_pr_file = create_mock_pr_file("ai")
    
    print(f"Engineer PR file: {engineer_pr_file}")
    print(f"AI PR file: {ai_pr_file}")
    print()
    
    # Custom weights (optional)
    custom_weights = {
        "correctness": 0.35,
        "readability": 0.15,
        "quality": 0.15,
        "problem_solving": 0.25,
        "similarity": 0.10
    }
    
    print("Using custom weights:")
    for metric, weight in custom_weights.items():
        print(f"  {metric}: {weight:.2f}")
    print()
    
    # Create evaluator
    evaluator = BugFixEvaluator(engineer_pr_file, ai_pr_file, weights=custom_weights)
    
    # Run evaluation and save report
    report = evaluator.run_evaluation("mock_evaluation_report.json", generate_html=True)
    
    # Print results
    print("\nEvaluation Results:")
    print("------------------")
    print(f"Final Score: {report['final_score']:.2f}")
    print("\nIndividual Scores:")
    for metric, score in report["scores"].items():
        print(f"  {metric}: {score:.2f}")
    
    if "improvement_suggestions" in report["details"]:
        print("\nImprovement Suggestions:")
        for suggestion in report["details"]["improvement_suggestions"]:
            print(f"  - {suggestion}")
    
    print("\nReports generated:")
    print("  - JSON: mock_evaluation_report.json")
    print("  - HTML: mock_evaluation_report.html")
    print("\nExample output (excerpt):")
    print(json.dumps(
        {k: report[k] for k in ["scores", "final_score", "weights"]},
        indent=2
    ))
    
    # Clean up temporary files
    os.unlink(engineer_pr_file)
    os.unlink(ai_pr_file)

if __name__ == "__main__":
    main() 