"""
Results processing module for Bug Fix Cursor Evaluator.

This module provides functionality for loading and processing evaluation results
from Cursor agent evaluations.
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_cursor_results(file_path: str) -> Dict[str, Any]:
    """
    Load and validate results from a Cursor agent evaluation.
    
    Args:
        file_path: Path to the results file
        
    Returns:
        Dictionary with evaluation results
        
    Raises:
        ValueError: If the file is invalid or missing required fields
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Validate the structure of the results
        if "repository" not in data:
            raise ValueError("Missing 'repository' field in results")
            
        if "pr_number" not in data:
            raise ValueError("Missing 'pr_number' field in results")
            
        if "criteria" not in data:
            raise ValueError("Missing 'criteria' field in results")
            
        if "overall" not in data:
            raise ValueError("Missing 'overall' field in results")
            
        # Check that criteria contains all required metrics
        required_metrics = [
            "correctness", "completeness", "code_quality",
            "efficiency", "testing", "documentation"
        ]
        
        for metric in required_metrics:
            if metric not in data["criteria"]:
                raise ValueError(f"Missing evaluation criteria: {metric}")
                
            # Each metric should have score, explanation, strength, and weakness
            metric_data = data["criteria"][metric]
            for field in ["score", "explanation", "strength", "weakness"]:
                if field not in metric_data:
                    raise ValueError(f"Missing {field} for metric {metric}")
        
        # Handle case where overall is an integer instead of a dictionary
        if isinstance(data["overall"], int):
            # Convert overall to expected dictionary format
            overall_score = data["overall"]
            
            # Extract strengths, weaknesses, and suggestions if available
            strengths = data.get("strengths", [])
            weaknesses = data.get("weaknesses", [])
            suggestions = data.get("suggestions", [])
            
            # Create proper overall structure
            data["overall"] = {
                "score": overall_score / 10,  # Convert to 0-10 scale
                "strengths": strengths,
                "weaknesses": weaknesses,
                "suggestions": suggestions
            }
            
            logger.info("Converted overall integer to dictionary format")
        else:
            # Check overall structure
            for field in ["score", "strengths", "weaknesses", "suggestions"]:
                if field not in data["overall"]:
                    raise ValueError(f"Missing {field} in overall assessment")
                    
        logger.info(f"Successfully loaded and validated evaluation results from {file_path}")
        return data
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in results file: {e}")
    except IOError as e:
        raise ValueError(f"Could not read results file: {e}")

def process_results(results_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the Cursor agent results into a format suitable for the reporter.
    
    Args:
        results_data: Results data from Cursor agent
        
    Returns:
        Processed data for the report generator
    """
    # Extract PR information
    pr_info = {
        "repo_name": results_data["repository"],
        "pr_number": results_data["pr_number"],
        "pr_url": f"https://github.com/{results_data['repository']}/pull/{results_data['pr_number']}"
    }
    
    # Extract metrics
    metrics = {}
    for metric_name, metric_data in results_data["criteria"].items():
        metrics[metric_name] = {
            "score": metric_data["score"],
            "weight": get_metric_weight(metric_name),
            "details": {
                "explanation": metric_data["explanation"],
                "strength": metric_data["strength"],
                "weakness": metric_data["weakness"]
            }
        }
    
    # Create processed data structure
    processed_data = {
        "overall_score": results_data["overall"]["score"] * 10,  # Convert 0-10 to 0-100
        "metrics": metrics,
        "strengths": results_data["overall"]["strengths"],
        "weaknesses": results_data["overall"]["weaknesses"],
        "suggestions": results_data["overall"]["suggestions"]
    }
    
    # Add PR info
    processed_data.update(pr_info)
    
    logger.info("Successfully processed evaluation results")
    return processed_data

def get_metric_weight(metric_name: str) -> float:
    """
    Get the default weight for a metric.
    
    Args:
        metric_name: Name of the metric
        
    Returns:
        Weight value between 0 and 1
    """
    weights = {
        "correctness": 0.30,
        "completeness": 0.15,
        "code_quality": 0.15,
        "efficiency": 0.15,
        "testing": 0.10,
        "documentation": 0.15
    }
    
    return weights.get(metric_name, 0.1) 