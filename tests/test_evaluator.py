#!/usr/bin/env python3
import unittest
import json
import os
import tempfile
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluator import BugFixEvaluator
from src.github_parser import GitHubPRParser
from src.code_analyzer import CodeAnalyzer
from src.test_runner import TestRunner

class MockGitHubPRParser:
    """Mock GitHub PR parser for testing."""
    
    def parse_pr(self, pr_url):
        """Return mock PR data."""
        if "engineer" in pr_url:
            return {
                "metadata": {
                    "number": 123,
                    "title": "Fix null pointer exception in login method",
                    "description": "When user is null, the login method throws NullPointerException",
                    "state": "merged",
                    "created_at": "2023-05-15T10:30:45Z",
                    "merged_at": "2023-05-16T14:20:10Z",
                    "author": "engineer",
                    "labels": ["bug", "critical"],
                    "milestone": "v1.2.0",
                    "draft": False
                },
                "files": [
                    {
                        "filename": "src/main/java/com/example/UserService.java",
                        "status": "modified",
                        "additions": 5,
                        "deletions": 2,
                        "changes": 7,
                        "patch": "@@ -45,7 +45,10 @@ public class UserService {\n     * @param user The user to authenticate\n     * @return true if authentication successful, false otherwise\n     */\n-    public boolean login(User user) {\n+    public boolean login(User user) {\n+        if (user == null) {\n+            return false;\n+        }\n         return userRepository.authenticate(user.getUsername(), user.getPassword());\n     }\n }"
                    }
                ],
                "commits": [
                    {
                        "sha": "abc123",
                        "message": "Fix null pointer exception in login method",
                        "author": "Engineer",
                        "email": "engineer@example.com",
                        "date": "2023-05-15T10:30:45Z"
                    }
                ],
                "comments": [],
                "source": pr_url
            }
        else:
            return {
                "metadata": {
                    "number": 456,
                    "title": "Fix login method null pointer exception",
                    "description": "This PR fixes the null pointer exception in the login method by adding a null check",
                    "state": "open",
                    "created_at": "2023-05-15T09:45:30Z",
                    "merged_at": None,
                    "author": "ai-assistant",
                    "labels": ["bug", "ai-generated"],
                    "milestone": "v1.2.0",
                    "draft": False
                },
                "files": [
                    {
                        "filename": "src/main/java/com/example/UserService.java",
                        "status": "modified",
                        "additions": 3,
                        "deletions": 1,
                        "changes": 4,
                        "patch": "@@ -45,7 +45,9 @@ public class UserService {\n     * @param user The user to authenticate\n     * @return true if authentication successful, false otherwise\n     */\n-    public boolean login(User user) {\n+    public boolean login(User user) {\n+        if (user == null) {\n+            throw new IllegalArgumentException(\"User cannot be null\");\n         return userRepository.authenticate(user.getUsername(), user.getPassword());\n     }\n }"
                    }
                ],
                "commits": [
                    {
                        "sha": "def456",
                        "message": "Fix login method null pointer exception",
                        "author": "AI Assistant",
                        "email": "ai@example.com",
                        "date": "2023-05-15T09:45:30Z"
                    }
                ],
                "comments": [],
                "source": pr_url
            }
    
    def parse_pr_url(self, pr_url):
        """Parse mock PR URL."""
        return ("owner", "repo", "123" if "engineer" in pr_url else "456")
    
    def clone_repository(self, owner, repo, target_dir):
        """Mock repository cloning."""
        repo_dir = os.path.join(target_dir, repo)
        os.makedirs(repo_dir, exist_ok=True)
        return repo_dir
    
    def checkout_pr(self, repo_dir, pr_number):
        """Mock PR checkout."""
        # Create a mock file for testing
        file_path = os.path.join(repo_dir, "src/main/java/com/example/UserService.java")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w") as f:
            if pr_number == "123":
                # Engineer solution
                f.write("""
package com.example;

public class UserService {
    private UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    /**
     * Authenticate a user
     * @param user The user to authenticate
     * @return true if authentication successful, false otherwise
     */
    public boolean login(User user) {
        if (user == null) {
            return false;
        }
        return userRepository.authenticate(user.getUsername(), user.getPassword());
    }
}
""")
            else:
                # AI solution
                f.write("""
package com.example;

public class UserService {
    private UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    /**
     * Authenticate a user
     * @param user The user to authenticate
     * @return true if authentication successful, false otherwise
     */
    public boolean login(User user) {
        if (user == null) {
            throw new IllegalArgumentException("User cannot be null");
        }
        return userRepository.authenticate(user.getUsername(), user.getPassword());
    }
}
""")


class MockCodeAnalyzer:
    """Mock code analyzer for testing."""
    
    def check_code_style(self, code, file_path, language=None):
        """Return mock style check results."""
        return {"style_score": 0.85, "issues": []}
    
    def analyze_code(self, old_code, new_code, file_path):
        """Return mock code analysis results."""
        return {
            "language": "java",
            "compiles": True,
            "complexity": {"average": 1.2, "functions": {}},
            "old_complexity": {"average": 1.0, "functions": {}},
            "complexity_change": 0.2,
            "lint": {"errors": 0, "warnings": 1, "issues": []},
            "style": {"style_score": 0.85, "issues": []},
            "diff": {"added_lines": 3, "removed_lines": 1, "diff_size": 4, "diff_ratio": 0.1},
            "similarity": 0.7
        }
    
    def calculate_code_similarity(self, code1, code2):
        """Return mock similarity score."""
        return 0.7


