"""
Bug Fix Evaluator - A tool for evaluating AI-generated bug fixes against engineer-created fixes.

This package provides tools to compare and evaluate bug fixes, generating metrics
and reports on the quality of the fixes.
"""

__version__ = "0.2.0"

from .core.repository import RepositoryHandler
from .core.analyzer import CodeAnalyzer
from .core.metrics import EvaluationMetrics
from .core.reporter import ReportGenerator

# Import main evaluator class
from .core import BugFixEvaluator

__all__ = [
    "BugFixEvaluator",
    "RepositoryHandler",
    "CodeAnalyzer", 
    "EvaluationMetrics",
    "ReportGenerator",
]
