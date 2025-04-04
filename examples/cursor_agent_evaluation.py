#!/usr/bin/env python3
"""
Example script for evaluating a bug fix using Cursor agent mode.

Usage:
    python -m examples.cursor_agent_evaluation https://github.com/owner/repo/pull/123 [--open-cursor] [--verbose]
"""

import argparse
import logging
import os
import sys

from bug_fix_cursor_evaluator import CursorAgentEvaluator


def setup_logging(verbose: bool = False) -> None:
    """Configure logging settings."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    """Execute the cursor agent evaluation example."""
    parser = argparse.ArgumentParser(description="Evaluate a GitHub PR using Cursor agent mode")
    parser.add_argument("pr_url", help="URL of the GitHub pull request to evaluate")
    parser.add_argument("--open-cursor", action="store_true", help="Open the instructions file in Cursor")
    parser.add_argument("--output-dir", default="./results", help="Directory to save results")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("Warning: GITHUB_TOKEN environment variable not set. API rate limits may apply.")
    
    evaluator = CursorAgentEvaluator(
        output_dir=args.output_dir,
        github_token=github_token,
        verbose=args.verbose,
    )
    
    try:
        result = evaluator.evaluate_pr(args.pr_url)
        
        print(f"\nEvaluation prepared successfully!")
        print(f"Instructions file: {result['instructions_file']}")
        print(f"Results will be saved to: {result['results_file']}")
        
        if args.open_cursor:
            evaluator.open_in_cursor(result["instructions_file"])
            print(f"\nInstructions file opened in Cursor.")
            print(f"Please activate agent mode and follow the instructions.")
        else:
            print(f"\nTo open the instructions in Cursor, run:")
            print(f"cursor {result['instructions_file']}")
            
        print(f"\nAfter evaluation in Cursor, run this to generate a report:")
        print(f"bug-fix-evaluator report {result['results_file']} --format html --open")
        
    except Exception as e:
        logging.error(f"Error evaluating PR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 