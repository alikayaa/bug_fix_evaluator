"""
Repository handling module for Bug Fix Cursor Evaluator.

This module provides functionality for working with GitHub repositories,
specifically for fetching PR diffs and other repository-related operations.
"""

import os
import re
import logging
import requests
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class RepositoryHandler:
    """
    Handles repository operations including fetching PR diffs.
    """
    
    def __init__(self):
        """Initialize the repository handler."""
        self.repo_name = None
        self.pr_number = None
        logger.info("Repository handler initialized")
    
    def parse_pr_url(self, pr_url: str) -> Tuple[str, int]:
        """
        Parse a GitHub PR URL to extract repository name and PR number
        
        Args:
            pr_url: URL of the GitHub pull request
            
        Returns:
            Tuple of (repo_name, pr_number)
            
        Raises:
            ValueError: If the URL is not a valid GitHub PR URL
        """
        # Parse GitHub PR URL format: https://github.com/owner/repo/pull/123
        pattern = r'https?://github\.com/([^/]+/[^/]+)/pull/(\d+)'
        match = re.search(pattern, pr_url)
        
        if not match:
            raise ValueError(f"Invalid GitHub PR URL: {pr_url}")
        
        self.repo_name = match.group(1)
        self.pr_number = int(match.group(2))
        logger.info(f"Parsed PR URL: repository={self.repo_name}, PR number={self.pr_number}")
        
        return self.repo_name, self.pr_number
    
    def get_pr_diff_from_github(self, owner: str, repo_name: str, pr_number: int) -> Optional[str]:
        """
        Get the diff for a specific PR directly from GitHub API.
        
        Args:
            owner: Owner of the repository
            repo_name: Name of the repository
            pr_number: PR number
            
        Returns:
            Diff of the PR as a string, or None if failed
        """
        url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pr_number}"
        
        headers = {
            "Accept": "application/vnd.github.v3.diff"
        }
        
        # Add GitHub token if available
        github_token = os.environ.get("GITHUB_TOKEN")
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            logger.info(f"Successfully fetched PR diff from GitHub API: {pr_number}")
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching PR diff from GitHub API: {str(e)}")
            return None 