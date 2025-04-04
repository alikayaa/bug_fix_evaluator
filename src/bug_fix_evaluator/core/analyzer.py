"""
Code analyzer module for Bug Fix Evaluator.

This module provides classes for analyzing code changes, identifying bug patterns,
and extracting relevant context from bug fixes.
"""

import re
import logging
from typing import Dict, List, Set, Tuple, Optional, Any, Union
import difflib

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """
    Analyzes code changes to extract patterns and context from bug fixes.
    """
    
    def __init__(self):
        """
        Initialize the code analyzer with default settings.
        """
        logger.debug("CodeAnalyzer initialized")
    
    def analyze_bug_fix(self, 
                       bug_files: Dict[str, str], 
                       fixed_files: Dict[str, str],
                       diffs: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze a bug fix by comparing the buggy and fixed versions of files.
        
        Args:
            bug_files: Dictionary mapping file paths to their content in buggy state
            fixed_files: Dictionary mapping file paths to their content in fixed state
            diffs: Dictionary mapping file paths to their git diff patches
            
        Returns:
            Dictionary containing analysis results:
            - changed_files: List of changed files
            - bug_patterns: Detected bug patterns
            - context: Extracted context information
            - complexity: Estimated complexity of the fix
        """
        result = {
            "changed_files": [],
            "bug_patterns": [],
            "context": {},
            "complexity": {
                "score": 0,
                "factors": []
            }
        }
        
        # Analyze each file that has changes
        for file_path in diffs.keys():
            if file_path not in bug_files or file_path not in fixed_files:
                logger.warning(f"Skipping analysis for {file_path}: missing content")
                continue
                
            file_analysis = self._analyze_file_changes(
                file_path, 
                bug_files[file_path], 
                fixed_files[file_path], 
                diffs[file_path]
            )
            
            result["changed_files"].append(file_analysis)
            
            # Update bug patterns from this file's analysis
            for pattern in file_analysis.get("patterns", []):
                if pattern not in result["bug_patterns"]:
                    result["bug_patterns"].append(pattern)
            
            # Update complexity score
            file_complexity = file_analysis.get("complexity", {})
            result["complexity"]["score"] += file_complexity.get("score", 0)
            
            for factor in file_complexity.get("factors", []):
                if factor not in result["complexity"]["factors"]:
                    result["complexity"]["factors"].append(factor)
        
        # Extract relevant context
        result["context"] = self._extract_context(result["changed_files"], bug_files)
        
        return result
    
    def _analyze_file_changes(self, 
                             file_path: str, 
                             bug_content: str, 
                             fixed_content: str, 
                             diff: str) -> Dict[str, Any]:
        """
        Analyze changes between buggy and fixed versions of a file.
        
        Args:
            file_path: Path to the file
            bug_content: Content of the file in buggy state
            fixed_content: Content of the file in fixed state
            diff: Git diff patch of changes
            
        Returns:
            Dictionary with file analysis results:
            - path: File path
            - patterns: Detected bug patterns
            - changes: Detailed list of changes
            - complexity: Complexity assessment for this file
        """
        file_type = self._get_file_type(file_path)
        
        result = {
            "path": file_path,
            "file_type": file_type,
            "patterns": [],
            "changes": [],
            "complexity": {
                "score": 0,
                "factors": []
            }
        }
        
        # Skip binary or very large files
        if not bug_content or not fixed_content:
            result["patterns"].append("binary_change")
            return result
            
        # Get line-by-line differences
        changes = self._get_line_changes(bug_content, fixed_content)
        result["changes"] = changes
        
        # Detect bug patterns based on file type and changes
        patterns = self._detect_bug_patterns(file_type, changes, diff)
        result["patterns"] = patterns
        
        # Assess complexity based on changes and patterns
        complexity = self._assess_complexity(file_path, changes, patterns)
        result["complexity"] = complexity
        
        return result
    
    def _get_line_changes(self, bug_content: str, fixed_content: str) -> List[Dict[str, Any]]:
        """
        Get detailed line-by-line changes between bug and fixed content.
        
        Args:
            bug_content: Content of the file in buggy state
            fixed_content: Content of the file in fixed state
            
        Returns:
            List of change dictionaries with:
            - type: Type of change ('added', 'removed', 'modified')
            - line_numbers: Line numbers in buggy and fixed versions
            - content: Changed content
        """
        changes = []
        
        # Split content into lines
        bug_lines = bug_content.splitlines()
        fixed_lines = fixed_content.splitlines()
        
        # Get unified diff
        diff = list(difflib.unified_diff(
            bug_lines, 
            fixed_lines, 
            n=0,  # No context lines
            lineterm=''
        ))
        
        # Parse the diff to extract changes
        bug_line_num = 0
        fixed_line_num = 0
        
        for line in diff:
            if line.startswith('---') or line.startswith('+++'):
                continue
                
            if line.startswith('@@'):
                # Extract line numbers from hunk header
                match = re.match(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
                if match:
                    bug_line_num = int(match.group(1)) - 1  # 0-indexed
                    fixed_line_num = int(match.group(2)) - 1  # 0-indexed
                continue
            
            if line.startswith('-'):
                # Line removed from buggy version
                changes.append({
                    "type": "removed",
                    "line_numbers": {
                        "bug": bug_line_num + 1,  # 1-indexed
                        "fixed": None
                    },
                    "content": line[1:]
                })
                bug_line_num += 1
            elif line.startswith('+'):
                # Line added in fixed version
                changes.append({
                    "type": "added",
                    "line_numbers": {
                        "bug": None,
                        "fixed": fixed_line_num + 1  # 1-indexed
                    },
                    "content": line[1:]
                })
                fixed_line_num += 1
            else:
                # Unchanged line (should not occur with n=0)
                bug_line_num += 1
                fixed_line_num += 1
        
        # Post-process to identify modified lines (pairs of removed + added)
        i = 0
        while i < len(changes) - 1:
            if (changes[i]["type"] == "removed" and 
                changes[i+1]["type"] == "added"):
                # Convert to a "modified" change
                modified = {
                    "type": "modified",
                    "line_numbers": {
                        "bug": changes[i]["line_numbers"]["bug"],
                        "fixed": changes[i+1]["line_numbers"]["fixed"]
                    },
                    "content": {
                        "bug": changes[i]["content"],
                        "fixed": changes[i+1]["content"]
                    }
                }
                changes[i] = modified
                changes.pop(i+1)
            else:
                i += 1
                
        return changes
    
    def _detect_bug_patterns(self, 
                            file_type: str, 
                            changes: List[Dict[str, Any]], 
                            diff: str) -> List[str]:
        """
        Detect common bug patterns based on file type and changes.
        
        Args:
            file_type: Type of the file (e.g., 'python', 'javascript', 'html', etc.)
            changes: List of changes between bug and fixed versions
            diff: Git diff patch of changes
            
        Returns:
            List of detected bug patterns
        """
        patterns = []
        
        # Count types of changes
        added_count = sum(1 for c in changes if c["type"] == "added")
        removed_count = sum(1 for c in changes if c["type"] == "removed")
        modified_count = sum(1 for c in changes if c["type"] == "modified")
        
        # Check for simple pattern - only adding lines
        if added_count > 0 and removed_count == 0 and modified_count == 0:
            patterns.append("missing_code")
            
        # Check for simple pattern - only removing lines
        if removed_count > 0 and added_count == 0 and modified_count == 0:
            patterns.append("extraneous_code")
            
        # Check for simple pattern - only modifying lines
        if modified_count > 0 and added_count == 0 and removed_count == 0:
            patterns.append("incorrect_logic")
            
        # Check for common patterns by file type
        if file_type == "python":
            patterns.extend(self._detect_python_patterns(changes))
        elif file_type == "javascript" or file_type == "typescript":
            patterns.extend(self._detect_js_patterns(changes))
        elif file_type == "java":
            patterns.extend(self._detect_java_patterns(changes))
            
        # Check for common patterns across languages
        patterns.extend(self._detect_common_patterns(changes, diff))
        
        return patterns
    
    def _detect_python_patterns(self, changes: List[Dict[str, Any]]) -> List[str]:
        """
        Detect Python-specific bug patterns.
        
        Args:
            changes: List of changes between bug and fixed versions
            
        Returns:
            List of detected Python-specific bug patterns
        """
        patterns = []
        
        for change in changes:
            if change["type"] == "modified":
                bug_line = change["content"]["bug"]
                fixed_line = change["content"]["fixed"]
                
                # Check for indentation errors
                if bug_line.lstrip() == fixed_line.lstrip() and bug_line.startswith(' ') != fixed_line.startswith(' '):
                    patterns.append("indentation_error")
                
                # Check for exception handling
                if ("except:" in bug_line and 
                    re.match(r"except\s+\w+(\s+as\s+\w+)?:", fixed_line)):
                    patterns.append("bare_except")
                    
                # Check for string formatting changes
                if ("%" in bug_line and "{" in fixed_line and "}" in fixed_line) or \
                   ("+" in bug_line and "format(" in fixed_line) or \
                   ("+" in bug_line and "f\"" in fixed_line):
                    patterns.append("string_formatting")
        
        return patterns
    
    def _detect_js_patterns(self, changes: List[Dict[str, Any]]) -> List[str]:
        """
        Detect JavaScript/TypeScript-specific bug patterns.
        
        Args:
            changes: List of changes between bug and fixed versions
            
        Returns:
            List of detected JavaScript/TypeScript-specific bug patterns
        """
        patterns = []
        
        for change in changes:
            if change["type"] == "modified":
                bug_line = change["content"]["bug"]
                fixed_line = change["content"]["fixed"]
                
                # Check for == vs === changes
                if "==" in bug_line and "===" in fixed_line:
                    patterns.append("loose_equality")
                    
                # Check for promise/async handling
                if ("then(" in bug_line and "await" in fixed_line) or \
                   ("callback" in bug_line and "Promise" in fixed_line):
                    patterns.append("async_handling")
                    
                # Check for null/undefined checking
                if re.search(r"(\w+)\.", bug_line) and re.search(r"(\w+)\s*(\?\.|&&)", fixed_line):
                    patterns.append("null_check")
        
        return patterns
    
    def _detect_java_patterns(self, changes: List[Dict[str, Any]]) -> List[str]:
        """
        Detect Java-specific bug patterns.
        
        Args:
            changes: List of changes between bug and fixed versions
            
        Returns:
            List of detected Java-specific bug patterns
        """
        patterns = []
        
        for change in changes:
            if change["type"] == "modified":
                bug_line = change["content"]["bug"]
                fixed_line = change["content"]["fixed"]
                
                # Check for null checks
                if re.search(r"(\w+)\.", bug_line) and re.search(r"(\w+)\s*!=\s*null", fixed_line):
                    patterns.append("null_check")
                    
                # Check for resource handling (try-with-resources)
                if "new " in bug_line and "close()" in bug_line and "try (" in fixed_line:
                    patterns.append("resource_handling")
                    
                # Check for concurrency issues
                if "synchronized" in fixed_line and "synchronized" not in bug_line:
                    patterns.append("concurrency")
        
        return patterns
    
    def _detect_common_patterns(self, 
                               changes: List[Dict[str, Any]], 
                               diff: str) -> List[str]:
        """
        Detect language-agnostic bug patterns.
        
        Args:
            changes: List of changes between bug and fixed versions
            diff: Git diff patch of changes
            
        Returns:
            List of detected common bug patterns
        """
        patterns = []
        
        # Check for off-by-one errors
        for change in changes:
            if change["type"] == "modified":
                bug_line = change["content"]["bug"]
                fixed_line = change["content"]["fixed"]
                
                # Look for +1 or -1 changes
                if (re.search(r"(\d+)", bug_line) and 
                    re.search(r"(\d+)", fixed_line)):
                    bug_nums = [int(m) for m in re.findall(r"(\d+)", bug_line)]
                    fixed_nums = [int(m) for m in re.findall(r"(\d+)", fixed_line)]
                    
                    for b, f in zip(bug_nums, fixed_nums):
                        if abs(b - f) == 1:
                            patterns.append("off_by_one")
                            break
        
        # Check for condition inversion
        condition_inversions = 0
        for change in changes:
            if change["type"] == "modified":
                bug_line = change["content"]["bug"]
                fixed_line = change["content"]["fixed"]
                
                # Check for inverting conditions (> to <, == to !=, etc.)
                if (">" in bug_line and "<" in fixed_line) or \
                   ("<" in bug_line and ">" in fixed_line) or \
                   ("==" in bug_line and "!=" in fixed_line) or \
                   ("!=" in bug_line and "==" in fixed_line):
                    condition_inversions += 1
        
        if condition_inversions > 0:
            patterns.append("condition_inversion")
            
        # Check for error/exception handling
        try_catch_changes = 0
        for change in changes:
            if change["type"] == "added":
                if ("try" in change["content"] or 
                    "catch" in change["content"] or 
                    "except" in change["content"] or 
                    "finally" in change["content"]):
                    try_catch_changes += 1
        
        if try_catch_changes > 0:
            patterns.append("error_handling")
            
        # Check for variable initialization
        init_changes = 0
        for change in changes:
            if change["type"] == "added" or change["type"] == "modified":
                content = change["content"]["fixed"] if change["type"] == "modified" else change["content"]
                if re.search(r"(\w+)\s*=\s*[^=]+", content):
                    init_changes += 1
        
        if init_changes > 0:
            patterns.append("initialization")
            
        return patterns
    
    def _assess_complexity(self, 
                          file_path: str, 
                          changes: List[Dict[str, Any]], 
                          patterns: List[str]) -> Dict[str, Any]:
        """
        Assess the complexity of a bug fix based on changes and patterns.
        
        Args:
            file_path: Path to the file
            changes: List of changes between bug and fixed versions
            patterns: Detected bug patterns
            
        Returns:
            Dictionary with complexity assessment:
            - score: Numeric complexity score (higher is more complex)
            - factors: List of factors contributing to complexity
        """
        complexity = {
            "score": 0,
            "factors": []
        }
        
        # Basic complexity based on number of changes
        added_count = sum(1 for c in changes if c["type"] == "added")
        removed_count = sum(1 for c in changes if c["type"] == "removed")
        modified_count = sum(1 for c in changes if c["type"] == "modified")
        
        total_changes = added_count + removed_count + modified_count
        
        # Base score from number of changes
        if total_changes <= 3:
            complexity["score"] += 1
            complexity["factors"].append("few_changes")
        elif total_changes <= 10:
            complexity["score"] += 2
            complexity["factors"].append("moderate_changes")
        else:
            complexity["score"] += 3
            complexity["factors"].append("many_changes")
            
        # Add complexity for multiple files changed
        if "." not in file_path:  # This indicates the file_path is actually a directory
            complexity["score"] += 2
            complexity["factors"].append("multi_file")
            
        # Add complexity for certain patterns
        complex_patterns = [
            "concurrency", 
            "async_handling", 
            "error_handling",
            "resource_handling"
        ]
        
        for pattern in patterns:
            if pattern in complex_patterns:
                complexity["score"] += 1
                complexity["factors"].append(f"complex_pattern_{pattern}")
                
        # Adjust score by file type
        file_type = self._get_file_type(file_path)
        if file_type in ["python", "javascript", "typescript"]:
            pass  # No adjustment
        elif file_type in ["java", "c++", "rust"]:
            complexity["score"] += 1
            complexity["factors"].append("complex_language")
            
        return complexity
    
    def _extract_context(self, 
                        file_analyses: List[Dict[str, Any]], 
                        bug_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract relevant context information from the bug fix.
        
        Args:
            file_analyses: Analyses of changed files
            bug_files: Content of files in buggy state
            
        Returns:
            Dictionary with extracted context:
            - summary: Summary of the bug fix
            - file_contexts: Context information for each file
        """
        context = {
            "summary": "",
            "file_contexts": {}
        }
        
        all_patterns = []
        for file_analysis in file_analyses:
            patterns = file_analysis.get("patterns", [])
            all_patterns.extend(patterns)
            
        # Generate summary based on patterns
        if "missing_code" in all_patterns:
            context["summary"] += "Missing code. "
        if "extraneous_code" in all_patterns:
            context["summary"] += "Extraneous code. "
        if "incorrect_logic" in all_patterns:
            context["summary"] += "Incorrect logic. "
        if "off_by_one" in all_patterns:
            context["summary"] += "Off-by-one error. "
        if "condition_inversion" in all_patterns:
            context["summary"] += "Inverted condition. "
        if "error_handling" in all_patterns:
            context["summary"] += "Missing error handling. "
            
        # Extract context for each file
        for file_analysis in file_analyses:
            file_path = file_analysis["path"]
            changes = file_analysis.get("changes", [])
            
            # Skip if no content available
            if file_path not in bug_files or not bug_files[file_path]:
                continue
                
            # Get content and split into lines
            content = bug_files[file_path]
            lines = content.splitlines()
            
            # Extract changed line numbers in buggy version
            changed_lines = []
            for change in changes:
                if change["type"] == "removed" or change["type"] == "modified":
                    if change["line_numbers"]["bug"]:
                        changed_lines.append(change["line_numbers"]["bug"])
            
            # Extract context around changed lines
            context_lines = {}
            for line_num in changed_lines:
                # Get a window of lines around the changed line
                start = max(0, line_num - 3)
                end = min(len(lines), line_num + 2)
                
                context_lines[line_num] = {
                    "line": line_num,
                    "content": lines[line_num - 1] if line_num <= len(lines) else "",
                    "before": lines[start:line_num - 1],
                    "after": lines[line_num:end]
                }
            
            file_context = {
                "path": file_path,
                "changed_lines": changed_lines,
                "context_lines": context_lines
            }
            
            context["file_contexts"][file_path] = file_context
            
        return context
        
    def _get_file_type(self, file_path: str) -> str:
        """
        Determine file type from file path extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            String representing the file type
        """
        ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
        
        if ext in ['py']:
            return 'python'
        elif ext in ['js']:
            return 'javascript'
        elif ext in ['ts', 'tsx']:
            return 'typescript'
        elif ext in ['java']:
            return 'java'
        elif ext in ['c', 'cpp', 'h', 'hpp']:
            return 'cpp'
        elif ext in ['rs']:
            return 'rust'
        elif ext in ['go']:
            return 'go'
        elif ext in ['rb']:
            return 'ruby'
        elif ext in ['php']:
            return 'php'
        elif ext in ['html', 'htm']:
            return 'html'
        elif ext in ['css']:
            return 'css'
        elif ext in ['json']:
            return 'json'
        elif ext in ['md', 'markdown']:
            return 'markdown'
        elif ext in ['yml', 'yaml']:
            return 'yaml'
        else:
            return 'unknown'
