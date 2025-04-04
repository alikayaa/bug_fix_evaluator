"""Tests for the CursorAgentEvaluator class."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from bug_fix_cursor_evaluator import CursorAgentEvaluator


class TestCursorAgentEvaluator(unittest.TestCase):
    """Test cases for the CursorAgentEvaluator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.evaluator = CursorAgentEvaluator(output_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temp files if needed
        pass

    @patch('bug_fix_cursor_evaluator.cursor_agent.parse_github_pr_url')
    @patch('bug_fix_cursor_evaluator.cursor_agent.clone_repository')
    @patch('bug_fix_cursor_evaluator.cursor_agent.get_pr_diff')
    def test_evaluate_pr(self, mock_get_pr_diff, mock_clone_repo, mock_parse_url):
        """Test evaluating a PR."""
        # Setup mocks
        mock_parse_url.return_value = {
            'owner': 'test-owner',
            'repo': 'test-repo',
            'pr_number': '123'
        }
        mock_clone_repo.return_value = '/tmp/repo-path'
        mock_get_pr_diff.return_value = 'Sample diff content'

        # Call the method
        result = self.evaluator.evaluate_pr('https://github.com/test-owner/test-repo/pull/123')

        # Assert results
        self.assertIn('instructions_file', result)
        self.assertIn('results_file', result)
        self.assertTrue(os.path.exists(result['instructions_file']))

        # Verify the instructions file contains expected content
        with open(result['instructions_file'], 'r') as f:
            content = f.read()
            self.assertIn('TASK: Evaluate the following bug fix', content)
            self.assertIn('Sample diff content', content)

    @patch('bug_fix_cursor_evaluator.cursor_agent.os.path.exists')
    @patch('bug_fix_cursor_evaluator.cursor_agent.json.load')
    def test_load_results(self, mock_json_load, mock_exists):
        """Test loading evaluation results."""
        # Setup mocks
        mock_exists.return_value = True
        mock_json_load.return_value = {
            'overall': 85,
            'correctness': 9,
            'completeness': 8
        }

        # Call the method with a mock file path
        results = self.evaluator.load_results('/path/to/results.json')

        # Assert results
        self.assertEqual(results['overall'], 85)
        self.assertEqual(results['correctness'], 9)
        self.assertEqual(results['completeness'], 8)

    @patch('bug_fix_cursor_evaluator.cursor_agent.subprocess.run')
    def test_open_in_cursor(self, mock_run):
        """Test opening a file in Cursor."""
        # Call the method
        self.evaluator.open_in_cursor('/path/to/file.txt')

        # Assert subprocess.run was called with correct args
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], 'cursor')
        self.assertEqual(args[1], '/path/to/file.txt')


if __name__ == '__main__':
    unittest.main() 