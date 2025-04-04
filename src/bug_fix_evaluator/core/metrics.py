"""
Evaluation metrics module for Bug Fix Evaluator.

This module provides classes for evaluating bug fixes using various metrics
and scoring algorithms.
"""

import logging
import math
from typing import Dict, List, Set, Tuple, Optional, Any, Union

logger = logging.getLogger(__name__)

class EvaluationMetrics:
    """
    Evaluates bug fixes using various metrics and scoring algorithms.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the evaluation metrics with optional configuration.
        
        Args:
            config: Optional configuration dictionary with metric weights and settings
        """
        self.config = config or {}
        self.metrics = self._get_default_metrics()
        
        # Override defaults with config if provided
        if config:
            for key, value in config.items():
                if key.startswith('weight_'):
                    metric_name = key[7:]  # Remove 'weight_' prefix
                    if metric_name in self.metrics:
                        self.metrics[metric_name]['weight'] = value
        
        logger.debug(f"EvaluationMetrics initialized with {len(self.metrics)} metrics")
    
    def evaluate(self, 
                engineer_analysis: Dict[str, Any], 
                ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the AI's bug fix against the engineer's fix.
        
        Args:
            engineer_analysis: Analysis results from engineer's fix
            ai_analysis: Analysis results from AI's fix
            
        Returns:
            Dictionary with evaluation metrics and scores:
            - overall_score: Overall weighted score (0-100)
            - metrics: Individual metric scores
            - comparison: Detailed comparison data
            - strengths: Identified strengths of the AI solution
            - weaknesses: Identified weaknesses of the AI solution
        """
        logger.info("Evaluating bug fix solutions")
        
        result = {
            "overall_score": 0,
            "metrics": {},
            "comparison": {},
            "strengths": [],
            "weaknesses": []
        }
        
        # Calculate individual metric scores
        for metric_name, metric_config in self.metrics.items():
            if metric_config.get('enabled', True):
                metric_func = getattr(self, f"_calc_{metric_name}", None)
                if metric_func:
                    score, details = metric_func(engineer_analysis, ai_analysis)
                    result["metrics"][metric_name] = {
                        "score": score,
                        "weight": metric_config['weight'],
                        "details": details
                    }
                    
                    # Update overall score
                    result["overall_score"] += score * metric_config['weight']
                else:
                    logger.warning(f"Metric function not found for {metric_name}")
        
        # Normalize overall score to 0-100 range
        total_weight = sum(m['weight'] for m in self.metrics.values() if m.get('enabled', True))
        if total_weight > 0:
            result["overall_score"] = (result["overall_score"] / total_weight) * 100
        
        # Generate comparison data
        result["comparison"] = self._generate_comparison(engineer_analysis, ai_analysis)
        
        # Identify strengths and weaknesses
        result["strengths"] = self._identify_strengths(result["metrics"])
        result["weaknesses"] = self._identify_weaknesses(result["metrics"])
        
        return result
    
    def _get_default_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get the default set of metrics and their weights.
        
        Returns:
            Dictionary mapping metric names to their configuration
        """
        return {
            "correctness": {
                "weight": 0.35,
                "enabled": True,
                "description": "Measures if the fix correctly addresses the bug"
            },
            "completeness": {
                "weight": 0.15,
                "enabled": True,
                "description": "Measures if the fix addresses all aspects of the bug"
            },
            "pattern_match": {
                "weight": 0.10,
                "enabled": True,
                "description": "Measures how well the fix patterns match the reference fix"
            },
            "cleanliness": {
                "weight": 0.15,
                "enabled": True,
                "description": "Measures code cleanliness and adherence to best practices"
            },
            "efficiency": {
                "weight": 0.10,
                "enabled": True,
                "description": "Measures the efficiency of the fix"
            },
            "complexity": {
                "weight": 0.15,
                "enabled": True,
                "description": "Measures the complexity of the fix compared to the reference"
            }
        }
    
    def _calc_correctness(self, 
                         engineer_analysis: Dict[str, Any], 
                         ai_analysis: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate correctness score by comparing AI and engineer fixes.
        
        Args:
            engineer_analysis: Analysis results from engineer's fix
            ai_analysis: Analysis results from AI's fix
            
        Returns:
            Tuple of (score, details) where:
            - score: float from 0 to 1
            - details: Dictionary with details about the score calculation
        """
        details = {
            "file_scores": {},
            "factors": []
        }
        
        # Get changed files from both analyses
        engineer_files = {f["path"] for f in engineer_analysis.get("changed_files", [])}
        ai_files = {f["path"] for f in ai_analysis.get("changed_files", [])}
        
        # Check for files that should have been changed but weren't
        missed_files = engineer_files - ai_files
        if missed_files:
            details["factors"].append(f"AI missed changes to {len(missed_files)} files")
            for file in missed_files:
                details["file_scores"][file] = 0.0
        
        # Check for files that were changed unnecessarily
        extra_files = ai_files - engineer_files
        if extra_files:
            details["factors"].append(f"AI made unnecessary changes to {len(extra_files)} files")
            for file in extra_files:
                details["file_scores"][file] = 0.0
        
        # For files changed by both, compare changes
        common_files = engineer_files.intersection(ai_files)
        for file in common_files:
            engineer_file = next((f for f in engineer_analysis.get("changed_files", []) if f["path"] == file), None)
            ai_file = next((f for f in ai_analysis.get("changed_files", []) if f["path"] == file), None)
            
            if engineer_file and ai_file:
                file_score = self._compare_file_changes(engineer_file, ai_file)
                details["file_scores"][file] = file_score
        
        # Calculate overall correctness score
        if not engineer_files:
            # If engineer made no changes, this is a special case
            score = 0.0
            details["factors"].append("Reference solution made no changes")
        elif not common_files:
            # If no common files, score is 0
            score = 0.0
        else:
            # Average file scores, weighted by importance of the file
            # (currently all files weighted equally)
            file_scores = [details["file_scores"].get(file, 0.0) for file in engineer_files]
            score = sum(file_scores) / len(engineer_files)
        
        return score, details
    
    def _calc_completeness(self, 
                          engineer_analysis: Dict[str, Any], 
                          ai_analysis: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate completeness score by checking if all bug aspects were fixed.
        
        Args:
            engineer_analysis: Analysis results from engineer's fix
            ai_analysis: Analysis results from AI's fix
            
        Returns:
            Tuple of (score, details) where:
            - score: float from 0 to 1
            - details: Dictionary with details about the score calculation
        """
        details = {
            "addressed_patterns": [],
            "missed_patterns": [],
            "total_patterns": 0
        }
        
        # Get bug patterns from engineer's analysis
        engineer_patterns = set(engineer_analysis.get("bug_patterns", []))
        ai_patterns = set(ai_analysis.get("bug_patterns", []))
        
        # Check which patterns were addressed by AI
        addressed_patterns = engineer_patterns.intersection(ai_patterns)
        missed_patterns = engineer_patterns - ai_patterns
        
        details["addressed_patterns"] = list(addressed_patterns)
        details["missed_patterns"] = list(missed_patterns)
        details["total_patterns"] = len(engineer_patterns)
        
        # Calculate completeness score
        if not engineer_patterns:
            score = 1.0  # No patterns to fix
        else:
            score = len(addressed_patterns) / len(engineer_patterns)
        
        return score, details
    
    def _calc_pattern_match(self, 
                           engineer_analysis: Dict[str, Any], 
                           ai_analysis: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate pattern match score by comparing bug patterns.
        
        Args:
            engineer_analysis: Analysis results from engineer's fix
            ai_analysis: Analysis results from AI's fix
            
        Returns:
            Tuple of (score, details) where:
            - score: float from 0 to 1
            - details: Dictionary with details about the score calculation
        """
        details = {
            "matched_patterns": [],
            "engineer_only": [],
            "ai_only": [],
            "pattern_similarity": 0.0
        }
        
        # Get bug patterns from both analyses
        engineer_patterns = set(engineer_analysis.get("bug_patterns", []))
        ai_patterns = set(ai_analysis.get("bug_patterns", []))
        
        # Find matched and mismatched patterns
        matched_patterns = engineer_patterns.intersection(ai_patterns)
        engineer_only = engineer_patterns - ai_patterns
        ai_only = ai_patterns - engineer_patterns
        
        details["matched_patterns"] = list(matched_patterns)
        details["engineer_only"] = list(engineer_only)
        details["ai_only"] = list(ai_only)
        
        # Calculate Jaccard similarity coefficient for pattern matching
        if not engineer_patterns and not ai_patterns:
            pattern_similarity = 1.0  # Both have no patterns
        elif not engineer_patterns or not ai_patterns:
            pattern_similarity = 0.0  # One has patterns, the other doesn't
        else:
            union_size = len(engineer_patterns.union(ai_patterns))
            intersection_size = len(matched_patterns)
            pattern_similarity = intersection_size / union_size
        
        details["pattern_similarity"] = pattern_similarity
        
        # Use pattern similarity as the score
        score = pattern_similarity
        
        return score, details
    
    def _calc_cleanliness(self, 
                         engineer_analysis: Dict[str, Any], 
                         ai_analysis: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate cleanliness score by evaluating code quality.
        
        Args:
            engineer_analysis: Analysis results from engineer's fix
            ai_analysis: Analysis results from AI's fix
            
        Returns:
            Tuple of (score, details) where:
            - score: float from 0 to 1
            - details: Dictionary with details about the score calculation
        """
        details = {
            "style_issues": [],
            "good_practices": []
        }
        
        # Start with perfect score, deduct for issues
        score = 1.0
        
        # Get changed files from both analyses
        ai_files = [f for f in ai_analysis.get("changed_files", [])]
        
        for file in ai_files:
            file_path = file["path"]
            file_type = file["file_type"]
            changes = file.get("changes", [])
            
            # Check for potential cleanliness issues
            for change in changes:
                if change["type"] != "added" and change["type"] != "modified":
                    continue
                
                content = change["content"]["fixed"] if change["type"] == "modified" else change["content"]
                
                # Check for comment updates
                if "TODO" in content or "FIXME" in content:
                    details["style_issues"].append(f"TODO/FIXME comment in {file_path}")
                    score -= 0.05  # Minor deduction
                
                # Check for long lines (language-specific)
                if len(content) > 100:
                    details["style_issues"].append(f"Long line in {file_path}")
                    score -= 0.02  # Minor deduction
                
                # Language-specific checks
                if file_type == "python":
                    # Python-specific checks
                    if "import *" in content:
                        details["style_issues"].append(f"Wildcard import in {file_path}")
                        score -= 0.10
                elif file_type in ["javascript", "typescript"]:
                    # JavaScript/TypeScript checks
                    if "var " in content:
                        details["style_issues"].append(f"'var' usage in {file_path}")
                        score -= 0.05
        
        # Cap score between 0 and 1
        score = max(0.0, min(1.0, score))
        
        # Add credit for good practices
        if not details["style_issues"]:
            details["good_practices"].append("No style issues detected")
            # Already at max score
        
        return score, details
    
    def _calc_efficiency(self, 
                        engineer_analysis: Dict[str, Any], 
                        ai_analysis: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate efficiency score by comparing solution efficiency.
        
        Args:
            engineer_analysis: Analysis results from engineer's fix
            ai_analysis: Analysis results from AI's fix
            
        Returns:
            Tuple of (score, details) where:
            - score: float from 0 to 1
            - details: Dictionary with details about the score calculation
        """
        details = {
            "line_count_comparison": {},
            "factors": []
        }
        
        # Get changed files from both analyses
        engineer_files = {f["path"]: f for f in engineer_analysis.get("changed_files", [])}
        ai_files = {f["path"]: f for f in ai_analysis.get("changed_files", [])}
        
        # Compare common files
        common_files = set(engineer_files.keys()).intersection(set(ai_files.keys()))
        
        if not common_files:
            # No common files, efficiency cannot be compared
            score = 0.5  # Neutral score
            details["factors"].append("No common files to compare efficiency")
            return score, details
        
        total_ratio = 0.0
        file_count = 0
        
        for file_path in common_files:
            engineer_file = engineer_files[file_path]
            ai_file = ai_files[file_path]
            
            # Count lines changed
            engineer_added = sum(1 for c in engineer_file.get("changes", []) if c["type"] == "added")
            engineer_modified = sum(1 for c in engineer_file.get("changes", []) if c["type"] == "modified")
            engineer_removed = sum(1 for c in engineer_file.get("changes", []) if c["type"] == "removed")
            engineer_total = engineer_added + engineer_modified + engineer_removed
            
            ai_added = sum(1 for c in ai_file.get("changes", []) if c["type"] == "added")
            ai_modified = sum(1 for c in ai_file.get("changes", []) if c["type"] == "modified")
            ai_removed = sum(1 for c in ai_file.get("changes", []) if c["type"] == "removed")
            ai_total = ai_added + ai_modified + ai_removed
            
            file_comparison = {
                "engineer": {
                    "added": engineer_added,
                    "modified": engineer_modified,
                    "removed": engineer_removed,
                    "total": engineer_total
                },
                "ai": {
                    "added": ai_added,
                    "modified": ai_modified,
                    "removed": ai_removed,
                    "total": ai_total
                }
            }
            
            details["line_count_comparison"][file_path] = file_comparison
            
            # Calculate ratio for this file
            if engineer_total > 0 and ai_total > 0:
                # Prefer smaller changes, but not too small (may be incomplete)
                # We aim for AI to be within 20% of engineer's change size
                ratio = min(engineer_total, ai_total) / max(engineer_total, ai_total)
                
                if ai_total < 0.5 * engineer_total:
                    details["factors"].append(f"AI solution for {file_path} is much smaller than reference")
                    ratio = 0.7  # Penalty for being too small (might be incomplete)
                elif ai_total > 2.0 * engineer_total:
                    details["factors"].append(f"AI solution for {file_path} is much larger than reference")
                    ratio = 0.5  # Bigger penalty for being too large (likely inefficient)
                
                total_ratio += ratio
                file_count += 1
        
        # Calculate average ratio
        if file_count > 0:
            score = total_ratio / file_count
        else:
            score = 0.5  # Neutral score
            details["factors"].append("No valid files to compare efficiency")
        
        return score, details
    
    def _calc_complexity(self, 
                        engineer_analysis: Dict[str, Any], 
                        ai_analysis: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate complexity score by comparing solution complexity.
        
        Args:
            engineer_analysis: Analysis results from engineer's fix
            ai_analysis: Analysis results from AI's fix
            
        Returns:
            Tuple of (score, details) where:
            - score: float from 0 to 1
            - details: Dictionary with details about the score calculation
        """
        details = {
            "complexity_comparison": {},
            "factors": []
        }
        
        # Get complexity scores from both analyses
        engineer_complexity = engineer_analysis.get("complexity", {})
        ai_complexity = ai_analysis.get("complexity", {})
        
        engineer_score = engineer_complexity.get("score", 0)
        ai_score = ai_complexity.get("score", 0)
        
        # Record complexity comparison
        details["complexity_comparison"] = {
            "engineer": {
                "score": engineer_score,
                "factors": engineer_complexity.get("factors", [])
            },
            "ai": {
                "score": ai_score,
                "factors": ai_complexity.get("factors", [])
            }
        }
        
        # Calculate complexity ratio
        if engineer_score == 0:
            if ai_score == 0:
                # Both have zero complexity, perfect match
                score = 1.0
            else:
                # Engineer solution has no complexity, but AI does
                score = 0.0
                details["factors"].append("AI solution is more complex than necessary")
        else:
            # Calculate ratio, aiming for AI to be similar or slightly less complex
            ratio = ai_score / engineer_score
            
            if ratio < 0.7:
                # AI solution is much less complex, might be incomplete
                score = 0.7
                details["factors"].append("AI solution may be too simple")
            elif ratio > 1.3:
                # AI solution is more complex, penalize based on how much more
                score = max(0.0, 1.0 - (ratio - 1.0))
                details["factors"].append("AI solution is more complex than reference")
            else:
                # AI solution is similar in complexity, good match
                score = 1.0 - abs(1.0 - ratio)
        
        return score, details
    
    def _compare_file_changes(self, 
                             engineer_file: Dict[str, Any], 
                             ai_file: Dict[str, Any]) -> float:
        """
        Compare changes made to a file by engineer and AI.
        
        Args:
            engineer_file: Analysis for engineer's changes to the file
            ai_file: Analysis for AI's changes to the file
            
        Returns:
            Similarity score from 0 to 1
        """
        # Extract changes from both analyses
        engineer_changes = engineer_file.get("changes", [])
        ai_changes = ai_file.get("changes", [])
        
        # If no changes in reference, but AI changed the file, score is 0
        if not engineer_changes:
            return 0.0
        
        # If no changes in AI, but reference changed the file, score is 0
        if not ai_changes:
            return 0.0
            
        # TODO: Implement more sophisticated comparison of changes
        # This is a simplified version that checks:
        # 1. How many lines overlap between engineer and AI changes
        # 2. How similar the modified content is
        
        # Get line numbers changed by each
        engineer_lines = set()
        for change in engineer_changes:
            if change["type"] == "modified" or change["type"] == "removed":
                line_num = change["line_numbers"].get("bug")
                if line_num:
                    engineer_lines.add(line_num)
        
        ai_lines = set()
        for change in ai_changes:
            if change["type"] == "modified" or change["type"] == "removed":
                line_num = change["line_numbers"].get("bug")
                if line_num:
                    ai_lines.add(line_num)
        
        # Calculate overlap
        common_lines = engineer_lines.intersection(ai_lines)
        union_lines = engineer_lines.union(ai_lines)
        
        if not union_lines:
            return 0.0
            
        line_overlap_score = len(common_lines) / len(union_lines)
        
        # For now, use line overlap as the score
        # In a more sophisticated version, we'd also compare content similarity
        return line_overlap_score
    
    def _generate_comparison(self, 
                            engineer_analysis: Dict[str, Any], 
                            ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed comparison data between engineer and AI solutions.
        
        Args:
            engineer_analysis: Analysis results from engineer's fix
            ai_analysis: Analysis results from AI's fix
            
        Returns:
            Dictionary with comparison data
        """
        comparison = {
            "files": {},
            "summary": {}
        }
        
        # Get files from both analyses
        engineer_files = {f["path"] for f in engineer_analysis.get("changed_files", [])}
        ai_files = {f["path"] for f in ai_analysis.get("changed_files", [])}
        all_files = engineer_files.union(ai_files)
        
        # Categorize files
        common_files = engineer_files.intersection(ai_files)
        engineer_only = engineer_files - ai_files
        ai_only = ai_files - engineer_files
        
        comparison["summary"] = {
            "common_files": len(common_files),
            "engineer_only": len(engineer_only),
            "ai_only": len(ai_only),
            "total_files": len(all_files)
        }
        
        # Compare each file
        for file_path in all_files:
            file_comparison = {
                "in_engineer": file_path in engineer_files,
                "in_ai": file_path in ai_files,
                "engineer_changes": {},
                "ai_changes": {}
            }
            
            # Add engineer's changes if available
            if file_path in engineer_files:
                engineer_file = next((f for f in engineer_analysis.get("changed_files", []) if f["path"] == file_path), None)
                if engineer_file:
                    file_comparison["engineer_changes"] = {
                        "patterns": engineer_file.get("patterns", []),
                        "change_count": len(engineer_file.get("changes", [])),
                        "complexity": engineer_file.get("complexity", {})
                    }
            
            # Add AI's changes if available
            if file_path in ai_files:
                ai_file = next((f for f in ai_analysis.get("changed_files", []) if f["path"] == file_path), None)
                if ai_file:
                    file_comparison["ai_changes"] = {
                        "patterns": ai_file.get("patterns", []),
                        "change_count": len(ai_file.get("changes", [])),
                        "complexity": ai_file.get("complexity", {})
                    }
            
            comparison["files"][file_path] = file_comparison
        
        return comparison
    
    def _identify_strengths(self, metrics: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Identify strengths of the AI solution based on metrics.
        
        Args:
            metrics: Dictionary of metric scores and details
            
        Returns:
            List of identified strengths
        """
        strengths = []
        
        # Check for high-scoring metrics
        for metric_name, metric_data in metrics.items():
            score = metric_data.get("score", 0)
            
            if score >= 0.8:
                # High score, identify as strength
                if metric_name == "correctness":
                    strengths.append("Solution correctly fixes the bug")
                elif metric_name == "completeness":
                    strengths.append("Solution addresses all aspects of the bug")
                elif metric_name == "pattern_match":
                    strengths.append("Solution uses similar fix patterns as reference")
                elif metric_name == "cleanliness":
                    strengths.append("Solution follows good coding practices")
                elif metric_name == "efficiency":
                    strengths.append("Solution is efficient in its approach")
                elif metric_name == "complexity":
                    strengths.append("Solution has appropriate complexity")
        
        return strengths
    
    def _identify_weaknesses(self, metrics: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Identify weaknesses of the AI solution based on metrics.
        
        Args:
            metrics: Dictionary of metric scores and details
            
        Returns:
            List of identified weaknesses
        """
        weaknesses = []
        
        # Check for low-scoring metrics
        for metric_name, metric_data in metrics.items():
            score = metric_data.get("score", 0)
            
            if score < 0.5:
                # Low score, identify as weakness
                if metric_name == "correctness":
                    weaknesses.append("Solution does not correctly fix the bug")
                elif metric_name == "completeness":
                    weaknesses.append("Solution misses aspects of the bug")
                elif metric_name == "pattern_match":
                    weaknesses.append("Solution uses different fix patterns than reference")
                elif metric_name == "cleanliness":
                    weaknesses.append("Solution has code quality issues")
                elif metric_name == "efficiency":
                    weaknesses.append("Solution is not efficient in its approach")
                elif metric_name == "complexity":
                    weaknesses.append("Solution has inappropriate complexity")
        
        return weaknesses
