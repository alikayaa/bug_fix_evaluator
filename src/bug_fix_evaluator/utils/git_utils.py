"""
Git utilities module for Bug Fix Evaluator.

This module provides utility functions for Git operations.
"""

import os
import re
import logging
import subprocess
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)

def run_git_command(command: List[str], cwd: str) -> Tuple[bool, str]:
    """
    Run a git command in the specified directory.
    
    Args:
        command: Git command as a list of arguments
        cwd: Working directory to run the command in
        
    Returns:
        Tuple of (success, output) where:
        - success: True if the command executed successfully, False otherwise
        - output: Command output or error message
    """
    try:
        # Add 'git' as the first argument
        git_command = ['git'] + command
        
        # Run the command
        process = subprocess.Popen(
            git_command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Get the output
        stdout, stderr = process.communicate()
        
        # Check if the command was successful
        if process.returncode == 0:
            return True, stdout.strip()
        else:
            logger.error(f"Git command failed: {' '.join(git_command)}")
            logger.error(f"Error: {stderr.strip()}")
            return False, stderr.strip()
    except Exception as e:
        logger.error(f"Exception running git command: {e}")
        return False, str(e)

def is_git_repository(path: str) -> bool:
    """
    Check if the specified path is a git repository.
    
    Args:
        path: Path to check
        
    Returns:
        True if the path is a git repository, False otherwise
    """
    git_dir = os.path.join(path, '.git')
    return os.path.exists(git_dir) and os.path.isdir(git_dir)

def get_commit_info(repo_path: str, commit_sha: str) -> Dict[str, Any]:
    """
    Get information about a commit.
    
    Args:
        repo_path: Path to the git repository
        commit_sha: SHA of the commit
        
    Returns:
        Dictionary with commit information:
        - sha: Full SHA hash
        - short_sha: Short SHA hash
        - author: Author name
        - author_email: Author email
        - date: Commit date
        - message: Commit message
        - files: List of files changed in the commit
    """
    if not is_git_repository(repo_path):
        raise ValueError(f"Not a git repository: {repo_path}")
    
    result = {}
    
    # Get commit information
    success, output = run_git_command(
        ['show', '--format=%H%n%h%n%an%n%ae%n%ad%n%s', '--name-only', commit_sha],
        repo_path
    )
    
    if not success:
        logger.error(f"Failed to get commit information for {commit_sha}")
        return result
    
    # Parse the output
    lines = output.splitlines()
    if len(lines) >= 6:
        result['sha'] = lines[0]
        result['short_sha'] = lines[1]
        result['author'] = lines[2]
        result['author_email'] = lines[3]
        result['date'] = lines[4]
        result['message'] = lines[5]
        result['files'] = lines[6:]
    
    return result

def parse_patch(patch: str) -> Dict[str, Any]:
    """
    Parse a git patch to extract information about changes.
    
    Args:
        patch: Git patch content
        
    Returns:
        Dictionary with patch information:
        - files: List of dictionaries with file information:
          - old_path: Old file path
          - new_path: New file path
          - changes: List of change dictionaries:
            - type: Type of change ('added', 'removed', 'context')
            - line: Line content
            - line_num: Line number
    """
    result = {
        'files': []
    }
    
    # Split the patch into file sections
    file_pattern = re.compile(r'^diff --git a/(.*?) b/(.*?)$', re.MULTILINE)
    file_matches = file_pattern.findall(patch)
    
    file_sections = re.split(r'^diff --git', patch, flags=re.MULTILINE)
    if len(file_sections) > 1:
        # Skip the first empty section
        file_sections = file_sections[1:]
    
    for i, (old_path, new_path) in enumerate(file_matches):
        if i >= len(file_sections):
            continue
        
        file_patch = 'diff --git' + file_sections[i]
        file_info = {
            'old_path': old_path,
            'new_path': new_path,
            'changes': []
        }
        
        # Parse hunks in the file patch
        hunk_pattern = re.compile(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@', re.MULTILINE)
        hunk_matches = hunk_pattern.findall(file_patch)
        
        hunk_sections = re.split(r'^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@', file_patch, flags=re.MULTILINE)
        if len(hunk_sections) > 1:
            # Skip the header section
            hunk_sections = hunk_sections[1:]
        
        for j, (old_start, new_start) in enumerate(hunk_matches):
            if j >= len(hunk_sections):
                continue
            
            old_line_num = int(old_start)
            new_line_num = int(new_start)
            
            for line in hunk_sections[j].splitlines():
                if not line:
                    continue
                
                if line.startswith(' '):
                    # Context line
                    file_info['changes'].append({
                        'type': 'context',
                        'line': line[1:],
                        'old_line_num': old_line_num,
                        'new_line_num': new_line_num
                    })
                    old_line_num += 1
                    new_line_num += 1
                elif line.startswith('-'):
                    # Removed line
                    file_info['changes'].append({
                        'type': 'removed',
                        'line': line[1:],
                        'old_line_num': old_line_num,
                        'new_line_num': None
                    })
                    old_line_num += 1
                elif line.startswith('+'):
                    # Added line
                    file_info['changes'].append({
                        'type': 'added',
                        'line': line[1:],
                        'old_line_num': None,
                        'new_line_num': new_line_num
                    })
                    new_line_num += 1
        
        result['files'].append(file_info)
    
    return result

def create_patch(old_file: str, new_file: str, old_path: Optional[str] = None, new_path: Optional[str] = None) -> str:
    """
    Create a git-style patch from two files.
    
    Args:
        old_file: Content of the old file
        new_file: Content of the new file
        old_path: Optional path to show for the old file (default: 'a/file')
        new_path: Optional path to show for the new file (default: 'b/file')
        
    Returns:
        Git-style patch content
    """
    import difflib
    
    old_path = old_path or 'a/file'
    new_path = new_path or 'b/file'
    
    # Split content into lines
    old_lines = old_file.splitlines()
    new_lines = new_file.splitlines()
    
    # Generate unified diff
    diff_lines = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f'a/{old_path}',
        tofile=f'b/{new_path}',
        lineterm=''
    )
    
    # Convert to string
    return '\n'.join(diff_lines)

def get_file_at_commit(repo_path: str, file_path: str, commit_sha: str) -> Optional[str]:
    """
    Get the content of a file at a specific commit.
    
    Args:
        repo_path: Path to the git repository
        file_path: Path to the file, relative to the repository root
        commit_sha: SHA of the commit
        
    Returns:
        File content as a string, or None if the file doesn't exist at that commit
    """
    if not is_git_repository(repo_path):
        raise ValueError(f"Not a git repository: {repo_path}")
    
    success, output = run_git_command(
        ['show', f'{commit_sha}:{file_path}'],
        repo_path
    )
    
    if not success:
        logger.warning(f"Failed to get file {file_path} at commit {commit_sha}")
        return None
    
    return output

def get_commit_diff(repo_path: str, commit_sha: str) -> Optional[str]:
    """
    Get the diff for a specific commit.
    
    Args:
        repo_path: Path to the git repository
        commit_sha: SHA of the commit
        
    Returns:
        Diff content as a string, or None if the commit doesn't exist
    """
    if not is_git_repository(repo_path):
        raise ValueError(f"Not a git repository: {repo_path}")
    
    success, output = run_git_command(
        ['show', '--patch', commit_sha],
        repo_path
    )
    
    if not success:
        logger.warning(f"Failed to get diff for commit {commit_sha}")
        return None
    
    return output

def clone_repository(repo_url: str, target_dir: str) -> bool:
    """
    Clone a git repository.
    
    Args:
        repo_url: URL of the git repository
        target_dir: Target directory to clone into
        
    Returns:
        True if the clone was successful, False otherwise
    """
    if os.path.exists(target_dir):
        if is_git_repository(target_dir):
            logger.info(f"Repository already exists at {target_dir}")
            return True
        else:
            logger.error(f"Target directory exists but is not a git repository: {target_dir}")
            return False
    
    # Create parent directory if it doesn't exist
    parent_dir = os.path.dirname(target_dir)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
    
    success, output = run_git_command(
        ['clone', repo_url, target_dir],
        os.path.dirname(target_dir) or '.'
    )
    
    if not success:
        logger.error(f"Failed to clone repository {repo_url} to {target_dir}")
        return False
    
    logger.info(f"Cloned repository {repo_url} to {target_dir}")
    return True

def pull_repository(repo_path: str) -> bool:
    """
    Pull the latest changes from a git repository.
    
    Args:
        repo_path: Path to the git repository
        
    Returns:
        True if the pull was successful, False otherwise
    """
    if not is_git_repository(repo_path):
        raise ValueError(f"Not a git repository: {repo_path}")
    
    success, output = run_git_command(
        ['pull'],
        repo_path
    )
    
    if not success:
        logger.error(f"Failed to pull repository at {repo_path}")
        return False
    
    logger.info(f"Pulled repository at {repo_path}")
    return True

def checkout_commit(repo_path: str, commit_sha: str) -> bool:
    """
    Checkout a specific commit in a git repository.
    
    Args:
        repo_path: Path to the git repository
        commit_sha: SHA of the commit to checkout
        
    Returns:
        True if the checkout was successful, False otherwise
    """
    if not is_git_repository(repo_path):
        raise ValueError(f"Not a git repository: {repo_path}")
    
    success, output = run_git_command(
        ['checkout', commit_sha],
        repo_path
    )
    
    if not success:
        logger.error(f"Failed to checkout commit {commit_sha} in {repo_path}")
        return False
    
    logger.info(f"Checked out commit {commit_sha} in {repo_path}")
    return True
