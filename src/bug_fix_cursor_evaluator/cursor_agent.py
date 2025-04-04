"""Cursor agent evaluation module for evaluating bug fixes with Cursor agent mode."""

import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional, Union

from .repository import RepositoryHandler
from .utils import is_git_repo, get_local_pr_diff, wait_for_results


class CursorAgentEvaluator:
    """Evaluator for bug fixes using Cursor agent mode.

    This class orchestrates the evaluation process of bug fixes using Cursor agent mode.
    It handles:
    - Setting up repositories
    - Generating instructions
    - Preparing files for evaluation
    - Waiting for evaluation results
    """

    def __init__(
        self,
        work_dir: Optional[str] = None,
        output_dir: str = "./results",
        github_token: Optional[str] = None,
        timeout: int = 600,
        verbose: bool = False,
    ):
        """Initialize the CursorAgentEvaluator.

        Args:
            work_dir: Directory to use for temporary files. Defaults to a temporary directory.
            output_dir: Directory to store evaluation results. Defaults to "./results".
            github_token: GitHub token for API access. Defaults to None.
            timeout: Timeout in seconds for waiting for results. Defaults to 600.
            verbose: Whether to enable verbose logging. Defaults to False.
        """
        self.logger = logging.getLogger(__name__)
        
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.getLogger().setLevel(log_level)
        
        self.work_dir = work_dir if work_dir else tempfile.mkdtemp()
        self.output_dir = output_dir
        self.github_token = github_token
        self.timeout = timeout
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.repo_handler = RepositoryHandler(
            work_dir=self.work_dir,
            github_token=self.github_token
        )
        
        self.logger.info(f"Initialized CursorAgentEvaluator with work_dir={self.work_dir}, output_dir={self.output_dir}")

    def evaluate_pr(self, pr_url: str) -> Dict:
        """Evaluate a PR using Cursor agent mode.

        Args:
            pr_url: URL of the PR to evaluate.

        Returns:
            Dict: Result info with path to results file.
        """
        self.logger.info(f"Evaluating PR: {pr_url}")
        
        # Parse PR URL
        repo_owner, repo_name, pr_number = self.repo_handler.parse_pr_url(pr_url)
        full_repo_name = f"{repo_owner}/{repo_name}"
        
        # Get PR diff from GitHub
        pr_diff = self.repo_handler.get_pr_diff_from_github(repo_owner, repo_name, pr_number)
        
        # Create evaluation directory
        eval_dir = os.path.join(self.work_dir, f"eval_{repo_name}_{pr_number}")
        os.makedirs(eval_dir, exist_ok=True)
        
        # Generate instruction file
        instruction_file = self._generate_instruction_file(
            eval_dir, full_repo_name, pr_number, pr_diff, pr_url
        )
        
        # Generate results file path
        results_file = os.path.join(self.output_dir, f"{repo_name}_{pr_number}_results.json")
        
        return {
            "instruction_file": instruction_file,
            "results_file": results_file,
            "eval_dir": eval_dir,
            "repo_name": full_repo_name,
            "pr_number": pr_number,
            "pr_url": pr_url,
        }

    def evaluate_local_pr(
        self, 
        repo_path: str, 
        pr_number: Union[int, str], 
        repo_url: Optional[str] = None
    ) -> Dict:
        """Evaluate a PR from a local Git repository.

        Args:
            repo_path: Path to the local Git repository.
            pr_number: PR number to evaluate.
            repo_url: Repository URL. If None, will attempt to extract from git remote.

        Returns:
            Dict: Result info with path to results file.
        """
        self.logger.info(f"Evaluating local PR #{pr_number} from {repo_path}")
        
        if not is_git_repo(repo_path):
            raise ValueError(f"Directory {repo_path} is not a Git repository")
        
        # Determine repo information
        if repo_url:
            parts = repo_url.strip("/").split("/")
            if "github.com" in parts:
                idx = parts.index("github.com")
                if idx + 2 < len(parts):
                    repo_owner = parts[idx + 1]
                    repo_name = parts[idx + 2]
                    full_repo_name = f"{repo_owner}/{repo_name}"
                else:
                    raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
            else:
                raise ValueError(f"Only GitHub repositories are supported, got: {repo_url}")
        else:
            # Try to extract from git remote
            import subprocess
            try:
                result = subprocess.run(
                    ["git", "-C", repo_path, "remote", "get-url", "origin"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                origin_url = result.stdout.strip()
                
                # Parse the URL to extract owner and repo
                if "github.com" in origin_url:
                    parts = origin_url.strip("/").replace(":", "/").replace(".git", "").split("/")
                    idx = parts.index("github.com") if "github.com" in parts else -1
                    if idx == -1:
                        # Handle SSH URL format
                        repo_owner = parts[-2]
                        repo_name = parts[-1]
                    else:
                        repo_owner = parts[idx + 1]
                        repo_name = parts[idx + 2]
                    
                    full_repo_name = f"{repo_owner}/{repo_name}"
                    repo_url = f"https://github.com/{full_repo_name}"
                else:
                    raise ValueError(f"Only GitHub repositories are supported, got: {origin_url}")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to get repository URL: {e}")
                raise ValueError("Could not determine repository information") from e
        
        # Get PR diff
        pr_diff = get_local_pr_diff(repo_path, pr_number)
        
        # Create evaluation directory
        eval_dir = os.path.join(self.work_dir, f"eval_{repo_name}_{pr_number}")
        os.makedirs(eval_dir, exist_ok=True)
        
        # Generate PR URL
        pr_url = f"https://github.com/{full_repo_name}/pull/{pr_number}"
        
        # Generate instruction file
        instruction_file = self._generate_instruction_file(
            eval_dir, full_repo_name, pr_number, pr_diff, pr_url
        )
        
        # Generate results file path
        results_file = os.path.join(self.output_dir, f"{repo_name}_{pr_number}_results.json")
        
        return {
            "instruction_file": instruction_file,
            "results_file": results_file,
            "eval_dir": eval_dir,
            "repo_name": full_repo_name,
            "pr_number": pr_number,
            "pr_url": pr_url,
        }

    def _generate_instruction_file(
        self, 
        eval_dir: str, 
        repo_name: str, 
        pr_number: Union[int, str], 
        pr_diff: str,
        pr_url: str
    ) -> str:
        """Generate the instruction file for Cursor agent mode.

        Args:
            eval_dir: Directory to store evaluation files.
            repo_name: Repository name in the format 'owner/repo'.
            pr_number: PR number.
            pr_diff: PR diff content.
            pr_url: URL of the PR.

        Returns:
            str: Path to the instruction file.
        """
        self.logger.info(f"Generating instruction file for PR #{pr_number} in {repo_name}")
        
        # Create directories
        instructions_dir = os.path.join(eval_dir, "instructions")
        results_dir = os.path.join(eval_dir, "results")
        
        os.makedirs(instructions_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)
        
        # Create diff file
        diff_file = os.path.join(instructions_dir, "pr_diff.diff")
        with open(diff_file, "w") as f:
            f.write(pr_diff)
        
        # Create instruction file
        instruction_file = os.path.join(instructions_dir, "bug_fix_evaluation.md")
        
        instruction_content = f"""# Bug Fix Evaluation

## Overview
You are tasked with evaluating a bug fix in a pull request. This evaluation will help determine the quality and effectiveness of the bug fix.

## Repository and PR Information
- Repository: {repo_name}
- PR Number: {pr_number}
- PR URL: {pr_url}

## Evaluation Criteria
Evaluate the bug fix based on the following criteria:

1. **Correctness (1-10)**: Does the fix correctly address the bug?
2. **Completeness (1-10)**: Does the fix address all aspects of the bug?
3. **Pattern Match (1-10)**: Does the fix follow good patterns and practices?
4. **Cleanliness (1-10)**: Is the code clean, readable, and well-structured?
5. **Efficiency (1-10)**: Is the fix efficient in terms of performance?
6. **Complexity (1-10)**: Is the fix appropriately complex for the problem?

## Steps to Follow
1. Review the PR diff provided in the `pr_diff.diff` file.
2. Analyze the changes to understand the bug and the fix.
3. Evaluate the fix based on the criteria above.
4. Provide an overall evaluation score (1-100).
5. List strengths and weaknesses of the fix.
6. Provide suggestions for improvement.

## Output Format
Your evaluation should be saved as a JSON file at: `{results_dir}/evaluation_results.json`

The JSON should have the following format:
```json
{{
  "repository": "{repo_name}",
  "pr_number": "{pr_number}",
  "criteria": {{
    "correctness": {{
      "score": 8,
      "explanation": "The fix correctly addresses the main issue...",
      "strength": "Good understanding of the root cause...",
      "weakness": "Could have added more validation..."
    }},
    "completeness": {{
      "score": 7,
      "explanation": "The fix addresses most aspects...",
      "strength": "Covers the main scenarios...",
      "weakness": "Doesn't handle edge case X..."
    }},
    "pattern_match": {{
      "score": 9,
      "explanation": "The fix follows established patterns...",
      "strength": "Uses the appropriate design pattern...",
      "weakness": "Minor deviation from project conventions..."
    }},
    "cleanliness": {{
      "score": 8,
      "explanation": "The code is clean and readable...",
      "strength": "Good variable names and structure...",
      "weakness": "Comments could be more descriptive..."
    }},
    "efficiency": {{
      "score": 7,
      "explanation": "The solution is reasonably efficient...",
      "strength": "Avoids unnecessary computations...",
      "weakness": "Could use a more optimized algorithm for X..."
    }},
    "complexity": {{
      "score": 8,
      "explanation": "The complexity is appropriate...",
      "strength": "Simple solution for a simple problem...",
      "weakness": "Could be slightly simpler in one area..."
    }}
  }},
  "overall": 78,
  "strengths": [
    "Good understanding of the root cause",
    "Clean implementation",
    "Follows project conventions"
  ],
  "weaknesses": [
    "Doesn't handle all edge cases",
    "Missing some validation"
  ],
  "suggestions": [
    "Add validation for X",
    "Consider optimizing Y",
    "Add tests for edge case Z"
  ]
}}
```

## Additional Notes
- Be thorough in your evaluation.
- Consider both the immediate fix and its long-term implications.
- Be specific in your explanations, strengths, weaknesses, and suggestions.
- Scores should be integers between 1 and 10.
- The overall score should be between 1 and 100.
"""
        
        with open(instruction_file, "w") as f:
            f.write(instruction_content)
        
        self.logger.info(f"Generated instruction file: {instruction_file}")
        return instruction_file

    def wait_for_results(self, results_file: str) -> Dict:
        """Wait for results to be generated.

        Args:
            results_file: Path to the results file to wait for.

        Returns:
            Dict: The results loaded from the file.
        """
        self.logger.info(f"Waiting for results file: {results_file}")
        results = wait_for_results(results_file, timeout=self.timeout)
        self.logger.info(f"Results received for {results_file}")
        return results

    def cleanup(self):
        """Clean up temporary files."""
        if self.work_dir and os.path.exists(self.work_dir) and self.work_dir != ".":
            self.logger.info(f"Cleaning up work directory: {self.work_dir}")
            shutil.rmtree(self.work_dir)
        else:
            self.logger.warning(f"Skipping cleanup of non-temporary work dir: {self.work_dir}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}") 