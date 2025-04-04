"""
Repository handling module for Bug Fix Evaluator.

This module provides classes for working with git repositories, including
cloning, checking out specific commits, and comparing changes.
"""

import os
import re
import tempfile
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import subprocess

import git
from git import Repo, GitCommandError

logger = logging.getLogger(__name__)

class RepositoryHandler:
    """
    Handles git repository operations including cloning, checkout, and diff analysis.
    """
    
    def __init__(self, work_dir: Optional[str] = None):
        """
        Initialize the repository handler with a working directory.
        
        Args:
            work_dir: Optional directory to use for git operations. If not provided,
                     a temporary directory will be created.
        """
        self.work_dir = work_dir or tempfile.mkdtemp(prefix="bug_fix_evaluator_")
        logger.info(f"Using work directory: {self.work_dir}")
        
    def clone_repository(self, repo_url: str, target_dir: Optional[str] = None) -> str:
        """
        Clone a git repository to a specified directory.
        
        Args:
            repo_url: URL of the git repository to clone
            target_dir: Optional target directory name (relative to work_dir)
                        If not provided, a directory name will be derived from the URL.
        
        Returns:
            Path to the cloned repository
        
        Raises:
            GitCommandError: If the clone operation fails
        """
        if target_dir is None:
            # Extract repo name from URL
            repo_name = repo_url.split('/')[-1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            target_dir = repo_name
        
        repo_path = os.path.join(self.work_dir, target_dir)
        
        # Check if repo already exists
        if os.path.exists(repo_path):
            logger.info(f"Repository already exists at {repo_path}, skipping clone")
            return repo_path
        
        # Create target directory if it doesn't exist
        os.makedirs(os.path.dirname(repo_path), exist_ok=True)
        
        try:
            logger.info(f"Cloning repository {repo_url} to {repo_path}")
            Repo.clone_from(repo_url, repo_path)
            return repo_path
        except GitCommandError as e:
            logger.error(f"Failed to clone repository {repo_url}: {e}")
            raise
    
    def checkout_commit(self, repo_path: str, commit_sha: str) -> bool:
        """
        Checkout a specific commit in a repository.
        
        Args:
            repo_path: Path to the git repository
            commit_sha: Commit SHA to checkout
        
        Returns:
            True if checkout was successful, False otherwise
        
        Raises:
            GitCommandError: If the checkout operation fails
        """
        try:
            repo = Repo(repo_path)
            logger.info(f"Checking out commit {commit_sha} in {repo_path}")
            repo.git.checkout(commit_sha)
            return True
        except GitCommandError as e:
            logger.error(f"Failed to checkout commit {commit_sha}: {e}")
            raise
    
    def checkout_parent_commit(self, repo_path: str, commit_sha: str) -> str:
        """
        Checkout the parent of a specific commit.
        
        Args:
            repo_path: Path to the git repository
            commit_sha: Child commit SHA
        
        Returns:
            SHA of the parent commit that was checked out
        
        Raises:
            GitCommandError: If the checkout operation fails
            ValueError: If the commit has no parent (e.g., initial commit)
        """
        try:
            repo = Repo(repo_path)
            commit = repo.commit(commit_sha)
            
            if not commit.parents:
                raise ValueError(f"Commit {commit_sha} has no parent commits (it may be the initial commit)")
            
            parent_sha = commit.parents[0].hexsha
            logger.info(f"Checking out parent commit {parent_sha} of {commit_sha}")
            repo.git.checkout(parent_sha)
            return parent_sha
        except GitCommandError as e:
            logger.error(f"Failed to checkout parent of commit {commit_sha}: {e}")
            raise
    
    def get_commit_diff(self, repo_path: str, commit_sha: str) -> Dict[str, Any]:
        """
        Get the diff information for a specific commit.
        
        Args:
            repo_path: Path to the git repository
            commit_sha: Commit SHA to analyze
        
        Returns:
            Dictionary containing diff information including:
            - files: List of modified files
            - insertions: Number of inserted lines
            - deletions: Number of deleted lines
            - diffs: Dictionary mapping filenames to their diffs
        
        Raises:
            GitCommandError: If the diff operation fails
        """
        try:
            repo = Repo(repo_path)
            commit = repo.commit(commit_sha)
            parent = commit.parents[0] if commit.parents else None
            
            if parent is None:
                # For initial commit, compare with empty tree
                diff_index = commit.diff(git.NULL_TREE)
            else:
                diff_index = parent.diff(commit)
            
            result = {
                "files": [],
                "insertions": 0,
                "deletions": 0,
                "diffs": {}
            }
            
            for diff_item in diff_index:
                file_path = diff_item.b_path if diff_item.b_path else diff_item.a_path
                
                # Skip binary files
                if diff_item.diff:
                    try:
                        diff_text = diff_item.diff.decode('utf-8')
                    except UnicodeDecodeError:
                        logger.warning(f"Could not decode diff for {file_path}, skipping")
                        continue
                else:
                    diff_text = ""
                
                # Count insertions and deletions
                insertions = len([l for l in diff_text.split('\n') if l.startswith('+')])
                deletions = len([l for l in diff_text.split('\n') if l.startswith('-')])
                
                file_info = {
                    "path": file_path,
                    "insertions": insertions,
                    "deletions": deletions,
                    "diff": diff_text,
                    "status": self._get_change_type(diff_item)
                }
                
                result["files"].append(file_info)
                result["diffs"][file_path] = diff_text
                result["insertions"] += insertions
                result["deletions"] += deletions
            
            return result
        except GitCommandError as e:
            logger.error(f"Failed to get diff for commit {commit_sha}: {e}")
            raise
    
    def compare_branches(self, repo_path: str, base_branch: str, target_branch: str) -> Dict[str, Any]:
        """
        Compare two branches and return diff information.
        
        Args:
            repo_path: Path to the git repository
            base_branch: Base branch name or commit SHA
            target_branch: Target branch name or commit SHA
        
        Returns:
            Dictionary with diff information similar to get_commit_diff
        
        Raises:
            GitCommandError: If the diff operation fails
        """
        try:
            repo = Repo(repo_path)
            diff_index = repo.git.diff(base_branch, target_branch, name_only=True).split('\n')
            
            result = {
                "files": [],
                "insertions": 0,
                "deletions": 0,
                "diffs": {}
            }
            
            for file_path in diff_index:
                if not file_path:  # Skip empty lines
                    continue
                
                # Get the diff for this file
                diff_text = repo.git.diff(base_branch, target_branch, '--', file_path)
                
                # Count insertions and deletions
                insertions = len([l for l in diff_text.split('\n') if l.startswith('+')])
                deletions = len([l for l in diff_text.split('\n') if l.startswith('-')])
                
                file_info = {
                    "path": file_path,
                    "insertions": insertions,
                    "deletions": deletions,
                    "diff": diff_text,
                    "status": "modified"  # Simplified status
                }
                
                result["files"].append(file_info)
                result["diffs"][file_path] = diff_text
                result["insertions"] += insertions
                result["deletions"] += deletions
            
            return result
        except GitCommandError as e:
            logger.error(f"Failed to compare branches {base_branch} and {target_branch}: {e}")
            raise
    
    def extract_changes_from_patch(self, patch: str) -> Dict[str, List[int]]:
        """
        Extract line numbers of added and removed lines from a git patch.
        
        Args:
            patch: Git patch string
            
        Returns:
            Dictionary with 'added' and 'removed' line numbers
        """
        if not patch:
            return {"added": [], "removed": []}
        
        added_lines = []
        removed_lines = []
        
        current_line = None
        
        # Parse the patch to find added/removed lines
        for line in patch.split('\n'):
            if line.startswith('@@'):
                # Extract starting line number from the @@ -a,b +c,d @@ format
                match = re.search(r'\+(\d+)', line)
                if match:
                    current_line = int(match.group(1))
                else:
                    current_line = None
                continue
                
            if current_line is not None:
                if line.startswith('+') and not line.startswith('+++'):
                    added_lines.append(current_line)
                    current_line += 1
                elif line.startswith('-') and not line.startswith('---'):
                    removed_lines.append(current_line)
                    # Don't increment current_line for removed lines as they don't exist in the final file
                else:
                    current_line += 1
        
        return {"added": added_lines, "removed": removed_lines}
    
    def get_file_content(self, repo_path: str, file_path: str) -> Optional[str]:
        """
        Get the content of a file in the repository at the current checked-out commit.
        
        Args:
            repo_path: Path to the git repository
            file_path: Path to the file, relative to repo root
            
        Returns:
            Content of the file as a string, or None if file doesn't exist
        """
        full_path = os.path.join(repo_path, file_path)
        
        if not os.path.exists(full_path):
            logger.warning(f"File {file_path} does not exist in {repo_path}")
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (IOError, UnicodeDecodeError) as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None
    
    def create_branch(self, repo_path: str, branch_name: str, start_point: Optional[str] = None) -> bool:
        """
        Create a new git branch.
        
        Args:
            repo_path: Path to the git repository
            branch_name: Name of the branch to create
            start_point: Optional starting point (commit or branch) for the new branch
        
        Returns:
            True if branch was created successfully, False otherwise
        """
        try:
            repo = Repo(repo_path)
            
            # Check if branch already exists
            if branch_name in repo.git.branch('--list').split('\n'):
                logger.warning(f"Branch {branch_name} already exists")
                return False
            
            if start_point:
                repo.git.branch(branch_name, start_point)
            else:
                repo.git.branch(branch_name)
                
            logger.info(f"Created branch {branch_name}")
            return True
        except GitCommandError as e:
            logger.error(f"Failed to create branch {branch_name}: {e}")
            return False
    
    def checkout_branch(self, repo_path: str, branch_name: str) -> bool:
        """
        Checkout a git branch.
        
        Args:
            repo_path: Path to the git repository
            branch_name: Name of the branch to checkout
        
        Returns:
            True if branch was checked out successfully, False otherwise
        """
        try:
            repo = Repo(repo_path)
            repo.git.checkout(branch_name)
            logger.info(f"Checked out branch {branch_name}")
            return True
        except GitCommandError as e:
            logger.error(f"Failed to checkout branch {branch_name}: {e}")
            return False
    
    def parse_pr_url(self, pr_url: str) -> Tuple[str, str, str]:
        """
        Parse a GitHub PR URL into its components.
        
        Args:
            pr_url: URL of the GitHub PR
            
        Returns:
            Tuple of (owner, repo, pr_number)
        
        Raises:
            ValueError: If the URL is not a valid GitHub PR URL
        """
        # Example URL: https://github.com/alikayaa/bug_fix_evaluator/pull/123
        pattern = r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
        match = re.match(pattern, pr_url)
        
        if not match:
            raise ValueError(f"Invalid GitHub PR URL: {pr_url}")
        
        owner, repo, pr_number = match.groups()
        return owner, repo, pr_number
    
    def _get_change_type(self, diff_item: git.diff.Diff) -> str:
        """
        Determine the type of change for a diff item.
        
        Args:
            diff_item: Git diff item
        
        Returns:
            String representing the change type: 'added', 'deleted', 'modified', or 'renamed'
        """
        if diff_item.new_file:
            return "added"
        elif diff_item.deleted_file:
            return "deleted"
        elif diff_item.renamed:
            return "renamed"
        else:
            return "modified"
    
    def cleanup(self) -> None:
        """
        Clean up temporary directories created by the repository handler.
        """
        if os.path.exists(self.work_dir) and self.work_dir.startswith(tempfile.gettempdir()):
            logger.info(f"Cleaning up work directory: {self.work_dir}")
            import shutil
            shutil.rmtree(self.work_dir)
