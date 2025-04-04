"""
Core module for Bug Fix Evaluator.

This module provides the main classes and functionality for evaluating bug fixes.
"""

import os
import logging
import tempfile
from typing import Dict, List, Optional, Any, Union, Tuple

from .repository import RepositoryHandler
from .analyzer import CodeAnalyzer
from .metrics import EvaluationMetrics
from .reporter import ReportGenerator

logger = logging.getLogger(__name__)

class BugFixEvaluator:
    """
    Main class for evaluating bug fixes by comparing engineer and AI solutions.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the bug fix evaluator with optional configuration.
        
        Args:
            config: Optional configuration dictionary with evaluation settings
        """
        self.config = config or {}
        
        # Set up logging
        log_level = self.config.get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Initialize components
        self.repo_handler = RepositoryHandler(
            work_dir=self.config.get('work_dir')
        )
        self.analyzer = CodeAnalyzer()
        self.metrics = EvaluationMetrics(
            config=self.config.get('metrics')
        )
        self.reporter = ReportGenerator(
            config=self.config.get('report')
        )
        
        logger.info("BugFixEvaluator initialized")
    
    def evaluate_from_pr(self, 
                       engineer_pr_url: str, 
                       ai_pr_url: str,
                       report_format: str = 'json') -> Dict[str, Any]:
        """
        Evaluate bug fixes from PR URLs for engineer and AI solutions.
        
        Args:
            engineer_pr_url: URL to the engineer's PR
            ai_pr_url: URL to the AI's PR
            report_format: Format for the generated report
            
        Returns:
            Dictionary with evaluation results
        """
        logger.info(f"Evaluating bug fixes from PRs: engineer={engineer_pr_url}, ai={ai_pr_url}")
        
        # Clone and analyze repositories
        engineer_analysis = self._analyze_pr(engineer_pr_url)
        ai_analysis = self._analyze_pr(ai_pr_url)
        
        # Evaluate the bug fixes
        evaluation_result = self.metrics.evaluate(engineer_analysis, ai_analysis)
        
        # Generate report
        report_path = self.reporter.generate_report(evaluation_result, report_format)
        evaluation_result['report_path'] = report_path
        
        return evaluation_result
    
    def evaluate_from_commits(self, 
                           repo_url: str,
                           engineer_commit: str, 
                           ai_commit: str,
                           report_format: str = 'json') -> Dict[str, Any]:
        """
        Evaluate bug fixes from specific commits in a repository.
        
        Args:
            repo_url: URL to the git repository
            engineer_commit: SHA of the engineer's bug fix commit
            ai_commit: SHA of the AI's bug fix commit
            report_format: Format for the generated report
            
        Returns:
            Dictionary with evaluation results
        """
        logger.info(f"Evaluating bug fixes from commits: engineer={engineer_commit}, ai={ai_commit}")
        
        # Clone the repository
        repo_path = self.repo_handler.clone_repository(repo_url)
        
        # Analyze engineer's commit
        engineer_analysis = self._analyze_commit(repo_path, engineer_commit)
        
        # Analyze AI's commit
        ai_analysis = self._analyze_commit(repo_path, ai_commit)
        
        # Evaluate the bug fixes
        evaluation_result = self.metrics.evaluate(engineer_analysis, ai_analysis)
        
        # Generate report
        report_path = self.reporter.generate_report(evaluation_result, report_format)
        evaluation_result['report_path'] = report_path
        
        return evaluation_result
    
    def evaluate_from_directories(self, 
                                engineer_buggy_dir: str,
                                engineer_fixed_dir: str,
                                ai_buggy_dir: str,
                                ai_fixed_dir: str,
                                report_format: str = 'json') -> Dict[str, Any]:
        """
        Evaluate bug fixes from directories containing buggy and fixed code.
        
        Args:
            engineer_buggy_dir: Directory with engineer's buggy code
            engineer_fixed_dir: Directory with engineer's fixed code
            ai_buggy_dir: Directory with AI's buggy code
            ai_fixed_dir: Directory with AI's fixed code
            report_format: Format for the generated report
            
        Returns:
            Dictionary with evaluation results
        """
        logger.info("Evaluating bug fixes from directories")
        
        # Analyze engineer's changes
        engineer_analysis = self._analyze_directories(engineer_buggy_dir, engineer_fixed_dir)
        
        # Analyze AI's changes
        ai_analysis = self._analyze_directories(ai_buggy_dir, ai_fixed_dir)
        
        # Evaluate the bug fixes
        evaluation_result = self.metrics.evaluate(engineer_analysis, ai_analysis)
        
        # Generate report
        report_path = self.reporter.generate_report(evaluation_result, report_format)
        evaluation_result['report_path'] = report_path
        
        return evaluation_result
    
    def evaluate_from_patch_files(self, 
                                engineer_patch_file: str,
                                ai_patch_file: str,
                                repo_url: Optional[str] = None,
                                base_commit: Optional[str] = None,
                                report_format: str = 'json') -> Dict[str, Any]:
        """
        Evaluate bug fixes from patch files containing the changes.
        
        Args:
            engineer_patch_file: Path to engineer's patch file
            ai_patch_file: Path to AI's patch file
            repo_url: Optional repository URL to get additional context
            base_commit: Optional base commit to apply patches to
            report_format: Format for the generated report
            
        Returns:
            Dictionary with evaluation results
        """
        logger.info("Evaluating bug fixes from patch files")
        
        repo_path = None
        if repo_url:
            # Clone the repository if provided
            repo_path = self.repo_handler.clone_repository(repo_url)
            if base_commit:
                self.repo_handler.checkout_commit(repo_path, base_commit)
        
        # Analyze engineer's patch
        engineer_analysis = self._analyze_patch_file(engineer_patch_file, repo_path)
        
        # Analyze AI's patch
        ai_analysis = self._analyze_patch_file(ai_patch_file, repo_path)
        
        # Evaluate the bug fixes
        evaluation_result = self.metrics.evaluate(engineer_analysis, ai_analysis)
        
        # Generate report
        report_path = self.reporter.generate_report(evaluation_result, report_format)
        evaluation_result['report_path'] = report_path
        
        return evaluation_result
    
    def _analyze_pr(self, pr_url: str) -> Dict[str, Any]:
        """
        Analyze a GitHub PR to extract bug fix information.
        
        Args:
            pr_url: URL of the GitHub PR
            
        Returns:
            Dictionary with analysis results
        """
        # Parse PR URL to extract repo information
        owner, repo_name, pr_number = self.repo_handler.parse_pr_url(pr_url)
        
        # Clone the repository
        repo_url = f"https://github.com/{owner}/{repo_name}.git"
        repo_path = self.repo_handler.clone_repository(repo_url)
        
        # TODO: Use GitHub API to get PR information
        # For now, we'll assume the PR is a single commit and use the HEAD of the PR branch
        # In a real implementation, we'd use the GitHub API to get the base and head commits
        
        # For demonstration purposes, we'll use the current HEAD commit
        try:
            import git
            repo = git.Repo(repo_path)
            commit_sha = repo.head.commit.hexsha
            
            # Analyze the commit
            return self._analyze_commit(repo_path, commit_sha)
        except Exception as e:
            logger.error(f"Error analyzing PR {pr_url}: {e}")
            return {
                "error": str(e),
                "changed_files": [],
                "bug_patterns": [],
                "context": {},
                "complexity": {"score": 0, "factors": []}
            }
    
    def _analyze_commit(self, repo_path: str, commit_sha: str) -> Dict[str, Any]:
        """
        Analyze a commit to extract bug fix information.
        
        Args:
            repo_path: Path to the repository
            commit_sha: SHA of the commit to analyze
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Checkout the commit
            self.repo_handler.checkout_commit(repo_path, commit_sha)
            
            # Get the diff for this commit
            diff_info = self.repo_handler.get_commit_diff(repo_path, commit_sha)
            
            # Checkout the parent commit to get the buggy state
            parent_sha = self.repo_handler.checkout_parent_commit(repo_path, commit_sha)
            
            # Collect buggy files
            bug_files = {}
            for file_info in diff_info.get("files", []):
                file_path = file_info["path"]
                bug_content = self.repo_handler.get_file_content(repo_path, file_path)
                if bug_content is not None:
                    bug_files[file_path] = bug_content
            
            # Checkout the commit again to get the fixed state
            self.repo_handler.checkout_commit(repo_path, commit_sha)
            
            # Collect fixed files
            fixed_files = {}
            for file_info in diff_info.get("files", []):
                file_path = file_info["path"]
                fixed_content = self.repo_handler.get_file_content(repo_path, file_path)
                if fixed_content is not None:
                    fixed_files[file_path] = fixed_content
            
            # Collect diffs
            diffs = diff_info.get("diffs", {})
            
            # Analyze the bug fix
            analysis_result = self.analyzer.analyze_bug_fix(bug_files, fixed_files, diffs)
            
            return analysis_result
        except Exception as e:
            logger.error(f"Error analyzing commit {commit_sha}: {e}")
            return {
                "error": str(e),
                "changed_files": [],
                "bug_patterns": [],
                "context": {},
                "complexity": {"score": 0, "factors": []}
            }
    
    def _analyze_directories(self, buggy_dir: str, fixed_dir: str) -> Dict[str, Any]:
        """
        Analyze directories to extract bug fix information.
        
        Args:
            buggy_dir: Directory with buggy code
            fixed_dir: Directory with fixed code
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Collect files from both directories
            bug_files = self._collect_files_from_directory(buggy_dir)
            fixed_files = self._collect_files_from_directory(fixed_dir)
            
            # Generate diffs between the files
            diffs = {}
            for file_path in set(bug_files.keys()).union(set(fixed_files.keys())):
                bug_content = bug_files.get(file_path, "")
                fixed_content = fixed_files.get(file_path, "")
                
                if bug_content != fixed_content:
                    import difflib
                    diff_lines = difflib.unified_diff(
                        bug_content.splitlines(),
                        fixed_content.splitlines(),
                        fromfile=f"a/{file_path}",
                        tofile=f"b/{file_path}",
                        lineterm=""
                    )
                    diffs[file_path] = "\n".join(diff_lines)
            
            # Analyze the bug fix
            analysis_result = self.analyzer.analyze_bug_fix(bug_files, fixed_files, diffs)
            
            return analysis_result
        except Exception as e:
            logger.error(f"Error analyzing directories: {e}")
            return {
                "error": str(e),
                "changed_files": [],
                "bug_patterns": [],
                "context": {},
                "complexity": {"score": 0, "factors": []}
            }
    
    def _analyze_patch_file(self, patch_file: str, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a patch file to extract bug fix information.
        
        Args:
            patch_file: Path to the patch file
            repo_path: Optional path to the repository for context
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Read the patch file
            with open(patch_file, 'r') as f:
                patch_content = f.read()
            
            # Create a temporary directory to apply the patch if repo_path is not provided
            if not repo_path:
                repo_path = tempfile.mkdtemp()
            
            # Parse the patch to identify files and changes
            import re
            file_pattern = re.compile(r'^--- a/(.+?)\n\+\+\+ b/(.+?)$', re.MULTILINE)
            file_matches = file_pattern.findall(patch_content)
            
            # Extract file paths
            file_paths = set()
            for old_path, new_path in file_matches:
                # Use the new path as the file path (patch might rename files)
                file_paths.add(new_path)
            
            # Split patch into per-file patches
            file_patches = {}
            current_file = None
            current_patch = []
            
            for line in patch_content.splitlines():
                if line.startswith('--- a/'):
                    # Start of a new file patch
                    if current_file and current_patch:
                        file_patches[current_file] = '\n'.join(current_patch)
                    current_patch = [line]
                    continue
                elif line.startswith('+++ b/'):
                    current_file = line[6:]  # Remove '+++ b/' prefix
                    current_patch.append(line)
                    continue
                elif current_file:
                    current_patch.append(line)
            
            # Add the last file patch
            if current_file and current_patch:
                file_patches[current_file] = '\n'.join(current_patch)
            
            # Create a temporary work directory to apply patches
            with tempfile.TemporaryDirectory() as work_dir:
                # If repo_path is provided, copy files to work directory
                if os.path.exists(repo_path):
                    import shutil
                    for file_path in file_paths:
                        src_path = os.path.join(repo_path, file_path)
                        dst_dir = os.path.join(work_dir, os.path.dirname(file_path))
                        dst_path = os.path.join(work_dir, file_path)
                        
                        if os.path.exists(src_path):
                            os.makedirs(dst_dir, exist_ok=True)
                            shutil.copy2(src_path, dst_path)
                
                # Collect buggy files (before applying patch)
                bug_files = {}
                for file_path in file_paths:
                    full_path = os.path.join(work_dir, file_path)
                    if os.path.exists(full_path):
                        with open(full_path, 'r') as f:
                            bug_files[file_path] = f.read()
                    else:
                        # New file, starts empty
                        bug_files[file_path] = ""
                
                # Apply patches to get fixed files
                import subprocess
                for file_path, patch in file_patches.items():
                    full_path = os.path.join(work_dir, file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Write patch to a temporary file
                    patch_path = os.path.join(work_dir, f"{file_path}.patch")
                    with open(patch_path, 'w') as f:
                        f.write(patch)
                    
                    # Apply the patch
                    subprocess.run(
                        ['patch', full_path, patch_path],
                        check=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                
                # Collect fixed files (after applying patch)
                fixed_files = {}
                for file_path in file_paths:
                    full_path = os.path.join(work_dir, file_path)
                    if os.path.exists(full_path):
                        with open(full_path, 'r') as f:
                            fixed_files[file_path] = f.read()
                    else:
                        # File was deleted
                        fixed_files[file_path] = ""
            
            # Use the file patches as diffs
            diffs = file_patches
            
            # Analyze the bug fix
            analysis_result = self.analyzer.analyze_bug_fix(bug_files, fixed_files, diffs)
            
            return analysis_result
        except Exception as e:
            logger.error(f"Error analyzing patch file {patch_file}: {e}")
            return {
                "error": str(e),
                "changed_files": [],
                "bug_patterns": [],
                "context": {},
                "complexity": {"score": 0, "factors": []}
            }
    
    def _collect_files_from_directory(self, directory: str) -> Dict[str, str]:
        """
        Collect all files from a directory.
        
        Args:
            directory: Path to the directory
            
        Returns:
            Dictionary mapping relative file paths to file content
        """
        files = {}
        
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                # Skip hidden files and directories
                if filename.startswith('.') or '/.git/' in root:
                    continue
                    
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, directory)
                
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    files[rel_path] = content
                except (UnicodeDecodeError, IOError):
                    # Skip binary files or unreadable files
                    pass
        
        return files
    
    def cleanup(self) -> None:
        """
        Clean up temporary resources.
        """
        self.repo_handler.cleanup()
