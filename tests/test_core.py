"""
Tests for the core functionality of the bug fix evaluator.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.bug_fix_evaluator.core.repository import RepositoryHandler
from src.bug_fix_evaluator.core.analyzer import CodeAnalyzer
from src.bug_fix_evaluator.core.metrics import EvaluationMetrics
from src.bug_fix_evaluator.core.reporter import ReportGenerator
from src.bug_fix_evaluator.core import BugFixEvaluator
from src.bug_fix_evaluator.utils.config import load_config, get_default_config


class TestRepositoryHandler(unittest.TestCase):
    """Test cases for the RepositoryHandler class."""
    
    @patch('src.bug_fix_evaluator.core.repository.git')
    def test_init(self, mock_git):
        """Test initialization of RepositoryHandler."""
        repo_handler = RepositoryHandler(repo_path="test_repo")
        self.assertEqual(repo_handler.repo_path, "test_repo")
    
    @patch('src.bug_fix_evaluator.core.repository.git')
    def test_get_commit_diff(self, mock_git):
        """Test getting commit diff."""
        # Setup mock
        mock_repo = MagicMock()
        mock_git.Repo.return_value = mock_repo
        
        # Test
        repo_handler = RepositoryHandler(repo_path="test_repo")
        repo_handler.get_commit_diff("commit1", "commit2")
        
        # Verify
        mock_repo.git.diff.assert_called_once()


class TestCodeAnalyzer(unittest.TestCase):
    """Test cases for the CodeAnalyzer class."""
    
    def test_init(self):
        """Test initialization of CodeAnalyzer."""
        analyzer = CodeAnalyzer()
        self.assertIsNotNone(analyzer)
    
    def test_analyze_diff(self):
        """Test analyzing diff."""
        analyzer = CodeAnalyzer()
        mock_diff = "diff --git a/file.py b/file.py\nindex abc..def 100644\n--- a/file.py\n+++ b/file.py\n@@ -1,3 +1,4 @@\n def func():\n-    return 1\n+    # Fixed bug\n+    return 2"
        result = analyzer.analyze_diff(mock_diff)
        self.assertIsNotNone(result)


class TestEvaluationMetrics(unittest.TestCase):
    """Test cases for the EvaluationMetrics class."""
    
    def test_init(self):
        """Test initialization of EvaluationMetrics."""
        config = get_default_config()
        metrics = EvaluationMetrics(config=config)
        self.assertIsNotNone(metrics)
    
    def test_evaluate(self):
        """Test evaluating bug fixes."""
        config = get_default_config()
        metrics = EvaluationMetrics(config=config)
        
        engineer_analysis = {
            'files_changed': 1,
            'lines_added': 2,
            'lines_removed': 1,
            'complexity_before': {'score': 5},
            'complexity_after': {'score': 4}
        }
        
        ai_analysis = {
            'files_changed': 1,
            'lines_added': 2,
            'lines_removed': 1,
            'complexity_before': {'score': 5},
            'complexity_after': {'score': 4}
        }
        
        result = metrics.evaluate(engineer_analysis, ai_analysis)
        self.assertIsNotNone(result)
        self.assertIn('scores', result)


class TestReportGenerator(unittest.TestCase):
    """Test cases for the ReportGenerator class."""
    
    def test_init(self):
        """Test initialization of ReportGenerator."""
        generator = ReportGenerator()
        self.assertIsNotNone(generator)
    
    @patch('src.bug_fix_evaluator.core.reporter.os')
    def test_generate_report(self, mock_os):
        """Test generating a report."""
        # Setup mock
        mock_os.path.exists.return_value = True
        mock_os.makedirs = MagicMock()
        
        # Test
        generator = ReportGenerator()
        evaluation_result = {
            'overall_score': 85,
            'scores': {
                'correctness': 90,
                'completeness': 80,
                'cleanliness': 85,
                'efficiency': 80,
                'complexity': 90
            },
            'engineer_analysis': {},
            'ai_analysis': {}
        }
        
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            report_path = generator.generate_report(evaluation_result, format='text')
            self.assertIsNotNone(report_path)


class TestBugFixEvaluator(unittest.TestCase):
    """Test cases for the BugFixEvaluator class."""
    
    def test_init(self):
        """Test initialization of BugFixEvaluator."""
        config = get_default_config()
        evaluator = BugFixEvaluator(config=config)
        self.assertIsNotNone(evaluator)
    
    @patch('src.bug_fix_evaluator.core.repository.RepositoryHandler')
    @patch('src.bug_fix_evaluator.core.analyzer.CodeAnalyzer')
    @patch('src.bug_fix_evaluator.core.metrics.EvaluationMetrics')
    @patch('src.bug_fix_evaluator.core.reporter.ReportGenerator')
    def test_evaluate_from_commits(self, mock_reporter, mock_metrics, mock_analyzer, mock_repo):
        """Test evaluating from commits."""
        # Setup mocks
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        mock_repo_instance.get_commit_diff.return_value = "mock diff"
        
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_diff.return_value = {}
        
        mock_metrics_instance = MagicMock()
        mock_metrics.return_value = mock_metrics_instance
        mock_metrics_instance.evaluate.return_value = {
            'overall_score': 85,
            'scores': {}
        }
        
        mock_reporter_instance = MagicMock()
        mock_reporter.return_value = mock_reporter_instance
        mock_reporter_instance.generate_report.return_value = "report.txt"
        
        # Test
        config = get_default_config()
        evaluator = BugFixEvaluator(config=config)
        result = evaluator.evaluate_from_commits(
            repo_path="test_repo",
            engineer_before_commit="commit1",
            engineer_after_commit="commit2",
            ai_before_commit="commit3",
            ai_after_commit="commit4"
        )
        
        # Verify
        self.assertIsNotNone(result)
        self.assertIn('overall_score', result)
        self.assertEqual(result['overall_score'], 85)


if __name__ == '__main__':
    unittest.main() 