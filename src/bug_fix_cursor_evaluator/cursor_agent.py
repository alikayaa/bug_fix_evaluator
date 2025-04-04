"""Cursor agent evaluation module for evaluating bug fixes with Cursor agent mode."""

import json
import logging
import os
import shutil
import tempfile
import subprocess
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
        auto_cleanup: bool = False,
    ):
        """Initialize the CursorAgentEvaluator.

        Args:
            work_dir: Directory to use for temporary files. Defaults to a temporary directory.
            output_dir: Directory to store evaluation results. Defaults to "./results".
            github_token: GitHub token for API access. Defaults to None.
            timeout: Timeout in seconds for waiting for results. Defaults to 600.
            verbose: Whether to enable verbose logging. Defaults to False.
            auto_cleanup: Whether to automatically clean up temporary files. Defaults to False.
        """
        self.logger = logging.getLogger(__name__)
        
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.getLogger().setLevel(log_level)
        
        self.work_dir = work_dir if work_dir else tempfile.mkdtemp()
        self.output_dir = output_dir
        self.github_token = github_token
        self.timeout = timeout
        self.auto_cleanup = auto_cleanup
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.repo_handler = RepositoryHandler(
            work_dir=self.work_dir,
            github_token=self.github_token
        )
        
        self.logger.info(f"Initialized CursorAgentEvaluator with work_dir={self.work_dir}, output_dir={self.output_dir}")
        print(f"\n🚀 Bug Fix Evaluator initialized:")
        print(f"- Working directory: {self.work_dir}")
        print(f"- Output directory: {self.output_dir}")
        print(f"- Auto cleanup: {'Enabled' if self.auto_cleanup else 'Disabled (manual cleanup required)'}\n")

    def evaluate_pr(self, pr_url: str) -> Dict:
        """Evaluate a PR using Cursor agent mode.

        Args:
            pr_url: URL of the PR to evaluate.

        Returns:
            Dict: Result info with path to results file.
        """
        self.logger.info(f"Evaluating PR: {pr_url}")
        print(f"\n📝 Preparing evaluation for PR: {pr_url}")
        
        # Parse PR URL
        repo_owner, repo_name, pr_number = self.repo_handler.parse_pr_url(pr_url)
        full_repo_name = f"{repo_owner}/{repo_name}"
        
        # Get PR diff from GitHub
        pr_diff = self.repo_handler.get_pr_diff_from_github(repo_owner, repo_name, pr_number)
        if not pr_diff:
            raise ValueError(f"Failed to get PR diff from GitHub for {pr_url}")
        
        # Create evaluation directory
        eval_dir = os.path.join(self.work_dir, f"eval_{repo_name}_{pr_number}")
        os.makedirs(eval_dir, exist_ok=True)
        
        # Save PR diff to file
        diff_file = os.path.join(eval_dir, f"pr_{pr_number}.diff")
        with open(diff_file, "w") as f:
            f.write(pr_diff)
        
        # Generate instruction file
        instruction_file = self._generate_instruction_file(
            eval_dir, full_repo_name, pr_number, pr_diff, pr_url
        )
        
        # Generate results file path
        results_file = os.path.join(self.output_dir, f"{repo_name}_{pr_number}_results.json")
        
        print(f"\n✅ PR preparation complete!")
        print(f"\n📋 Evaluation Files:")
        print(f"- Instructions: {instruction_file}")
        print(f"- PR Diff: {diff_file}")
        print(f"- Expected Results: {results_file}")
        print(f"\n⚠️ IMPORTANT: Keep these files until evaluation is complete!")
        print(f"If you don't see the files at the locations above, they may have been cleaned up.")
        print(f"Set auto_cleanup=False to prevent automatic cleanup.\n")
        
        return {
            "instructions_file": instruction_file,
            "diff_file": diff_file,
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
        """Generate instruction file for Cursor agent.

        Args:
            eval_dir: Directory to write files to.
            repo_name: Name of the repository (owner/repo).
            pr_number: PR number.
            pr_diff: Diff of the PR.
            pr_url: URL of the PR.

        Returns:
            str: Path to the instruction file.
        """
        self.logger.info(f"Generating instruction file for {repo_name} PR #{pr_number}")
        
        # Create directories
        instructions_dir = os.path.join(eval_dir, "instructions")
        results_dir = self.output_dir
        os.makedirs(instructions_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)
        
        # Save PR diff to file
        diff_file = os.path.join(eval_dir, f"pr_{pr_number}.diff")
        with open(diff_file, "w") as f:
            f.write(pr_diff)
        
        # Create instruction file
        instruction_file = os.path.join(instructions_dir, "bug_fix_evaluation.md")
        results_file = os.path.join(results_dir, f"{repo_name.replace('/', '_')}_{pr_number}_results.json")
        results_file = os.path.abspath(results_file)
        
        instruction_content = f"""# Bug Fix Evaluation - IMPORTANT AGENT INSTRUCTIONS

## Instructions for Cursor Agent
You are currently in Cursor's agent mode. Please carefully follow these instructions to evaluate a bug fix PR.

## Steps for You (the User)
1. After opening this file in Cursor, activate Agent Mode by pressing Cmd+Shift+P (macOS) or Ctrl+Shift+P (Windows/Linux) and selecting "Enable Agent Mode"
2. Ask the agent: "Please evaluate this PR based on the instructions in this file and save the results to the exact file path specified"
3. Wait for the agent to complete the evaluation
4. Make sure the agent saves the results to exactly: `{results_file}`
5. Check that the file has been created successfully

## Repository and PR Information
- Repository: {repo_name}
- PR Number: {pr_number}
- PR URL: {pr_url}
- Diff File: {os.path.abspath(diff_file)}

## Evaluation Criteria (For the Agent)
Dear Agent, please evaluate the bug fix based on the following criteria:

1. **Correctness (1-10)**: Does the fix correctly address the bug?
2. **Completeness (1-10)**: Does the fix address all aspects of the bug?
3. **Code Quality (1-10)**: Is the code clean, readable, and well-structured?
4. **Efficiency (1-10)**: Is the fix efficient in terms of performance?
5. **Testing (1-10)**: Does the fix include appropriate tests?
6. **Documentation (1-10)**: Is the fix well-documented?

## Output Format (For the Agent)
Your evaluation must be saved as a JSON file at EXACTLY this path:
`{results_file}`

The JSON must have the following structure:
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
    "code_quality": {{
      "score": 9,
      "explanation": "The code is clean and readable...",
      "strength": "Good variable names and structure...",
      "weakness": "Minor deviation from project conventions..."
    }},
    "efficiency": {{
      "score": 8,
      "explanation": "The solution is reasonably efficient...",
      "strength": "Avoids unnecessary computations...",
      "weakness": "Could use a more optimized algorithm for X..."
    }},
    "testing": {{
      "score": 7,
      "explanation": "Tests cover the main scenarios...",
      "strength": "Good test structure...",
      "weakness": "Missing tests for edge cases..."
    }},
    "documentation": {{
      "score": 8,
      "explanation": "Documentation is clear...",
      "strength": "Good comments and PR description...",
      "weakness": "Could explain the rationale better..."
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

## PR Diff File
The PR diff is available at: {os.path.abspath(diff_file)}

You should analyze this diff file to understand the changes made in the PR.

## Saving the Results (CRITICAL)
After completing your evaluation:
1. You MUST create a JSON file with the evaluation results at this EXACT path:
   `{results_file}`
2. The file MUST follow the structure shown above
3. Make sure the file is correctly formatted JSON
4. Confirm when the file has been successfully created

This is crucial for the Bug Fix Evaluator to process your results.
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

    def open_in_cursor(self, file_path: str) -> bool:
        """Open a file in Cursor.

        Args:
            file_path: Path to the file to open.

        Returns:
            bool: True if successful, False otherwise.
        """
        self.logger.info(f"Opening file in Cursor: {file_path}")
        try:
            # Try to find cursor executable
            cursor_cmd = "cursor"
            
            # On macOS, also try the app bundle
            if os.path.exists("/Applications/Cursor.app"):
                cursor_cmd = "open -a Cursor"
            
            # Execute the command
            cmd = f"{cursor_cmd} {file_path}"
            subprocess.run(cmd, shell=True, check=True)
            return True
        except Exception as e:
            self.logger.error(f"Error opening file in Cursor: {e}")
            return False

    def cleanup(self):
        """Clean up temporary files."""
        if self.auto_cleanup and self.work_dir and os.path.exists(self.work_dir) and self.work_dir != ".":
            self.logger.info(f"Cleaning up work directory: {self.work_dir}")
            shutil.rmtree(self.work_dir)
        else:
            self.logger.info(f"Skipping cleanup of work directory: {self.work_dir}")
            print(f"\n⚠️ Note: Temporary files in {self.work_dir} were not cleaned up.")
            print(f"You may want to manually delete this directory when you're done.\n")

    def __del__(self):
        """Destructor to ensure cleanup."""
        if self.auto_cleanup:
            try:
                self.cleanup()
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}") 