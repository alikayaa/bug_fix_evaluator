#!/usr/bin/env python3
import os
import re
import subprocess
import tempfile
import shutil
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Tuple
import json
import time

class TestRunner:
    def __init__(self, repo_path: str, test_command: str = None, test_dir: str = None):
        """
        Initialize the test runner.
        
        Args:
            repo_path: Path to the repository
            test_command: Optional custom test command
            test_dir: Optional custom test directory
        """
        self.repo_path = repo_path
        self.test_command = test_command
        self.test_dir = test_dir
        self.test_results = {}
    
    def detect_test_framework(self) -> str:
        """
        Detect the test framework used in the repository.
        
        Returns:
            Name of the test framework
        """
        # Check for common test frameworks
        if os.path.exists(os.path.join(self.repo_path, "pytest.ini")):
            return "pytest"
        elif os.path.exists(os.path.join(self.repo_path, "package.json")):
            # Check package.json for Jest or Mocha
            with open(os.path.join(self.repo_path, "package.json"), "r") as f:
                package_data = json.load(f)
                
                dependencies = {
                    **package_data.get("dependencies", {}),
                    **package_data.get("devDependencies", {})
                }
                
                if "jest" in dependencies:
                    return "jest"
                elif "mocha" in dependencies:
                    return "mocha"
        
        # Look for test files with common patterns
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    return "pytest"
                elif file.endswith(".test.js") or file.endswith(".spec.js"):
                    return "jest"
        
        return "unknown"
    
    def run_tests(self, specific_tests: List[str] = None) -> Dict[str, Any]:
        """
        Run tests and collect results.
        
        Args:
            specific_tests: Optional list of specific tests to run
            
        Returns:
            Dictionary with test results
        """
        framework = self.detect_test_framework()
        
        if framework == "pytest":
            return self._run_pytest(specific_tests)
        elif framework == "jest":
            return self._run_jest(specific_tests)
        else:
            # Fallback to custom test command
            return self._run_custom_tests()
    
    def _run_pytest(self, specific_tests: List[str] = None) -> Dict[str, Any]:
        """
        Run pytest tests.
        
        Args:
            specific_tests: Optional list of specific tests to run
            
        Returns:
            Dictionary with pytest results
        """
        # Prepare command
        command = ["pytest", "-v"]
        
        # Add JUnit XML output
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as temp_file:
            xml_path = temp_file.name
        
        command.extend(["--junitxml", xml_path])
        
        # Add coverage
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as temp_file:
            coverage_path = temp_file.name
        
        command.extend(["--cov", "--cov-report", f"xml:{coverage_path}"])
        
        # Add specific tests if provided
        if specific_tests:
            command.extend(specific_tests)
        elif self.test_dir:
            command.append(self.test_dir)
        
        # Run tests
        start_time = time.time()
        process = subprocess.run(
            command,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        elapsed_time = time.time() - start_time
        
        # Parse JUnit XML
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Extract test counts
            total = int(root.attrib.get("tests", 0))
            failures = int(root.attrib.get("failures", 0))
            errors = int(root.attrib.get("errors", 0))
            skipped = int(root.attrib.get("skipped", 0))
            passed = total - failures - errors - skipped
            
            # Extract test cases
            test_cases = []
            for test_case in root.findall(".//testcase"):
                test_result = {
                    "name": test_case.attrib.get("name"),
                    "classname": test_case.attrib.get("classname"),
                    "time": float(test_case.attrib.get("time", 0)),
                    "status": "passed"
                }
                
                failure = test_case.find("failure")
                error = test_case.find("error")
                skipped_tag = test_case.find("skipped")
                
                if failure is not None:
                    test_result["status"] = "failed"
                    test_result["message"] = failure.attrib.get("message")
                    test_result["type"] = failure.attrib.get("type")
                    test_result["traceback"] = failure.text
                elif error is not None:
                    test_result["status"] = "error"
                    test_result["message"] = error.attrib.get("message")
                    test_result["type"] = error.attrib.get("type")
                    test_result["traceback"] = error.text
                elif skipped_tag is not None:
                    test_result["status"] = "skipped"
                    test_result["message"] = skipped_tag.attrib.get("message")
                
                test_cases.append(test_result)
            
            # Parse coverage
            coverage_data = {}
            try:
                coverage_tree = ET.parse(coverage_path)
                coverage_root = coverage_tree.getroot()
                
                # Overall coverage
                coverage_data["overall"] = float(coverage_root.attrib.get("line-rate", 0)) * 100
                
                # Per-file coverage
                coverage_data["files"] = {}
                for class_elem in coverage_root.findall(".//class"):
                    filename = class_elem.attrib.get("filename")
                    line_rate = float(class_elem.attrib.get("line-rate", 0)) * 100
                    coverage_data["files"][filename] = line_rate
            except Exception as e:
                print(f"Error parsing coverage: {e}")
            
            # Cleanup
            os.unlink(xml_path)
            os.unlink(coverage_path)
            
            self.test_results = {
                "framework": "pytest",
                "success": process.returncode == 0,
                "total": total,
                "passed": passed,
                "failed": failures,
                "errors": errors,
                "skipped": skipped,
                "pass_rate": (passed / total) if total > 0 else 0,
                "execution_time": elapsed_time,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "test_cases": test_cases,
                "coverage": coverage_data
            }
            
            return self.test_results
        except Exception as e:
            print(f"Error parsing test results: {e}")
            
            # Fallback to basic results
            return {
                "framework": "pytest",
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "execution_time": elapsed_time
            }
    
    def _run_jest(self, specific_tests: List[str] = None) -> Dict[str, Any]:
        """
        Run Jest tests.
        
        Args:
            specific_tests: Optional list of specific tests to run
            
        Returns:
            Dictionary with Jest results
        """
        # Prepare command
        command = ["npx", "jest", "--json", "--coverage"]
        
        # Add specific tests if provided
        if specific_tests:
            command.extend(specific_tests)
        elif self.test_dir:
            command.append(self.test_dir)
        
        # Run tests
        start_time = time.time()
        process = subprocess.run(
            command,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        elapsed_time = time.time() - start_time
        
        # Parse JSON output
        try:
            result_json = json.loads(process.stdout)
            
            # Extract test counts
            test_results = result_json.get("testResults", [])
            
            # Calculate aggregates
            total = result_json.get("numTotalTests", 0)
            passed = result_json.get("numPassedTests", 0)
            failed = result_json.get("numFailedTests", 0)
            pending = result_json.get("numPendingTests", 0)
            
            # Extract test cases
            test_cases = []
            for test_suite in test_results:
                for test_result in test_suite.get("assertionResults", []):
                    test_cases.append({
                        "name": test_result.get("title"),
                        "classname": test_suite.get("name"),
                        "status": test_result.get("status"),
                        "message": test_result.get("failureMessages", [])
                    })
            
            # Extract coverage
            coverage_data = {}
            coverage_summary = result_json.get("coverageMap", {})
            if coverage_summary:
                # Overall coverage
                total_statements = 0
                covered_statements = 0
                
                for file_path, file_coverage in coverage_summary.items():
                    statements = file_coverage.get("s", {})
                    total_statements += len(statements)
                    covered_statements += sum(1 for count in statements.values() if count > 0)
                
                overall_coverage = (covered_statements / total_statements) * 100 if total_statements > 0 else 0
                coverage_data["overall"] = overall_coverage
                
                # Per-file coverage
                coverage_data["files"] = {}
                for file_path, file_coverage in coverage_summary.items():
                    statements = file_coverage.get("s", {})
                    total = len(statements)
                    covered = sum(1 for count in statements.values() if count > 0)
                    file_coverage_pct = (covered / total) * 100 if total > 0 else 0
                    coverage_data["files"][file_path] = file_coverage_pct
            
            self.test_results = {
                "framework": "jest",
                "success": process.returncode == 0,
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": pending,
                "pass_rate": (passed / total) if total > 0 else 0,
                "execution_time": elapsed_time,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "test_cases": test_cases,
                "coverage": coverage_data
            }
            
            return self.test_results
        except Exception as e:
            print(f"Error parsing test results: {e}")
            
            # Fallback to basic results
            return {
                "framework": "jest",
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "execution_time": elapsed_time
            }
    
    def _run_custom_tests(self) -> Dict[str, Any]:
        """
        Run tests using a custom command.
        
        Returns:
            Dictionary with test results
        """
        if not self.test_command:
            return {
                "framework": "custom",
                "success": False,
                "error": "No test command provided"
            }
        
        # Run tests
        start_time = time.time()
        process = subprocess.run(
            self.test_command,
            cwd=self.repo_path,
            shell=True,
            capture_output=True,
            text=True
        )
        elapsed_time = time.time() - start_time
        
        self.test_results = {
            "framework": "custom",
            "success": process.returncode == 0,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "execution_time": elapsed_time
        }
        
        return self.test_results
    
    def verify_bugfix(self, bug_description: str) -> Dict[str, Any]:
        """
        Verify if a bug has been fixed.
        
        Args:
            bug_description: Description of the bug to verify
            
        Returns:
            Dictionary with verification results
        """
        # Extract keywords from bug description
        keywords = set(re.findall(r'\b\w+\b', bug_description.lower()))
        
        # Run tests
        test_results = self.run_tests()
        
        # Check if all tests pass
        all_pass = test_results.get("success", False)
        
        # Check if any failing tests match the bug description
        matching_failed_tests = []
        
        for test_case in test_results.get("test_cases", []):
            if test_case.get("status") != "passed":
                test_name = test_case.get("name", "").lower()
                test_class = test_case.get("classname", "").lower()
                
                # Count keyword matches in test name and class
                matches = sum(1 for keyword in keywords if keyword in test_name or keyword in test_class)
                
                if matches > 0:
                    matching_failed_tests.append(test_case)
        
        return {
            "all_tests_pass": all_pass,
            "matching_failed_tests": matching_failed_tests,
            "test_results": test_results,
            "likely_fixed": all_pass and not matching_failed_tests,
            "verification_confidence": 0.8 if all_pass and not matching_failed_tests else 0.4
        }
    
    def compare_test_results(self, before_results: Dict[str, Any], after_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare test results before and after a bug fix.
        
        Args:
            before_results: Test results before the fix
            after_results: Test results after the fix
            
        Returns:
            Dictionary with comparison results
        """
        # Check if tests improved
        before_pass = before_results.get("pass_rate", 0)
        after_pass = after_results.get("pass_rate", 0)
        
        pass_rate_change = after_pass - before_pass
        
        # Compare failed tests
        before_failed = set(
            test.get("name") for test in before_results.get("test_cases", [])
            if test.get("status") != "passed"
        )
        
        after_failed = set(
            test.get("name") for test in after_results.get("test_cases", [])
            if test.get("status") != "passed"
        )
        
        fixed_tests = before_failed - after_failed
        new_failures = after_failed - before_failed
        
        # Compare coverage
        before_coverage = before_results.get("coverage", {}).get("overall", 0)
        after_coverage = after_results.get("coverage", {}).get("overall", 0)
        
        coverage_change = after_coverage - before_coverage
        
        return {
            "pass_rate_change": pass_rate_change,
            "fixed_tests": list(fixed_tests),
            "new_failures": list(new_failures),
            "coverage_change": coverage_change,
            "improved": pass_rate_change > 0 and not new_failures,
            "regression": new_failures or pass_rate_change < 0,
            "overall_improvement": pass_rate_change > 0 and coverage_change >= 0 and not new_failures
        } 