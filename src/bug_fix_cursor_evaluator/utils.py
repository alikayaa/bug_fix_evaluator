"""
Utilities module for Bug Fix Cursor Evaluator.

This module provides utility functions and classes for the Bug Fix Cursor Evaluator.
"""

import os
import json
import time
import logging
import subprocess
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Union, Dict, List, Callable, Any, TypeVar, cast, Protocol

# Type variables for better type hinting
T = TypeVar('T')
PathLike = Union[str, Path]

# Module logger
logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Enum for logging levels."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class LoggingConfig:
    """Configuration class for logging setup."""
    format_str: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    level: Union[LogLevel, int] = LogLevel.INFO
    external_loggers: Dict[str, Union[LogLevel, int]] = field(default_factory=lambda: {
        "requests": LogLevel.WARNING,
        "urllib3": LogLevel.WARNING,
    })
    package_logger: str = "bug_fix_cursor_evaluator"
    log_file: Optional[PathLike] = None

    def get_level_value(self) -> int:
        """Convert level to its integer value."""
        if isinstance(self.level, LogLevel):
            return self.level.value
        return cast(int, self.level)

    def get_external_logger_levels(self) -> Dict[str, int]:
        """Convert external logger levels to their integer values."""
        result = {}
        for name, level in self.external_loggers.items():
            if isinstance(level, LogLevel):
                result[name] = level.value
            else:
                result[name] = level
        return result


