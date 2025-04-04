"""
Utilities module for Bug Fix Cursor Evaluator.

This module provides utility functions for the Bug Fix Cursor Evaluator.
"""

import os
import json
import time
import logging
import subprocess
from typing import Optional, Union, Dict, List

logger = logging.getLogger(__name__)

class LoggingConfig:
    """Configuration class for logging setup."""
    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DEFAULT_LEVEL = logging.INFO
    EXTERNAL_LOGGERS = {
        "requests": logging.WARNING,
        "urllib3": logging.WARNING,
    }
    PACKAGE_LOGGER = "bug_fix_cursor_evaluator"

def setup_logger(
    level: Union[int, str] = logging.INFO,
    format_str: str = LoggingConfig.DEFAULT_FORMAT,
    log_file: Optional[str] = None,
    external_loggers: Optional[Dict[str, int]] = None
) -> None:
    """
    Configure logging for the Bug Fix Cursor Evaluator.
    
    Args:
        level: Logging level (can be int or string like 'INFO', 'DEBUG')
        format_str: Format string for log messages
        log_file: Optional path to write logs to a file
        external_loggers: Optional dictionary mapping logger names to their levels
    """
    # Convert string level to int if needed
    if isinstance(level, str):
        level = getattr(logging, level.upper(), LoggingConfig.DEFAULT_LEVEL)
    
    # Get root logger and configure it
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter to reuse
    formatter = logging.Formatter(format_str)
    
    # Add console handler
    add_console_handler(root_logger, level, formatter)
    
    # Add file handler if specified
    if log_file:
        add_file_handler(root_logger, log_file, level, formatter)
    
    # Configure external loggers
    configure_external_loggers(level, external_loggers)

def add_console_handler(logger_obj: logging.Logger, level: int, formatter: logging.Formatter) -> None:
    """Add console handler to logger."""
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger_obj.addHandler(console_handler)

def add_file_handler(logger_obj: logging.Logger, log_file: str, level: int, formatter: logging.Formatter) -> None:
    """Add file handler to logger."""
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger_obj.addHandler(file_handler)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to set up file logging: {e}")

def configure_external_loggers(level: int, external_loggers: Optional[Dict[str, int]] = None) -> None:
    """Configure external and package loggers."""
    # Set levels for external libraries
    loggers_to_configure = external_loggers or LoggingConfig.EXTERNAL_LOGGERS
    for logger_name, logger_level in loggers_to_configure.items():
        logging.getLogger(logger_name).setLevel(logger_level)
    
    # Set package logger level
    pkg_logger = logging.getLogger(LoggingConfig.PACKAGE_LOGGER)
    pkg_logger.setLevel(level)

def is_git_repo(path: str) -> bool:
    """
    Check if a directory is a git repository.
    
    Args:
        path: Path to check
        
    Returns:
        True if the directory is a git repository, False otherwise
    """
    return os.path.exists(os.path.join(path, '.git'))

def get_local_pr_diff(pr_number: int, repo_path: Optional[str] = None) -> Optional[str]:
    """
    Get PR diff from local repository.
    
    Args:
        pr_number: PR number
        repo_path: Path to local repository (defaults to current directory)
        
    Returns:
        Diff as a string, or None if failed
    """
    repo_path = repo_path or os.getcwd()
    
    try:
        # Ensure PR is fetched locally
        subprocess.run(['git', 'fetch', 'origin', f'pull/{pr_number}/head:pr-{pr_number}'],
                      check=True, cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Find default branch
        default_branch = None
        for branch in ['main', 'master', 'develop']:
            try:
                subprocess.run(['git', 'rev-parse', '--verify', f'origin/{branch}'],
                              check=True, cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                default_branch = f'origin/{branch}'
                break
            except subprocess.CalledProcessError:
                continue
        
        if not default_branch:
            logger.warning("Could not determine default branch, using HEAD")
            default_branch = 'HEAD'
        
        # Get merge base
        try:
            merge_base = subprocess.run(['git', 'merge-base', default_branch, f'pr-{pr_number}'],
                                      check=True, cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            merge_base = merge_base.stdout.decode('utf-8').strip()
        except subprocess.CalledProcessError:
            logger.warning("Could not find merge-base, using first commit of PR branch")
            first_commit = subprocess.run(['git', 'rev-list', '--max-parents=0', f'pr-{pr_number}'],
                                        check=True, cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            merge_base = first_commit.stdout.decode('utf-8').strip()
        
        # Get diff between merge base and PR
        diff = subprocess.run(['git', 'diff', merge_base, f'pr-{pr_number}'],
                             check=True, cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        logger.info(f"Successfully retrieved PR diff from local repository")
        return diff.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting PR diff from local repo: {e}")
        return None

def wait_for_results(results_file: str, timeout: int = 3600, check_interval: int = 5) -> bool:
    """
    Wait for results file to be created and populated.
    
    Args:
        results_file: Path to the results file to wait for
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        
    Returns:
        True if the results file was found, False otherwise
    """
    start_time = time.time()
    
    logger.info(f"Waiting for evaluation results to be saved to: {results_file}")
    
    while time.time() - start_time < timeout:
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r') as f:
                    data = json.load(f)
                if data and isinstance(data, dict):
                    logger.info(f"Results file detected after {time.time() - start_time:.1f} seconds")
                    return True
            except (json.JSONDecodeError, IOError):
                # File exists but is not valid JSON yet
                pass
                
        # Wait before checking again
        time.sleep(check_interval)
        
    logger.warning(f"Timeout after waiting {timeout} seconds for results")
    return False 