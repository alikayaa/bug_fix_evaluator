"""
Cursor integration adapter for Bug Fix Evaluator.

This module provides an adapter for integrating the Bug Fix Evaluator with Cursor.
"""

import json
import logging
import sys
from typing import Dict, Any

from ..core import BugFixEvaluator

logger = logging.getLogger(__name__)

def cursor_evaluate_from_commits(
    repo_path: str,
    engineer_before_commit: str,
    engineer_after_commit: str,
    ai_before_commit: str,
    ai_after_commit: str,
    report_format: str = 'html',
    config_path: str = None,
    output_dir: str = None
) -> Dict[str, Any]:
    """
    Evaluate bug fixes from Git commits for Cursor integration.
    
    Args:
        repo_path: Path to the Git repository
        engineer_before_commit: SHA of the commit before the engineer's fix
        engineer_after_commit: SHA of the commit after the engineer's fix
        ai_before_commit: SHA of the commit before the AI's fix
        ai_after_commit: SHA of the commit after the AI's fix
        report_format: Format of the report ('html', 'json', 'text', or 'markdown')
        config_path: Path to the configuration file
        output_dir: Directory for storing evaluation reports
        
    Returns:
        A dictionary with the evaluation results
    """
    try:
        # Create configuration
        config = {}
        if config_path:
            from ..utils.config import load_config
            config = load_config(config_path)
        
        # Set output directory if provided
        if output_dir:
            if 'report' not in config:
                config['report'] = {}
            config['report']['output_dir'] = output_dir
        
        # Create evaluator
        evaluator = BugFixEvaluator(config)
        
        # Run evaluation
        result = evaluator.evaluate_from_commits(
            repo_path=repo_path,
            engineer_before_commit=engineer_before_commit,
            engineer_after_commit=engineer_after_commit,
            ai_before_commit=ai_before_commit,
            ai_after_commit=ai_after_commit,
            report_format=report_format
        )
        
        # Output result in a format Cursor can parse
        print(f"RESULT_JSON_START{json.dumps(result)}RESULT_JSON_END")
        
        return result
    except Exception as e:
        logger.error(f"Error in cursor_evaluate_from_commits: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}", file=sys.stderr)
        raise

def cursor_evaluate_from_directories(
    engineer_buggy_dir: str,
    engineer_fixed_dir: str,
    ai_buggy_dir: str,
    ai_fixed_dir: str,
    report_format: str = 'html',
    config_path: str = None,
    output_dir: str = None
) -> Dict[str, Any]:
    """
    Evaluate bug fixes from directories for Cursor integration.
    
    Args:
        engineer_buggy_dir: Directory with engineer's buggy code
        engineer_fixed_dir: Directory with engineer's fixed code
        ai_buggy_dir: Directory with AI's buggy code
        ai_fixed_dir: Directory with AI's fixed code
        report_format: Format of the report ('html', 'json', 'text', or 'markdown')
        config_path: Path to the configuration file
        output_dir: Directory for storing evaluation reports
        
    Returns:
        A dictionary with the evaluation results
    """
    try:
        # Create configuration
        config = {}
        if config_path:
            from ..utils.config import load_config
            config = load_config(config_path)
        
        # Set output directory if provided
        if output_dir:
            if 'report' not in config:
                config['report'] = {}
            config['report']['output_dir'] = output_dir
        
        # Create evaluator
        evaluator = BugFixEvaluator(config)
        
        # Run evaluation
        result = evaluator.evaluate_from_directories(
            engineer_buggy_dir=engineer_buggy_dir,
            engineer_fixed_dir=engineer_fixed_dir,
            ai_buggy_dir=ai_buggy_dir,
            ai_fixed_dir=ai_fixed_dir,
            report_format=report_format
        )
        
        # Output result in a format Cursor can parse
        print(f"RESULT_JSON_START{json.dumps(result)}RESULT_JSON_END")
        
        return result
    except Exception as e:
        logger.error(f"Error in cursor_evaluate_from_directories: {str(e)}", exc_info=True)
        print(f"ERROR: {str(e)}", file=sys.stderr)
        raise

def main():
    """
    Main entry point for the Cursor adapter CLI.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Bug Fix Evaluator Cursor Adapter"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Evaluate from commits command
    commits_parser = subparsers.add_parser(
        "commits", help="Evaluate bug fixes from Git commits"
    )
    commits_parser.add_argument("--repo-path", required=True, help="Path to the Git repository")
    commits_parser.add_argument("--engineer-before", required=True, help="Engineer's code before fix (commit SHA)")
    commits_parser.add_argument("--engineer-after", required=True, help="Engineer's code after fix (commit SHA)")
    commits_parser.add_argument("--ai-before", required=True, help="AI's code before fix (commit SHA)")
    commits_parser.add_argument("--ai-after", required=True, help="AI's code after fix (commit SHA)")
    commits_parser.add_argument("--format", choices=["html", "json", "text", "markdown"], default="html", help="Report format")
    commits_parser.add_argument("--config", help="Path to configuration file")
    commits_parser.add_argument("--output-dir", help="Directory for storing evaluation reports")
    
    # Evaluate from directories command
    dirs_parser = subparsers.add_parser(
        "directories", help="Evaluate bug fixes from directories"
    )
    dirs_parser.add_argument("--engineer-buggy", required=True, help="Directory with engineer's buggy code")
    dirs_parser.add_argument("--engineer-fixed", required=True, help="Directory with engineer's fixed code")
    dirs_parser.add_argument("--ai-buggy", required=True, help="Directory with AI's buggy code")
    dirs_parser.add_argument("--ai-fixed", required=True, help="Directory with AI's fixed code")
    dirs_parser.add_argument("--format", choices=["html", "json", "text", "markdown"], default="html", help="Report format")
    dirs_parser.add_argument("--config", help="Path to configuration file")
    dirs_parser.add_argument("--output-dir", help="Directory for storing evaluation reports")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    if args.command == "commits":
        cursor_evaluate_from_commits(
            repo_path=args.repo_path,
            engineer_before_commit=args.engineer_before,
            engineer_after_commit=args.engineer_after,
            ai_before_commit=args.ai_before,
            ai_after_commit=args.ai_after,
            report_format=args.format,
            config_path=args.config,
            output_dir=args.output_dir
        )
    elif args.command == "directories":
        cursor_evaluate_from_directories(
            engineer_buggy_dir=args.engineer_buggy,
            engineer_fixed_dir=args.engineer_fixed,
            ai_buggy_dir=args.ai_buggy,
            ai_fixed_dir=args.ai_fixed,
            report_format=args.format,
            config_path=args.config,
            output_dir=args.output_dir
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 