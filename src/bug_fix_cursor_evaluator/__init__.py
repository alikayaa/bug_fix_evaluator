"""
Bug Fix Cursor Evaluator - A tool for evaluating bug fixes using Cursor agent mode.

This package provides tools to prepare GitHub PRs for evaluation with Cursor agent mode
and process the results to generate comprehensive reports.
"""

__version__ = "0.1.0"

from .cursor_agent import CursorAgentEvaluator
from .repository import RepositoryHandler
from .reporter import ReportGenerator
from .results import load_cursor_results, process_results
from .utils import setup_logger

__all__ = [
    "CursorAgentEvaluator",
    "RepositoryHandler",
    "ReportGenerator",
    "load_cursor_results",
    "process_results",
    "setup_logger",
] 