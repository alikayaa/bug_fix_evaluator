#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import tempfile
from typing import Dict, List, Tuple, Any
import shutil

from src.github_parser import GitHubPRParser
from src.code_analyzer import CodeAnalyzer
from src.test_runner import TestRunner

class BugFixEvaluator:
    def __init__(self, engineer_pr: str, ai_pr: str, weights: Dict[str, float] = None):
        """
        Initialize the PR evaluator with paths to the PRs to compare.
        
        Args:
            engineer_pr: Path or URL to the engineer's PR
            ai_pr: Path or URL to the AI-generated PR
            weights: Optional dict of metric weights
        """
        self.engineer_pr = engineer_pr
        self.ai_pr = ai_pr
        
        # Default weights for evaluation metrics
        self.weights = weights or {
            "correctness": 0.30,
            "readability": 0.15,
            "quality": 0.20,
            "problem_solving": 0.25,
            "similarity": 0.10
        }
        
        # Store the parsed PR data
        self.engineer_pr_data = None
        self.ai_pr_data = None
        
        # Store the evaluation results
        self.scores = {}
        self.final_score = 0.0
        self.report = {}
        
        # Set up components
        self.github_parser = GitHubPRParser()
        self.code_analyzer = CodeAnalyzer()
        
        # Working directories
        self.work_dir = tempfile.mkdtemp()
        self.engineer_repo_dir = None
        self.ai_repo_dir = None
    
    def __del__(self):
        """Clean up temporary directories"""
        if hasattr(self, 'work_dir') and os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
    
    def load_prs(self) -> None:
        """
        Parse and load PR data from GitHub or local files.
        """
        print("Loading PR data...")
        
        # Parse GitHub PRs
        if self.engineer_pr.startswith("https://github.com"):
            self.engineer_pr_data = self.github_parser.parse_pr(self.engineer_pr)
        else:
            # Load from local file
            with open(self.engineer_pr, 'r') as f:
                self.engineer_pr_data = json.load(f)
        
        if self.ai_pr.startswith("https://github.com"):
            self.ai_pr_data = self.github_parser.parse_pr(self.ai_pr)
        else:
            # Load from local file
            with open(self.ai_pr, 'r') as f:
                self.ai_pr_data = json.load(f)
        
        print(f"Loaded engineer PR: {self.engineer_pr}")
        print(f"Loaded AI PR: {self.ai_pr}")
    
    def clone_repositories(self) -> None:
        """
        Clone repositories for both PRs.
        """
        print("Cloning repositories...")
        
        # Extract owner/repo/PR info
        if self.engineer_pr.startswith("https://github.com"):
            engineer_owner, engineer_repo, engineer_pr_number = self.github_parser.parse_pr_url(self.engineer_pr)
            self.engineer_repo_dir = self.github_parser.clone_repository(
                engineer_owner, engineer_repo, os.path.join(self.work_dir, "engineer")
            )
            self.github_parser.checkout_pr(self.engineer_repo_dir, engineer_pr_number)
        
        if self.ai_pr.startswith("https://github.com"):
            ai_owner, ai_repo, ai_pr_number = self.github_parser.parse_pr_url(self.ai_pr)
            self.ai_repo_dir = self.github_parser.clone_repository(
                ai_owner, ai_repo, os.path.join(self.work_dir, "ai")
            )
            self.github_parser.checkout_pr(self.ai_repo_dir, ai_pr_number)
        
        print(f"Cloned repositories to {self.work_dir}")
    
    def extract_diffs(self) -> Dict[str, Any]:
        """
        Extract code diffs from both PRs.
        
        Returns:
            Dictionary with diff information
        """
        print("Extracting diffs...")
        
        engineer_files = {file["filename"]: file for file in self.engineer_pr_data["files"]}
        ai_files = {file["filename"]: file for file in self.ai_pr_data["files"]}
        
        # Find common files
        common_files = set(engineer_files.keys()).intersection(set(ai_files.keys()))
        only_engineer_files = set(engineer_files.keys()) - common_files
        only_ai_files = set(ai_files.keys()) - common_files
        
        # Analyze each file
        file_analyses = {}
        
        for filename in common_files:
            engineer_file = engineer_files[filename]
            ai_file = ai_files[filename]
            
            # Get file contents for analysis
            if "patch" in engineer_file and "patch" in ai_file:
                # If we have patches, analyze them
                file_analyses[filename] = {
                    "engineer_patch": engineer_file["patch"],
                    "ai_patch": ai_file["patch"],
                    "status": "common"
                }
        
        for filename in only_engineer_files:
            file_analyses[filename] = {
                "engineer_patch": engineer_files[filename].get("patch", ""),
                "ai_patch": None,
                "status": "engineer_only"
            }
        
        for filename in only_ai_files:
            file_analyses[filename] = {
                "engineer_patch": None,
                "ai_patch": ai_files[filename].get("patch", ""),
                "status": "ai_only"
            }
        
        return {
            "common_files": list(common_files),
            "only_engineer_files": list(only_engineer_files),
            "only_ai_files": list(only_ai_files),
            "file_analyses": file_analyses
        }
    
    def evaluate_correctness(self) -> float:
        """
        Evaluate code correctness by checking if code compiles and passes tests.
        
        Returns:
            Score between 0.0 and 1.0
        """
        print("Evaluating correctness...")
        
        # Skip if repositories not cloned
        if not self.engineer_repo_dir or not self.ai_repo_dir:
            print("Warning: Repositories not cloned, skipping correctness evaluation")
            return 0.5
        
        # Set up test runners
        engineer_test_runner = TestRunner(self.engineer_repo_dir)
        ai_test_runner = TestRunner(self.ai_repo_dir)
        
        # Run tests on both repositories
        engineer_test_results = engineer_test_runner.run_tests()
        ai_test_results = ai_test_runner.run_tests()
        
        # Compare test results
        comparison = engineer_test_runner.compare_test_results(
            engineer_test_results, ai_test_results
        )
        
        # Extract bug description from PR title/body
        bug_description = self.engineer_pr_data["metadata"]["title"] + " " + self.engineer_pr_data["metadata"]["description"]
        
        # Verify bugfix
        verification = ai_test_runner.verify_bugfix(bug_description)
        
        # Calculate correctness score
        correctness_score = 0.0
        
        # Base score on whether all tests pass
        if ai_test_results.get("success", False):
            correctness_score += 0.6
        
        # Bonus for improvement over engineer's PR
        if comparison["improved"]:
            correctness_score += 0.2
        
        # Penalty for regressions
        if comparison["regression"]:
            correctness_score -= 0.4
        
        # Bonus for handling the specific bug correctly
        if verification["likely_fixed"]:
            correctness_score += 0.2
        
        # Ensure score is between 0 and 1
        correctness_score = max(0.0, min(1.0, correctness_score))
        
        return correctness_score
    
    def evaluate_readability(self) -> float:
        """
        Evaluate code readability using style checks and complexity metrics.
        
        Returns:
            Score between 0.0 and 1.0
        """
        print("Evaluating readability...")
        
        # Get file diffs
        diffs = self.extract_diffs()
        
        # Initialize scores
        style_scores = []
        
        # Analyze common files
        for filename in diffs.get("common_files", []):
            file_info = diffs["file_analyses"][filename]
            
            # Get file contents for analysis
            if self.engineer_repo_dir and self.ai_repo_dir:
                # If we have local repositories, use files directly
                engineer_file_path = os.path.join(self.engineer_repo_dir, filename)
                ai_file_path = os.path.join(self.ai_repo_dir, filename)
                
                if os.path.exists(engineer_file_path) and os.path.exists(ai_file_path):
                    with open(engineer_file_path, 'r') as f:
                        engineer_code = f.read()
                    
                    with open(ai_file_path, 'r') as f:
                        ai_code = f.read()
                    
                    # Run style checks on AI code
                    style_result = self.code_analyzer.check_code_style(ai_code, filename)
                    style_scores.append(style_result.get("style_score", 0.5))
            
        # Calculate average style score
        avg_style_score = sum(style_scores) / len(style_scores) if style_scores else 0.5
        
        return avg_style_score
    
    def evaluate_quality(self) -> float:
        """
        Evaluate code quality and logic.
        
        Returns:
            Score between 0.0 and 1.0
        """
        print("Evaluating quality...")
        
        # Get file diffs
        diffs = self.extract_diffs()
        
        # Initialize scores
        quality_scores = []
        
        # Analyze common files
        for filename in diffs.get("common_files", []):
            file_info = diffs["file_analyses"][filename]
            
            # Get file contents for analysis
            if self.engineer_repo_dir and self.ai_repo_dir:
                # If we have local repositories, use files directly
                engineer_file_path = os.path.join(self.engineer_repo_dir, filename)
                ai_file_path = os.path.join(self.ai_repo_dir, filename)
                
                if os.path.exists(engineer_file_path) and os.path.exists(ai_file_path):
                    with open(engineer_file_path, 'r') as f:
                        engineer_code = f.read()
                    
                    with open(ai_file_path, 'r') as f:
                        ai_code = f.read()
                    
                    # Run full code analysis
                    analysis = self.code_analyzer.analyze_code(engineer_code, ai_code, filename)
                    
                    # Calculate quality score based on analysis
                    file_quality = 0.0
                    
                    # Code compiles
                    if analysis.get("compiles", False):
                        file_quality += 0.4
                    
                    # Complexity not worse than original
                    if analysis.get("complexity_change", 0) <= 0:
                        file_quality += 0.3
                    
                    # Few linting issues
                    linting = analysis.get("lint", {})
                    if linting.get("errors", 0) == 0:
                        file_quality += 0.3
                    elif linting.get("errors", 0) <= 2:
                        file_quality += 0.1
                    
                    quality_scores.append(file_quality)
        
        # Calculate average quality score
        avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5
        
        return avg_quality_score
    
    def evaluate_problem_solving(self) -> float:
        """
        Evaluate how effectively the bug was addressed.
        
        Returns:
            Score between 0.0 and 1.0
        """
        print("Evaluating problem solving...")
        
        # Skip if repositories not cloned
        if not self.engineer_repo_dir or not self.ai_repo_dir:
            print("Warning: Repositories not cloned, skipping problem solving evaluation")
            return 0.5
        
        # Set up test runner
        ai_test_runner = TestRunner(self.ai_repo_dir)
        
        # Extract bug description from PR title/body
        bug_description = self.engineer_pr_data["metadata"]["title"] + " " + self.engineer_pr_data["metadata"]["description"]
        
        # Verify bugfix
        verification = ai_test_runner.verify_bugfix(bug_description)
        
        # Calculate problem solving score
        problem_solving_score = 0.0
        
        # Base score on whether the bug is fixed
        if verification["likely_fixed"]:
            problem_solving_score += 0.7
        
        # Add confidence factor
        problem_solving_score += verification["verification_confidence"] * 0.3
        
        # Ensure score is between 0 and 1
        problem_solving_score = max(0.0, min(1.0, problem_solving_score))
        
        return problem_solving_score
    
    def evaluate_similarity(self) -> float:
        """
        Evaluate similarity between engineer and AI solutions.
        
        Returns:
            Score between 0.0 and 1.0
        """
        print("Evaluating similarity...")
        
        # Get file diffs
        diffs = self.extract_diffs()
        
        # Initialize scores
        similarity_scores = []
        
        # Analyze common files
        for filename in diffs.get("common_files", []):
            file_info = diffs["file_analyses"][filename]
            
            # Get file contents for analysis
            if self.engineer_repo_dir and self.ai_repo_dir:
                # If we have local repositories, use files directly
                engineer_file_path = os.path.join(self.engineer_repo_dir, filename)
                ai_file_path = os.path.join(self.ai_repo_dir, filename)
                
                if os.path.exists(engineer_file_path) and os.path.exists(ai_file_path):
                    with open(engineer_file_path, 'r') as f:
                        engineer_code = f.read()
                    
                    with open(ai_file_path, 'r') as f:
                        ai_code = f.read()
                    
                    # Calculate similarity
                    similarity = self.code_analyzer.calculate_code_similarity(engineer_code, ai_code)
                    similarity_scores.append(similarity)
        
        # Calculate average similarity score
        avg_similarity_score = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.5
        
        return avg_similarity_score
    
    def calculate_scores(self) -> Dict[str, float]:
        """
        Calculate scores for all metrics and compute final score.
        
        Returns:
            Dictionary with individual and composite scores
        """
        print("Calculating scores...")
        
        scores = {
            "correctness": self.evaluate_correctness(),
            "readability": self.evaluate_readability(),
            "quality": self.evaluate_quality(),
            "problem_solving": self.evaluate_problem_solving(),
            "similarity": self.evaluate_similarity()
        }
        
        # Calculate weighted final score
        final_score = sum(scores[metric] * weight for metric, weight in self.weights.items())
        
        self.scores = scores
        self.final_score = final_score
        
        return {
            **scores,
            "final_score": final_score
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a detailed evaluation report.
        
        Returns:
            Dictionary containing the evaluation report
        """
        print("Generating report...")
        
        # Extract PR metadata
        engineer_meta = self.engineer_pr_data.get("metadata", {})
        ai_meta = self.ai_pr_data.get("metadata", {})
        
        # Extract bug information
        bug_description = engineer_meta.get("title", "") + " " + engineer_meta.get("description", "")
        
        # Get file diffs
        diffs = self.extract_diffs()
        
        self.report = {
            "scores": self.scores,
            "final_score": self.final_score,
            "weights": self.weights,
            "details": {
                "engineer_pr": {
                    "url": self.engineer_pr,
                    "title": engineer_meta.get("title", ""),
                    "author": engineer_meta.get("author", ""),
                    "created_at": engineer_meta.get("created_at", ""),
                    "merged_at": engineer_meta.get("merged_at", "")
                },
                "ai_pr": {
                    "url": self.ai_pr,
                    "title": ai_meta.get("title", ""),
                    "author": ai_meta.get("author", ""),
                    "created_at": ai_meta.get("created_at", "")
                },
                "bug_info": {
                    "description": bug_description,
                    "keywords": list(set(bug_description.lower().split()))[:10]
                },
                "file_comparison": {
                    "common_files": diffs.get("common_files", []),
                    "only_engineer_files": diffs.get("only_engineer_files", []),
                    "only_ai_files": diffs.get("only_ai_files", [])
                },
                "metric_breakdown": {
                    "correctness": {
                        "score": self.scores.get("correctness", 0),
                        "weight": self.weights.get("correctness", 0.3),
                        "details": "Tests pass and bug is fixed correctly"
                    },
                    "readability": {
                        "score": self.scores.get("readability", 0),
                        "weight": self.weights.get("readability", 0.15),
                        "details": "Code follows style guidelines and is easy to understand"
                    },
                    "quality": {
                        "score": self.scores.get("quality", 0),
                        "weight": self.weights.get("quality", 0.2),
                        "details": "Code is well-structured, efficient, and adheres to best practices"
                    },
                    "problem_solving": {
                        "score": self.scores.get("problem_solving", 0),
                        "weight": self.weights.get("problem_solving", 0.25),
                        "details": "The approach effectively addresses the core issue"
                    },
                    "similarity": {
                        "score": self.scores.get("similarity", 0),
                        "weight": self.weights.get("similarity", 0.1),
                        "details": "Similarity to the engineer's solution"
                    }
                },
                "improvement_suggestions": []
            }
        }
        
        # Add improvement suggestions based on scores
        if self.scores.get("correctness", 0) < 0.7:
            self.report["details"]["improvement_suggestions"].append(
                "Ensure all tests pass and the bug is fully fixed"
            )
        
        if self.scores.get("readability", 0) < 0.7:
            self.report["details"]["improvement_suggestions"].append(
                "Improve code readability and adhere to style guidelines"
            )
        
        if self.scores.get("quality", 0) < 0.7:
            self.report["details"]["improvement_suggestions"].append(
                "Refactor code to improve structure and efficiency"
            )
        
        if self.scores.get("problem_solving", 0) < 0.7:
            self.report["details"]["improvement_suggestions"].append(
                "Revisit problem-solving approach to better address the root cause"
            )
        
        return self.report
    
    def save_report(self, output_path: str) -> None:
        """
        Save the evaluation report to a file.
        
        Args:
            output_path: Path to save the report
        """
        with open(output_path, 'w') as f:
            json.dump(self.report, f, indent=2)
        
        print(f"Report saved to {output_path}")
    
    def generate_html_report(self, json_report_path: str, html_output_path: str = None) -> str:
        """
        Generate an HTML report from the JSON evaluation.
        
        Args:
            json_report_path: Path to the JSON report
            html_output_path: Path to save the HTML report (defaults to JSON path with .html extension)
            
        Returns:
            Path to the generated HTML file
        """
        if html_output_path is None:
            html_output_path = os.path.splitext(json_report_path)[0] + '.html'
        
        # Get the path to the HTML template
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(script_dir, "web_report.html")
        
        if not os.path.exists(template_path):
            print(f"Warning: HTML template not found at {template_path}")
            print("Please make sure web_report.html is in the project root directory.")
            return None
        
        # Read the JSON report
        try:
            with open(json_report_path, 'r') as f:
                report_data = json.load(f)
        except Exception as e:
            print(f"Error reading JSON report: {e}")
            return None
        
        # Read the HTML template
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(html_output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Update the template with report data
        modified_template = template.replace(
            "// Run on page load - try to load from a parameter or use demo data",
            f"// Report data embedded directly\nconst reportData = {json.dumps(report_data, indent=2)};"
        ).replace(
            "if (reportPath) {\n                loadReportData(reportPath);\n            } else {\n                loadDemoData();\n            }",
            "renderReport(reportData);"
        )
        
        # Write the HTML file
        with open(html_output_path, 'w') as f:
            f.write(modified_template)
        
        print(f"HTML report generated at: {html_output_path}")
        return html_output_path
    
    def run_evaluation(self, output_path: str = None, generate_html: bool = False) -> Dict[str, Any]:
        """
        Run the complete evaluation pipeline.
        
        Args:
            output_path: Optional path to save the report
            generate_html: Whether to generate an HTML report
            
        Returns:
            Evaluation report dictionary
        """
        print("Starting PR evaluation...")
        self.load_prs()
        self.clone_repositories()
        self.extract_diffs()
        self.calculate_scores()
        self.generate_report()
        
        if output_path:
            self.save_report(output_path)
            
            if generate_html:
                html_path = self.generate_html_report(output_path)
                print(f"You can open the HTML report in your browser: file://{os.path.abspath(html_path)}")
        
        return self.report

def main():
    parser = argparse.ArgumentParser(description="Evaluate AI-generated bug-fix PRs against engineer PRs")
    parser.add_argument("--engineer-pr", required=True, help="URL or path to engineer's PR")
    parser.add_argument("--ai-pr", required=True, help="URL or path to AI-generated PR")
    parser.add_argument("--output", default="evaluation_report.json", help="Path to save evaluation report")
    parser.add_argument("--weights", help="JSON string with custom weights for metrics")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    
    args = parser.parse_args()
    
    weights = None
    if args.weights:
        try:
            weights = json.loads(args.weights)
        except json.JSONDecodeError:
            print("Warning: Could not parse weights, using defaults")
    
    evaluator = BugFixEvaluator(args.engineer_pr, args.ai_pr, weights)
    report = evaluator.run_evaluation(args.output, args.html)
    
    print(f"Final score: {report['final_score']:.2f}")
    
    # Print breakdown
    print("\nScore Breakdown:")
    for metric, score in report["scores"].items():
        weight = report["weights"][metric]
        weighted_score = score * weight
        print(f"  {metric}: {score:.2f} (weight: {weight:.2f}, contribution: {weighted_score:.2f})")
    
    # Print improvement suggestions
    if report["details"]["improvement_suggestions"]:
        print("\nImprovement Suggestions:")
        for suggestion in report["details"]["improvement_suggestions"]:
            print(f"  - {suggestion}")

if __name__ == "__main__":
    main() 