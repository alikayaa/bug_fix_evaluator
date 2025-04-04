#!/usr/bin/env python3
"""
Example script demonstrating how to use the bug-fix PR evaluation system.
"""
import os
import sys
import json
from pprint import pprint

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluator import BugFixEvaluator

def main():
    """Run an example evaluation."""
    # Check if GitHub token is set
    if "GITHUB_TOKEN" not in os.environ:
        print("Warning: GITHUB_TOKEN environment variable not set.")
        print("GitHub API requests may be rate-limited.")
        print("Set it with: export GITHUB_TOKEN=your_token")
        print()
    
    # Example PR URLs - replace with actual PR URLs
    engineer_pr = "https://github.com/owner/repo/pull/123"
    ai_pr = "https://github.com/owner/repo/pull/456"
    
    print("Bug-Fix PR Evaluation Example")
    print("=============================")
    print(f"Engineer PR: {engineer_pr}")
    print(f"AI PR: {ai_pr}")
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
    evaluator = BugFixEvaluator(engineer_pr, ai_pr, weights=custom_weights)
    
    # Run evaluation and save report
    report = evaluator.run_evaluation("evaluation_report.json")
    
    # Print results
    print("\nEvaluation Results:")
    print("------------------")
    print(f"Final Score: {report['final_score']:.2f}")
    print("\nIndividual Scores:")
    for metric, score in report["scores"].items():
        print(f"  {metric}: {score:.2f}")
    
    print("\nImprovement Suggestions:")
    for suggestion in report["details"]["improvement_suggestions"]:
        print(f"  - {suggestion}")
    
    print("\nReport saved to evaluation_report.json")
    print("\nExample output (excerpt):")
    print(json.dumps(
        {k: report[k] for k in ["scores", "final_score", "weights"]},
        indent=2
    ))

if __name__ == "__main__":
    main() 