class LoggerManager:
    """Class to manage logging setup and operations."""
    
    @staticmethod
    def setup_logger(config: LoggingConfig = LoggingConfig()) -> None:
        """
        Configure logging for the Bug Fix Cursor Evaluator.
        
        Args:
            config: Logging configuration object
        """
        level = config.get_level_value()
        
        # Get root logger and configure it
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create formatter to reuse
        formatter = logging.Formatter(config.format_str)
        
        # Add console handler
        LoggerManager._add_console_handler(root_logger, level, formatter)
        
        # Add file handler if specified
        if config.log_file:
            LoggerManager._add_file_handler(root_logger, config.log_file, level, formatter)
        
        # Configure external loggers
        LoggerManager._configure_external_loggers(level, config)

    @staticmethod
    def _add_console_handler(
        logger_obj: logging.Logger, 
        level: int, 
        formatter: logging.Formatter
    ) -> None:
        """Add console handler to logger."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger_obj.addHandler(console_handler)

    @staticmethod
    def _add_file_handler(
        logger_obj: logging.Logger, 
        log_file: PathLike, 
        level: int, 
        formatter: logging.Formatter
    ) -> None:
        """Add file handler to logger."""
        try:
            # Ensure directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(str(log_path))
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger_obj.addHandler(file_handler)
            logger.debug(f"File logging configured: {log_file}")
        except Exception as e:
            logger.error(f"Failed to set up file logging: {e}")

    @staticmethod
    def _configure_external_loggers(level: int, config: LoggingConfig) -> None:
        """Configure external and package loggers."""
        # Set levels for external libraries
        external_logger_levels = config.get_external_logger_levels()
        for logger_name, logger_level in external_logger_levels.items():
            logging.getLogger(logger_name).setLevel(logger_level)
        
        # Set package logger level
        pkg_logger = logging.getLogger(config.package_logger)
        pkg_logger.setLevel(level)
        logger.debug(f"Package logger {config.package_logger} configured with level {level}")


class CommandResult:
    """Class to store and handle the result of shell commands."""
    
    def __init__(self, returncode: int, stdout: str, stderr: str):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        
    @property
    def success(self) -> bool:
        """Whether the command was successful."""
        return self.returncode == 0
        
    def __str__(self) -> str:
        status = "Success" if self.success else f"Failed (code {self.returncode})"
        return f"{status}\nStdout: {self.stdout}\nStderr: {self.stderr}"


class GitUtils:
    """Utility class for Git operations."""
    
    @staticmethod
    def is_git_repo(path: PathLike) -> bool:
        """
        Check if a directory is a git repository.
        
        Args:
            path: Path to check
            
        Returns:
            True if the directory is a git repository, False otherwise
        """
        return Path(path).joinpath('.git').exists()
    
    @staticmethod
    def run_git_command(
        args: List[str], 
        cwd: Optional[PathLike] = None, 
        check: bool = True
    ) -> CommandResult:
        """
        Run a git command and return the result.
        
        Args:
            args: Command arguments (without 'git')
            cwd: Working directory
            check: Whether to raise an exception on failure
            
        Returns:
            CommandResult object with returncode, stdout, and stderr
            
        Raises:
            subprocess.CalledProcessError: If check is True and command fails
        """
        cwd = str(cwd) if cwd else os.getcwd()
        cmd = ['git'] + args
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=check,
                text=True
            )
            return CommandResult(
                result.returncode,
                result.stdout.strip(),
                result.stderr.strip()
            )
        except subprocess.CalledProcessError as e:
            error_result = CommandResult(
                e.returncode,
                e.stdout.strip() if e.stdout else "",
                e.stderr.strip() if e.stderr else ""
            )
            if check:
                logger.error(f"Git command failed: {' '.join(cmd)}\n{error_result}")
                raise
            return error_result

    @staticmethod
    def get_local_pr_diff(pr_number: int, repo_path: Optional[PathLike] = None) -> Optional[str]:
        """
        Get PR diff from local repository.
        
        Args:
            pr_number: PR number
            repo_path: Path to local repository (defaults to current directory)
            
        Returns:
            Diff as a string, or None if failed
        """
        repo_path = repo_path or os.getcwd()
        
        if not GitUtils.is_git_repo(repo_path):
            logger.error(f"Not a git repository: {repo_path}")
            return None
        
        try:
            # Ensure PR is fetched locally
            fetch_result = GitUtils.run_git_command(
                ['fetch', 'origin', f'pull/{pr_number}/head:pr-{pr_number}'],
                cwd=repo_path
            )
            
            # Find default branch
            default_branch = GitUtils._find_default_branch(repo_path)
            
            # Get merge base
            merge_base = GitUtils._get_merge_base(default_branch, f'pr-{pr_number}', repo_path)
            
            # Get diff between merge base and PR
            diff_result = GitUtils.run_git_command(
                ['diff', merge_base, f'pr-{pr_number}'],
                cwd=repo_path
            )
            
            logger.info(f"Successfully retrieved PR diff from local repository")
            return diff_result.stdout
        except Exception as e:
            logger.error(f"Error getting PR diff from local repo: {e}")
            return None
    
    @staticmethod
    def _find_default_branch(repo_path: PathLike) -> str:
        """Find the default branch for the repository."""
        for branch in ['main', 'master', 'develop']:
            result = GitUtils.run_git_command(
                ['rev-parse', '--verify', f'origin/{branch}'],
                cwd=repo_path,
                check=False
            )
            if result.success:
                logger.debug(f"Found default branch: origin/{branch}")
                return f'origin/{branch}'
        
        logger.warning("Could not determine default branch, using HEAD")
        return 'HEAD'
    
    @staticmethod
    def _get_merge_base(base: str, branch: str, repo_path: PathLike) -> str:
        """Get the merge base between two branches."""
        try:
            merge_base_result = GitUtils.run_git_command(
                ['merge-base', base, branch],
                cwd=repo_path
            )
            return merge_base_result.stdout
        except subprocess.CalledProcessError:
            logger.warning(f"Could not find merge-base, using first commit of {branch}")
            first_commit_result = GitUtils.run_git_command(
                ['rev-list', '--max-parents=0', branch],
                cwd=repo_path
            )
            return first_commit_result.stdout


class FileWatcher:
    """Utility class for watching files and waiting for changes."""
    
    @staticmethod
    def wait_for_results(
        results_file: PathLike, 
        timeout: int = 3600, 
        check_interval: int = 5,
        validator: Callable[[Any], bool] = lambda data: data and isinstance(data, dict)
    ) -> bool:
        """
        Wait for results file to be created and populated.
        
        Args:
            results_file: Path to the results file to wait for
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            validator: Function to validate the loaded data
            
        Returns:
            True if the results file was found and validated, False otherwise
        """
        start_time = time.time()
        path = Path(results_file)
        
        logger.info(f"Waiting for evaluation results to be saved to: {path}")
        
        while time.time() - start_time < timeout:
            if path.exists():
                try:
                    data = FileWatcher._load_json_file(path)
                    if validator(data):
                        elapsed = time.time() - start_time
                        logger.info(f"Results file detected after {elapsed:.1f} seconds")
                        return True
                except (json.JSONDecodeError, IOError) as e:
                    logger.debug(f"File exists but not ready: {e}")
                    
            # Wait before checking again
            time.sleep(check_interval)
            
        logger.warning(f"Timeout after waiting {timeout} seconds for results")
        return False
    
    @staticmethod
    def _load_json_file(file_path: Path) -> Any:
        """Load and parse a JSON file."""
        with open(file_path, 'r') as f:
            return json.load(f)


# Alias for backward compatibility
def setup_logger(
    level: Union[int, str] = logging.INFO,
    format_str: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: Optional[PathLike] = None,
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
        level_value = getattr(logging, level.upper(), LoggingConfig().get_level_value())
        config = LoggingConfig(level=level_value, format_str=format_str, log_file=log_file)
    else:
        config = LoggingConfig(level=level, format_str=format_str, log_file=log_file)
    
    if external_loggers:
        config.external_loggers = external_loggers
        
    return LoggerManager.setup_logger(config)

is_git_repo = GitUtils.is_git_repo
get_local_pr_diff = GitUtils.get_local_pr_diff
wait_for_results = FileWatcher.wait_for_results 