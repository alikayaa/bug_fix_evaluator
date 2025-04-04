"""
Cursor Agent Evaluator for Bug Fix Cursor Evaluator.

This module provides the main evaluator class for preparing GitHub PRs for
evaluation with Cursor's agent mode.
"""

import os
import logging
import tempfile
from typing import Dict, Any, Optional

from .repository import RepositoryHandler
from .reporter import ReportGenerator
from .utils import setup_logger

logger = logging.getLogger(__name__)

class CursorAgentEvaluator:
    """
    Evaluator for Cursor agent evaluations of bug fixes
    """
    
    def __init__(self, pr_url: str, verbose: bool = False):
        """
        Initialize the evaluator with a PR URL
        
        Args:
            pr_url: URL of the pull request to evaluate
            verbose: Whether to enable verbose logging
        """
        self.pr_url = pr_url
        self.verbose = verbose
        self.repo_name = None
        self.pr_number = None
        self.temp_dir = tempfile.mkdtemp(prefix="cursor_agent_evaluation_")
        
        # Set up logging
        level = logging.DEBUG if verbose else logging.INFO
        setup_logger(level=level)
        logger.info(f"Initializing Cursor agent evaluator for PR: {pr_url}")
        
        # Initialize repository handler and reporter
        self.repo_handler = RepositoryHandler()
        self.reporter = ReportGenerator(output_dir=os.path.join(self.temp_dir, "output"))
        
        # Parse PR URL to get repository and PR number
        self._parse_pr_url()
    
    def _parse_pr_url(self):
        """Parse the PR URL to extract repository and PR number"""
        self.repo_name, self.pr_number = self.repo_handler.parse_pr_url(self.pr_url)
    
    def evaluate_pr(self, report_format: str = 'html') -> Dict[str, Any]:
        """
        Prepare a PR for evaluation with Cursor agent mode
        
        Args:
            report_format: Format for the report (html, markdown, json, text)
            
        Returns:
            Dictionary with paths to instruction file, diff file, and expected results file
        """
        logger.info(f"Preparing PR for evaluation: {self.pr_url} with format {report_format}")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.reporter.output_dir, exist_ok=True)
        
        # Get the PR diff directly from GitHub API
        owner, repo = self.repo_name.split('/')
        pr_diff = self.repo_handler.get_pr_diff_from_github(owner, repo, self.pr_number)
        
        # If that fails, warn user
        if not pr_diff:
            logger.warning(f"Could not fetch PR diff from GitHub API. Consider using a GITHUB_TOKEN environment variable.")
        
        # Write the diff to a file
        diff_file_path = os.path.join(self.temp_dir, "pr_diff.txt")
        with open(diff_file_path, 'w') as f:
            f.write(pr_diff or "")
        
        # Create instruction file for Cursor agent
        instruction_file_path = os.path.join(self.temp_dir, "cursor_instructions.md")
        self._create_instruction_file(instruction_file_path, diff_file_path)
        
        # Create expected results file path
        expected_results_file = os.path.join(self.temp_dir, "evaluation_results.json")
        
        return {
            "instruction_file": instruction_file_path,
            "diff_file": diff_file_path,
            "expected_results_file": expected_results_file,
            "report_format": report_format
        }
    
    def _create_instruction_file(self, instruction_file_path: str, diff_file_path: str) -> None:
        """
        Create instruction file for Cursor agent
        
        Args:
            instruction_file_path: Path to write instructions to
            diff_file_path: Path to the PR diff file
        """
        instructions = f"""# Bug Fix Evaluation with Cursor Agent

## Overview
You've been asked to evaluate a bug fix in pull request #{self.pr_number} from repository `{self.repo_name}`. This evaluation will use Cursor's AI agent capabilities to analyze code quality, correctness, and other aspects of the fix.

## How to Use This File
1. **Activate Cursor's Agent Mode**: Use the "Ask Agent" button or press Ctrl+I (Cmd+I on Mac) to interact with Cursor's AI.
2. **Ask the Agent to Evaluate**: Prompt the agent with "Please evaluate this bug fix PR based on the criteria outlined in this document."
3. **Save Results**: The agent will provide an evaluation - you'll need to help it save the results as a JSON file (instructions below).

## PR Information
- **Repository**: [{self.repo_name}](https://github.com/{self.repo_name})
- **PR Number**: [#{self.pr_number}](https://github.com/{self.repo_name}/pull/{self.pr_number})
- **Diff File**: [{diff_file_path}]({diff_file_path})

## Evaluation Criteria
The agent should evaluate the PR based on these criteria, with a score from 0-10 and explanation for each:

1. **Correctness (30%)**: Does the fix properly address the root cause of the bug?
2. **Completeness (15%)**: Does the fix address all aspects of the bug without missing edge cases?
3. **Code Quality (15%)**: Is the code well-structured, readable, and maintainable?
4. **Efficiency (15%)**: Is the fix efficient in terms of performance and resource usage?
5. **Testing (10%)**: Does the fix include appropriate tests or test updates?
6. **Documentation (15%)**: Is the fix well-documented with comments, PR description, etc?

## Results Format
After the evaluation, the agent should save the results as a JSON file named `evaluation_results.json` in the same directory as this file. The format should be:

```json
{{
  "repository": "{self.repo_name}",
  "pr_number": {self.pr_number},
  "criteria": {{
    "correctness": {{
      "score": 8,
      "explanation": "The fix correctly addresses the race condition by adding proper synchronization...",
      "strength": "Properly identifies and fixes the root cause",
      "weakness": "Could be more robust against potential deadlocks"
    }},
    "completeness": {{ ... }},
    "code_quality": {{ ... }},
    "efficiency": {{ ... }},
    "testing": {{ ... }},
    "documentation": {{ ... }}
  }},
  "overall": {{
    "score": 7.5,
    "strengths": [
      "Thorough understanding of the underlying issue",
      "Clean implementation with good variable names"
    ],
    "weaknesses": [
      "Missing tests for edge case X",
      "Could use more inline documentation"
    ],
    "suggestions": [
      "Add test for concurrent access pattern",
      "Consider adding a comment explaining the synchronization approach"
    ]
  }}
}}
```

## Saving the JSON Output
Tell the agent to:

1. Format the evaluation results as JSON using the structure above
2. Save the results to a file named `evaluation_results.json` in this directory
3. You can copy the JSON and save it manually, or have the agent help create the file

## Next Steps
After the agent completes the evaluation and the results are saved, you can generate a detailed HTML report by running:

```
bug-fix-cursor-results {os.path.join(os.path.dirname(instruction_file_path), "evaluation_results.json")} --open
```

This will process the results and open an HTML report in your browser.
"""

        with open(instruction_file_path, 'w') as f:
            f.write(instructions)
        
        logger.info(f"Created instruction file at: {instruction_file_path}") 