"""
Utilities module for Bug Fix Evaluator.

This module provides utility functions and classes for the Bug Fix Evaluator.
"""

from .config import (
    load_config,
    save_config,
    get_config_value,
    set_config_value,
    create_default_config,
    validate_config,
    get_default_config,
    DEFAULT_CONFIG
)

from .git_utils import (
    run_git_command,
    is_git_repository,
    get_commit_info,
    parse_patch,
    create_patch,
    get_file_at_commit,
    get_commit_diff,
    clone_repository,
    pull_repository,
    checkout_commit
)

__all__ = [
    # Config utilities
    'load_config',
    'save_config',
    'get_config_value',
    'set_config_value',
    'create_default_config',
    'validate_config',
    'get_default_config',
    'DEFAULT_CONFIG',
    
    # Git utilities
    'run_git_command',
    'is_git_repository',
    'get_commit_info',
    'parse_patch',
    'create_patch',
    'get_file_at_commit',
    'get_commit_diff',
    'clone_repository',
    'pull_repository',
    'checkout_commit'
]
