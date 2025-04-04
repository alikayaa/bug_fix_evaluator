#!/usr/bin/env python
"""
Command-line interface for Bug Fix Cursor Evaluator.

This module provides commands for preparing PRs for evaluation with Cursor agent mode
and processing the results to generate reports.
"""

import os
import sys
import time
import argparse
import logging
import json
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional

from . import __version__
from .cursor_agent import CursorAgentEvaluator
from .results import load_cursor_results, process_results
from .reporter import ReportGenerator
from .utils import setup_logger, is_git_repo, get_local_pr_diff, wait_for_results

logger = logging.getLogger(__name__)

def parse_args():
    """Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Evaluate bug fixes in GitHub pull requests using Cursor agent mode."
    )
    
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Prepare command
    prepare_parser = subparsers.add_parser(
        "prepare", help="Prepare a PR for evaluation with Cursor agent mode"
    )
    prepare_parser.add_argument(
        "pr_url",
        help="URL of the GitHub PR to evaluate",
    )
    prepare_parser.add_argument(
        "--work-dir",
        default=None,
        help="Directory to use for temporary files",
    )
    prepare_parser.add_argument(
        "--output-dir",
        default="./results",
        help="Directory to store evaluation results",
    )
    prepare_parser.add_argument(
        "--github-token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub token for API access",
    )
    prepare_parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout in seconds for waiting for results",
    )
    prepare_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    
    # Prepare local command
    prepare_local_parser = subparsers.add_parser(
        "prepare-local", help="Prepare a PR from a local Git repository for evaluation"
    )
    prepare_local_parser.add_argument(
        "repo_path",
        help="Path to the local Git repository",
    )
    prepare_local_parser.add_argument(
        "pr_number",
        help="PR number to evaluate",
    )
    prepare_local_parser.add_argument(
        "--repo-url",
        default=None,
        help="Repository URL (optional, will try to extract from git remote)",
    )
    prepare_local_parser.add_argument(
        "--work-dir",
        default=None,
        help="Directory to use for temporary files",
    )
    prepare_local_parser.add_argument(
        "--output-dir",
        default="./results",
        help="Directory to store evaluation results",
    )
    prepare_local_parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout in seconds for waiting for results",
    )
    prepare_local_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    
    # Report command
    report_parser = subparsers.add_parser(
        "report", help="Generate a report from evaluation results"
    )
    report_parser.add_argument(
        "results_file",
        help="Path to the results file",
    )
    report_parser.add_argument(
        "--output-dir",
        default="./reports",
        help="Directory to store reports",
    )
    report_parser.add_argument(
        "--format",
        choices=["html", "md", "markdown", "json", "text"],
        default="html",
        help="Report format",
    )
    report_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    
    # Wait command
    wait_parser = subparsers.add_parser(
        "wait", help="Wait for results to be generated"
    )
    wait_parser.add_argument(
        "results_file",
        help="Path to the results file",
    )
    wait_parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout in seconds for waiting for results",
    )
    wait_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    
    # Evaluate command (prepare + wait)
    evaluate_parser = subparsers.add_parser(
        "evaluate", help="Prepare and wait for results in one command"
    )
    evaluate_parser.add_argument(
        "pr_url",
        help="URL of the GitHub PR to evaluate",
    )
    evaluate_parser.add_argument(
        "--work-dir",
        default=None,
        help="Directory to use for temporary files",
    )
    evaluate_parser.add_argument(
        "--output-dir",
        default="./results",
        help="Directory to store evaluation results",
    )
    evaluate_parser.add_argument(
        "--github-token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub token for API access",
    )
    evaluate_parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout in seconds for waiting for results",
    )
    evaluate_parser.add_argument(
        "--report",
        action="store_true",
        help="Generate a report from evaluation results",
    )
    evaluate_parser.add_argument(
        "--report-format",
        choices=["html", "md", "markdown", "json", "text"],
        default="html",
        help="Report format",
    )
    evaluate_parser.add_argument(
        "--report-dir",
        default="./reports",
        help="Directory to store reports",
    )
    evaluate_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    
    # Evaluate local command (prepare-local + wait)
    evaluate_local_parser = subparsers.add_parser(
        "evaluate-local", help="Prepare a local PR and wait for results in one command"
    )
    evaluate_local_parser.add_argument(
        "repo_path",
        help="Path to the local Git repository",
    )
    evaluate_local_parser.add_argument(
        "pr_number",
        help="PR number to evaluate",
    )
    evaluate_local_parser.add_argument(
        "--repo-url",
        default=None,
        help="Repository URL (optional, will try to extract from git remote)",
    )
    evaluate_local_parser.add_argument(
        "--work-dir",
        default=None,
        help="Directory to use for temporary files",
    )
    evaluate_local_parser.add_argument(
        "--output-dir",
        default="./results",
        help="Directory to store evaluation results",
    )
    evaluate_local_parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout in seconds for waiting for results",
    )
    evaluate_local_parser.add_argument(
        "--report",
        action="store_true",
        help="Generate a report from evaluation results",
    )
    evaluate_local_parser.add_argument(
        "--report-format",
        choices=["html", "md", "markdown", "json", "text"],
        default="html",
        help="Report format",
    )
    evaluate_local_parser.add_argument(
        "--report-dir",
        default="./reports",
        help="Directory to store reports",
    )
    evaluate_local_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    return args

def prepare_pr(args):
    """Prepare a PR for evaluation.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        dict: Result info with paths to instruction and results files.
    """
    evaluator = CursorAgentEvaluator(
        work_dir=args.work_dir,
        output_dir=args.output_dir,
        github_token=args.github_token,
        timeout=args.timeout,
        verbose=args.verbose,
    )
    
    result = evaluator.evaluate_pr(args.pr_url)
    
    print("\nPR prepared for evaluation:")
    print(f"Instruction file: {result['instruction_file']}")
    print(f"Expected results file: {result['results_file']}")
    print("\nNext steps:")
    print("1. Open the instruction file in Cursor")
    print("2. Press Cmd+Shift+P to open the command palette")
    print("3. Type and select 'Enable Agent Mode'")
    print("4. Wait for Cursor to evaluate the PR")
    print(f"5. Once done, run: bug-fix-evaluator wait {result['results_file']}")
    
    return result

def prepare_local_pr(args):
    """Prepare a local PR for evaluation.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        dict: Result info with paths to instruction and results files.
    """
    evaluator = CursorAgentEvaluator(
        work_dir=args.work_dir,
        output_dir=args.output_dir,
        timeout=args.timeout,
        verbose=args.verbose,
    )
    
    result = evaluator.evaluate_local_pr(
        args.repo_path, args.pr_number, args.repo_url
    )
    
    print("\nLocal PR prepared for evaluation:")
    print(f"Instruction file: {result['instruction_file']}")
    print(f"Expected results file: {result['results_file']}")
    print("\nNext steps:")
    print("1. Open the instruction file in Cursor")
    print("2. Press Cmd+Shift+P to open the command palette")
    print("3. Type and select 'Enable Agent Mode'")
    print("4. Wait for Cursor to evaluate the PR")
    print(f"5. Once done, run: bug-fix-evaluator wait {result['results_file']}")
    
    return result

def wait_for_results(args):
    """Wait for results to be generated.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        dict: The results loaded from the file.
    """
    from .utils import wait_for_results as wait_func
    
    print(f"Waiting for results file: {args.results_file}")
    results = wait_func(args.results_file, timeout=args.timeout)
    
    print("\nResults received:")
    overall_score = results.get("overall", "N/A")
    print(f"Overall score: {overall_score}/100")
    
    return results

def generate_report(results_file, output_dir="./reports", report_format="html", verbose=False):
    """Generate a report from evaluation results.
    
    Args:
        results_file: Path to the results file.
        output_dir: Directory to store reports.
        report_format: Report format.
        verbose: Whether to enable verbose logging.
        
    Returns:
        str: Path to the generated report.
    """
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logger = setup_logger(level=level)
    
    # Load and process results
    results = load_cursor_results(results_file)
    processed_data = process_results(results)
    
    # Generate report
    reporter = ReportGenerator(output_dir=output_dir)
    report_path = reporter.generate_report(processed_data, format=report_format)
    
    print(f"\nReport generated at: {report_path}")
    return report_path

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Configure logging
    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logger = setup_logger(level=level)
    
    try:
        if args.command == "prepare":
            prepare_pr(args)
        
        elif args.command == "prepare-local":
            prepare_local_pr(args)
        
        elif args.command == "wait":
            results = wait_for_results(args)
            print("\nTo generate a report, run:")
            print(f"bug-fix-evaluator report {args.results_file} --format html")
        
        elif args.command == "report":
            generate_report(
                args.results_file,
                output_dir=args.output_dir,
                report_format=args.format,
                verbose=args.verbose,
            )
        
        elif args.command == "evaluate":
            result = prepare_pr(args)
            print("\nWaiting for results...")
            results = wait_for_results(args)
            
            if args.report:
                generate_report(
                    result["results_file"],
                    output_dir=args.report_dir,
                    report_format=args.report_format,
                    verbose=args.verbose,
                )
        
        elif args.command == "evaluate-local":
            result = prepare_local_pr(args)
            print("\nWaiting for results...")
            results = wait_for_results(args)
            
            if args.report:
                generate_report(
                    result["results_file"],
                    output_dir=args.report_dir,
                    report_format=args.report_format,
                    verbose=args.verbose,
                )
    
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 