class MockTestRunner:
    """Mock test runner for testing."""
    
    def __init__(self, repo_path, test_command=None, test_dir=None):
        """Initialize with repo path."""
        self.repo_path = repo_path
    
    def run_tests(self, specific_tests=None):
        """Return mock test results."""
        if "engineer" in self.repo_path:
            return {
                "framework": "junit",
                "success": True,
                "total": 10,
                "passed": 9,
                "failed": 1,
                "errors": 0,
                "skipped": 0,
                "pass_rate": 0.9,
                "execution_time": 1.5,
                "test_cases": [
                    {"name": "testLoginWithNullUser", "status": "failed"}
                ],
                "coverage": {"overall": 80.0}
            }
        else:
            return {
                "framework": "junit",
                "success": True,
                "total": 10,
                "passed": 10,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "pass_rate": 1.0,
                "execution_time": 1.4,
                "test_cases": [],
                "coverage": {"overall": 82.0}
            }
    
    def verify_bugfix(self, bug_description):
        """Return mock bug verification results."""
        return {
            "all_tests_pass": True,
            "matching_failed_tests": [],
            "test_results": {},
            "likely_fixed": True,
            "verification_confidence": 0.8
        }
    
    def compare_test_results(self, before_results, after_results):
        """Return mock test comparison results."""
        return {
            "pass_rate_change": 0.1,
            "fixed_tests": ["testLoginWithNullUser"],
            "new_failures": [],
            "coverage_change": 2.0,
            "improved": True,
            "regression": False,
            "overall_improvement": True
        }


class TestBugFixEvaluator(unittest.TestCase):
    """Test the BugFixEvaluator class."""
    
    def setUp(self):
        """Set up the test case."""
        # Create mock PR data files
        self.engineer_pr_file = tempfile.NamedTemporaryFile(delete=False)
        self.ai_pr_file = tempfile.NamedTemporaryFile(delete=False)
        
        # Write mock PR data to files
        with open(self.engineer_pr_file.name, "w") as f:
            json.dump(MockGitHubPRParser().parse_pr("engineer_pr"), f)
        
        with open(self.ai_pr_file.name, "w") as f:
            json.dump(MockGitHubPRParser().parse_pr("ai_pr"), f)
        
        # Patch the evaluator's dependencies with mocks
        self.original_github_parser = BugFixEvaluator.github_parser
        self.original_code_analyzer = BugFixEvaluator.code_analyzer
        self.original_test_runner = TestRunner
        
        BugFixEvaluator.github_parser = MockGitHubPRParser()
        BugFixEvaluator.code_analyzer = MockCodeAnalyzer()
        sys.modules["src.test_runner"].TestRunner = MockTestRunner
    
    def tearDown(self):
        """Clean up after the test case."""
        # Remove temporary files
        os.unlink(self.engineer_pr_file.name)
        os.unlink(self.ai_pr_file.name)
        
        # Restore original implementations
        BugFixEvaluator.github_parser = self.original_github_parser
        BugFixEvaluator.code_analyzer = self.original_code_analyzer
        sys.modules["src.test_runner"].TestRunner = self.original_test_runner
    
    def test_evaluator_with_file_paths(self):
        """Test evaluator with local file paths."""
        evaluator = BugFixEvaluator(self.engineer_pr_file.name, self.ai_pr_file.name)
        report = evaluator.run_evaluation()
        
        # Check that scores are calculated
        self.assertIn("scores", report)
        self.assertIn("final_score", report)
        
        # Check that all metrics have scores
        for metric in ["correctness", "readability", "quality", "problem_solving", "similarity"]:
            self.assertIn(metric, report["scores"])
            self.assertTrue(0 <= report["scores"][metric] <= 1)
        
        # Check final score
        self.assertTrue(0 <= report["final_score"] <= 1)
    
    def test_evaluator_with_github_urls(self):
        """Test evaluator with GitHub URLs."""
        evaluator = BugFixEvaluator(
            "https://github.com/owner/repo/pull/123",
            "https://github.com/owner/repo/pull/456"
        )
        report = evaluator.run_evaluation()
        
        # Check that scores are calculated
        self.assertIn("scores", report)
        self.assertIn("final_score", report)
        
        # Check that all metrics have scores
        for metric in ["correctness", "readability", "quality", "problem_solving", "similarity"]:
            self.assertIn(metric, report["scores"])
            self.assertTrue(0 <= report["scores"][metric] <= 1)
        
        # Check final score
        self.assertTrue(0 <= report["final_score"] <= 1)
    
    def test_custom_weights(self):
        """Test evaluator with custom weights."""
        custom_weights = {
            "correctness": 0.5,
            "readability": 0.1,
            "quality": 0.1,
            "problem_solving": 0.2,
            "similarity": 0.1
        }
        
        evaluator = BugFixEvaluator(
            self.engineer_pr_file.name,
            self.ai_pr_file.name,
            weights=custom_weights
        )
        report = evaluator.run_evaluation()
        
        # Check that custom weights are used
        self.assertEqual(report["weights"], custom_weights)
        
        # Check that final score is calculated using custom weights
        expected_score = sum(
            report["scores"][metric] * weight
            for metric, weight in custom_weights.items()
        )
        self.assertAlmostEqual(report["final_score"], expected_score, places=6)


if __name__ == "__main__":
    unittest.main() 