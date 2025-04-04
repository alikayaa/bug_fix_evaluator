#!/usr/bin/env python3
import json
import os
import re
import subprocess
from typing import Dict, List, Any, Optional, Tuple
import urllib.request
import urllib.parse
import base64

class GitHubPRParser:
    def __init__(self, token: str = None):
        """
        Initialize the GitHub PR parser.
        
        Args:
            token: Optional GitHub API token for authentication
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.headers = {}
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def _make_api_request(self, url: str) -> Dict[str, Any]:
        """
        Make a request to the GitHub API.
        
        Args:
            url: GitHub API URL
            
        Returns:
            JSON response as dictionary
        """
        request = urllib.request.Request(url, headers=self.headers)
        
        try:
            with urllib.request.urlopen(request) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            print(f"Error making API request: {e}")
            print(f"Response: {e.read().decode()}")
            return {}
    
    def parse_pr_url(self, pr_url: str) -> Tuple[str, str, str]:
        """
        Parse a GitHub PR URL to extract owner, repo, and PR number.
        
        Args:
            pr_url: GitHub PR URL
            
        Returns:
            Tuple of (owner, repo, pr_number)
        """
        # Example URL: https://github.com/owner/repo/pull/123
        match = re.match(r"https://github.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
        
        if not match:
            raise ValueError(f"Invalid GitHub PR URL: {pr_url}")
        
        return match.groups()
    
    def fetch_pr_data(self, pr_url: str) -> Dict[str, Any]:
        """
        Fetch PR data from GitHub.
        
        Args:
            pr_url: GitHub PR URL
            
        Returns:
            Dictionary containing PR data
        """
        owner, repo, pr_number = self.parse_pr_url(pr_url)
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        
        pr_data = self._make_api_request(api_url)
        
        if not pr_data:
            raise ValueError(f"Failed to fetch PR data for {pr_url}")
        
        # Fetch PR files
        files_url = f"{api_url}/files"
        files_data = self._make_api_request(files_url)
        
        # Fetch PR commits
        commits_url = f"{api_url}/commits"
        commits_data = self._make_api_request(commits_url)
        
        # Fetch PR comments
        comments_url = f"{api_url}/comments"
        comments_data = self._make_api_request(comments_url)
        
        return {
            "pr": pr_data,
            "files": files_data,
            "commits": commits_data,
            "comments": comments_data
        }
    
    def extract_pr_metadata(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from PR data.
        
        Args:
            pr_data: PR data dictionary
            
        Returns:
            Dictionary containing PR metadata
        """
        pr = pr_data["pr"]
        
        return {
            "number": pr["number"],
            "title": pr["title"],
            "description": pr["body"],
            "state": pr["state"],
            "created_at": pr["created_at"],
            "closed_at": pr["closed_at"],
            "merged_at": pr["merged_at"],
            "author": pr["user"]["login"],
            "labels": [label["name"] for label in pr.get("labels", [])],
            "milestone": pr.get("milestone", {}).get("title"),
            "draft": pr.get("draft", False)
        }
    
    def extract_file_changes(self, pr_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract file changes from PR data.
        
        Args:
            pr_data: PR data dictionary
            
        Returns:
            List of file change dictionaries
        """
        files = pr_data["files"]
        
        return [
            {
                "filename": file["filename"],
                "status": file["status"],  # added, modified, removed
                "additions": file["additions"],
                "deletions": file["deletions"],
                "changes": file["changes"],
                "patch": file.get("patch"),
                "raw_url": file.get("raw_url")
            }
            for file in files
        ]
    
    def extract_commit_messages(self, pr_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract commit messages from PR data.
        
        Args:
            pr_data: PR data dictionary
            
        Returns:
            List of commit message dictionaries
        """
        commits = pr_data["commits"]
        
        return [
            {
                "sha": commit["sha"],
                "message": commit["commit"]["message"],
                "author": commit["commit"]["author"]["name"],
                "email": commit["commit"]["author"]["email"],
                "date": commit["commit"]["author"]["date"]
            }
            for commit in commits
        ]
    
    def extract_pr_comments(self, pr_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract PR comments from PR data.
        
        Args:
            pr_data: PR data dictionary
            
        Returns:
            List of comment dictionaries
        """
        comments = pr_data["comments"]
        
        return [
            {
                "id": comment["id"],
                "body": comment["body"],
                "user": comment["user"]["login"],
                "created_at": comment["created_at"],
                "updated_at": comment["updated_at"]
            }
            for comment in comments
        ]
    
    def fetch_file_content(self, owner: str, repo: str, path: str, ref: str) -> str:
        """
        Fetch file content from GitHub.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            ref: Branch or commit SHA
            
        Returns:
            File content as string
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}"
        
        content_data = self._make_api_request(url)
        
        if not content_data or "content" not in content_data:
            raise ValueError(f"Failed to fetch file content for {path} at {ref}")
        
        # GitHub API returns content as base64 encoded
        return base64.b64decode(content_data["content"]).decode()
    
    def clone_repository(self, owner: str, repo: str, target_dir: str) -> str:
        """
        Clone a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            target_dir: Target directory for clone
            
        Returns:
            Path to cloned repository
        """
        repo_url = f"https://github.com/{owner}/{repo}.git"
        repo_dir = os.path.join(target_dir, repo)
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # Clone the repository
        subprocess.run(["git", "clone", repo_url, repo_dir], check=True)
        
        return repo_dir
    
    def checkout_pr(self, repo_dir: str, pr_number: str) -> None:
        """
        Checkout a PR branch.
        
        Args:
            repo_dir: Path to repository directory
            pr_number: PR number
        """
        # Fetch the PR
        subprocess.run(
            ["git", "fetch", "origin", f"pull/{pr_number}/head:pr-{pr_number}"],
            cwd=repo_dir,
            check=True
        )
        
        # Checkout the PR branch
        subprocess.run(
            ["git", "checkout", f"pr-{pr_number}"],
            cwd=repo_dir,
            check=True
        )
    
    def parse_pr(self, pr_url: str) -> Dict[str, Any]:
        """
        Parse a GitHub PR and extract all relevant information.
        
        Args:
            pr_url: GitHub PR URL
            
        Returns:
            Dictionary containing PR data
        """
        pr_data = self.fetch_pr_data(pr_url)
        
        return {
            "metadata": self.extract_pr_metadata(pr_data),
            "files": self.extract_file_changes(pr_data),
            "commits": self.extract_commit_messages(pr_data),
            "comments": self.extract_pr_comments(pr_data),
            "source": pr_url
        } 