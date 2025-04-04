#!/usr/bin/env python3
import os
import re
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Union, Tuple
import difflib
import radon.complexity as complexity
import radon.metrics as metrics
import pylint.lint
from pylint.reporters.text import TextReporter
import io

class CodeAnalyzer:
    def __init__(self, language: str = None):
        """
        Initialize the code analyzer.
        
        Args:
            language: Programming language (auto-detected if None)
        """
        self.language = language
        self.supported_languages = {
            "python": [".py"],
            "javascript": [".js", ".jsx", ".ts", ".tsx"],
            "java": [".java"],
            "c": [".c", ".h"],
            "cpp": [".cpp", ".hpp", ".cc", ".hh"],
            "csharp": [".cs"],
            "go": [".go"],
            "rust": [".rs"],
            "ruby": [".rb"],
            "php": [".php"],
            "swift": [".swift"],
            "kotlin": [".kt", ".kts"]
        }
    
    def detect_language(self, file_path: str) -> str:
        """
        Detect the programming language from file extension.
        
        Args:
            file_path: Path to the code file
            
        Returns:
            Detected language or 'unknown'
        """
        _, ext = os.path.splitext(file_path)
        
        for lang, extensions in self.supported_languages.items():
            if ext in extensions:
                return lang
        
        return "unknown"
    
    def compute_cyclomatic_complexity(self, code: str, language: str = None) -> Dict[str, Any]:
        """
        Compute cyclomatic complexity metrics for the given code.
        
        Args:
            code: Source code to analyze
            language: Programming language (auto-detected if None)
            
        Returns:
            Dictionary with complexity metrics
        """
        if not language:
            language = self.language or "python"  # Default to Python
        
        if language != "python":
            # For now, only Python is supported for complexity analysis
            return {"average": 0, "functions": {}}
        
        try:
            # Use radon to compute complexity for Python code
            results = complexity.cc_visit(code)
            
            function_complexity = {}
            total_complexity = 0
            
            for result in results:
                function_complexity[result.name] = {
                    "complexity": result.complexity,
                    "rank": result.rank,
                    "line_number": result.lineno
                }
                total_complexity += result.complexity
            
            avg_complexity = total_complexity / len(function_complexity) if function_complexity else 0
            
            return {
                "average": avg_complexity,
                "functions": function_complexity
            }
        except Exception as e:
            print(f"Error computing complexity: {e}")
            return {"average": 0, "functions": {}}
    
    def run_linter(self, code: str, file_path: str, language: str = None) -> Dict[str, Any]:
        """
        Run linter on the given code.
        
        Args:
            code: Source code to analyze
            file_path: Path to the code file (for linter configuration)
            language: Programming language (auto-detected if None)
            
        Returns:
            Dictionary with linter results
        """
        if not language:
            language = self.language or self.detect_language(file_path)
        
        if language == "python":
            return self._run_pylint(code)
        elif language in ["javascript", "typescript"]:
            return self._run_eslint(code, file_path)
        else:
            return {"errors": 0, "warnings": 0, "issues": []}
    
    def _run_pylint(self, code: str) -> Dict[str, Any]:
        """
        Run pylint on Python code.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Dictionary with pylint results
        """
        # Create a temporary file for pylint
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            # Capture pylint output
            output_stream = io.StringIO()
            reporter = TextReporter(output_stream)
            
            # Run pylint
            pylint.lint.Run(
                [temp_file_path, "--output-format=text"],
                reporter=reporter,
                do_exit=False
            )
            
            # Parse pylint output
            output = output_stream.getvalue()
            
            # Count errors and warnings
            errors = len(re.findall(r"\(E\d+\)", output))
            warnings = len(re.findall(r"\(W\d+\)", output))
            
            # Extract issues
            issues = []
            for line in output.split("\n"):
                if re.search(r"[EWC]\d+", line):
                    issues.append(line.strip())
            
            return {
                "errors": errors,
                "warnings": warnings,
                "issues": issues
            }
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    def _run_eslint(self, code: str, file_path: str) -> Dict[str, Any]:
        """
        Run eslint on JavaScript/TypeScript code.
        
        Args:
            code: JavaScript/TypeScript code to analyze
            file_path: Path to the original file
            
        Returns:
            Dictionary with eslint results
        """
        # This would require eslint to be installed
        # For now, return placeholder results
        return {"errors": 0, "warnings": 0, "issues": []}
    
    def check_code_style(self, code: str, file_path: str, language: str = None) -> Dict[str, Any]:
        """
        Check code style using formatters.
        
        Args:
            code: Source code to analyze
            file_path: Path to the code file
            language: Programming language (auto-detected if None)
            
        Returns:
            Dictionary with style check results
        """
        if not language:
            language = self.language or self.detect_language(file_path)
        
        if language == "python":
            return self._check_python_style(code)
        else:
            # Placeholder for other languages
            return {"style_score": 1.0, "issues": []}
    
    def _check_python_style(self, code: str) -> Dict[str, Any]:
        """
        Check Python code style using black and flake8.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Dictionary with style check results
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            # Try to run black to check if code is formatted according to black
            black_result = subprocess.run(
                ["black", "--check", temp_file_path],
                capture_output=True,
                text=True
            )
            
            # Count style issues
            issues = []
            
            if black_result.returncode != 0:
                issues.append("Code does not match black formatting")
            
            # Try to run flake8
            flake8_result = subprocess.run(
                ["flake8", temp_file_path],
                capture_output=True,
                text=True
            )
            
            # Add flake8 issues
            for line in flake8_result.stdout.split("\n"):
                if line.strip():
                    issues.append(line.strip())
            
            # Calculate style score based on issues
            style_score = 1.0 if not issues else max(0.0, 1.0 - (len(issues) / 10))
            
            return {
                "style_score": style_score,
                "issues": issues
            }
        except Exception as e:
            print(f"Error checking Python style: {e}")
            return {"style_score": 0.5, "issues": [str(e)]}
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    def calculate_diff_metrics(self, old_code: str, new_code: str) -> Dict[str, Any]:
        """
        Calculate diff metrics between old and new code.
        
        Args:
            old_code: Original code
            new_code: Modified code
            
        Returns:
            Dictionary with diff metrics
        """
        # Calculate diff
        diff = difflib.unified_diff(
            old_code.splitlines(),
            new_code.splitlines(),
            lineterm=""
        )
        
        diff_lines = list(diff)
        
        # Count added and removed lines
        added_lines = sum(1 for line in diff_lines if line.startswith("+") and not line.startswith("+++"))
        removed_lines = sum(1 for line in diff_lines if line.startswith("-") and not line.startswith("---"))
        
        # Calculate diff size
        diff_size = added_lines + removed_lines
        
        return {
            "added_lines": added_lines,
            "removed_lines": removed_lines,
            "diff_size": diff_size,
            "diff_ratio": diff_size / (len(old_code.splitlines()) + 0.001),
            "diff_text": "\n".join(diff_lines)
        }
    
    def calculate_code_similarity(self, code1: str, code2: str) -> float:
        """
        Calculate similarity between two code fragments.
        
        Args:
            code1: First code fragment
            code2: Second code fragment
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, code1, code2)
        return matcher.ratio()
    
    def check_compiler_errors(self, code: str, file_path: str, language: str = None) -> Dict[str, Any]:
        """
        Check for compiler errors.
        
        Args:
            code: Source code to analyze
            file_path: Path to the code file
            language: Programming language (auto-detected if None)
            
        Returns:
            Dictionary with compiler check results
        """
        if not language:
            language = self.language or self.detect_language(file_path)
        
        if language == "python":
            return self._check_python_syntax(code)
        else:
            # Placeholder for other languages
            return {"compiles": True, "errors": []}
    
    def _check_python_syntax(self, code: str) -> Dict[str, Any]:
        """
        Check Python code syntax.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Dictionary with syntax check results
        """
        try:
            compile(code, "<string>", "exec")
            return {"compiles": True, "errors": []}
        except SyntaxError as e:
            return {
                "compiles": False,
                "errors": [f"Line {e.lineno}: {e.msg}"]
            }
    
    def analyze_code(self, old_code: str, new_code: str, file_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive code analysis.
        
        Args:
            old_code: Original code
            new_code: Modified code
            file_path: Path to the code file
            
        Returns:
            Dictionary with analysis results
        """
        language = self.detect_language(file_path)
        
        # Compile checks
        compile_result = self.check_compiler_errors(new_code, file_path, language)
        
        # Only proceed with other metrics if code compiles
        if compile_result["compiles"]:
            complexity_result = self.compute_cyclomatic_complexity(new_code, language)
            lint_result = self.run_linter(new_code, file_path, language)
            style_result = self.check_code_style(new_code, file_path, language)
            old_complexity = self.compute_cyclomatic_complexity(old_code, language)
            diff_metrics = self.calculate_diff_metrics(old_code, new_code)
            similarity = self.calculate_code_similarity(old_code, new_code)
            
            return {
                "language": language,
                "compiles": True,
                "complexity": complexity_result,
                "old_complexity": old_complexity,
                "complexity_change": complexity_result["average"] - old_complexity["average"],
                "lint": lint_result,
                "style": style_result,
                "diff": diff_metrics,
                "similarity": similarity
            }
        else:
            return {
                "language": language,
                "compiles": False,
                "compile_errors": compile_result["errors"],
                "similarity": self.calculate_code_similarity(old_code, new_code)
            } 