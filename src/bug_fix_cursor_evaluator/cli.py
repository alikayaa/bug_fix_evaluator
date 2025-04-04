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
    prepare_parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Disable automatic cleanup of temporary files",
    )
    prepare_parser.add_argument(
        "--open-cursor",
        action="store_true",
        help="Open the instructions file in Cursor",
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
    prepare_local_parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Disable automatic cleanup of temporary files",
    )
    prepare_local_parser.add_argument(
        "--open-cursor",
        action="store_true",
        help="Open the instructions file in Cursor",
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
    report_parser.add_argument(
        "--open",
        action="store_true",
        help="Open the report in a web browser",
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
    wait_parser.add_argument(
        "--report",
        action="store_true",
        help="Generate a report from evaluation results",
    )
    wait_parser.add_argument(
        "--format",
        choices=["html", "md", "markdown", "json", "text"],
        default="html",
        help="Report format",
    )
    wait_parser.add_argument(
        "--report-dir",
        default="./reports",
        help="Directory to store reports",
    )
    wait_parser.add_argument(
        "--open",
        action="store_true",
        help="Open the report in a web browser",
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
    evaluate_parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Disable automatic cleanup of temporary files",
    )
    evaluate_parser.add_argument(
        "--open-cursor",
        action="store_true",
        help="Open the instructions file in Cursor",
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
    evaluate_local_parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Disable automatic cleanup of temporary files",
    )
    evaluate_local_parser.add_argument(
        "--open-cursor",
        action="store_true",
        help="Open the instructions file in Cursor",
    )
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    return args

def prepare_pr(args):
    """Prepare a PR for evaluation"""
    try:
        evaluator = CursorAgentEvaluator(
            work_dir=args.work_dir,
            output_dir=args.output_dir,
            github_token=args.github_token,
            timeout=args.timeout,
            verbose=args.verbose,
            auto_cleanup=not args.no_cleanup,
        )
        
        result = evaluator.evaluate_pr(args.pr_url)
        
        # Print clear instructions for the user
        print("\n" + "="*80)
        print("🔍 Bug Fix Evaluator - Next Steps 🔍".center(80))
        print("="*80)
        print("\n1. Open the instructions file in Cursor:")
        print(f"   {result['instructions_file']}")
        print("\n2. Enable Agent Mode in Cursor:")
        print("   Press Cmd+Shift+P (macOS) or Ctrl+Shift+P (Windows/Linux)")
        print("   Type 'Enable Agent Mode' and select it")
        print("\n3. Ask the agent to evaluate the PR:")
        print("   Type: \"Please evaluate this PR based on the instructions in this file\"")
        print("\n4. The agent will analyze the diff file referenced in the instructions")
        print("   and provide an evaluation with scores and explanations")
        print("\n5. Save the evaluation results as a JSON file at:")
        print(f"   {result['results_file']}")
        print("\n6. Once the results are saved, generate a report with:")
        print(f"   bug-fix-evaluator report {result['results_file']} --format html --open")
        print("\n7. Or wait for results and generate a report in one step:")
        print(f"   bug-fix-evaluator wait {result['results_file']} --report --format html --open")
        print("="*80)
        
        # Offer to open in Cursor if requested
        if args.open_cursor:
            try:
                evaluator.open_in_cursor(result["instructions_file"])
                print("\n✅ Opened instructions file in Cursor.")
                print("   Please follow the steps above to complete the evaluation.")
            except Exception as e:
                logger.error(f"Failed to open in Cursor: {e}")
                print("\n⚠️ Failed to open in Cursor. Please open the file manually.")
        
        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            logger.debug(traceback.format_exc())
        sys.exit(1)

def prepare_local_pr(args):
    """Prepare a local PR for evaluation.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        dict: Result info with paths to instruction and results files.
    """
    try:
        evaluator = CursorAgentEvaluator(
            work_dir=args.work_dir,
            output_dir=args.output_dir,
            github_token=args.github_token,
            timeout=args.timeout,
            verbose=args.verbose,
            auto_cleanup=not args.no_cleanup,
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
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            logger.debug(traceback.format_exc())
        sys.exit(1)

def wait_for_results(args):
    """Wait for results to be generated"""
    try:
        print(f"\n⏳ Waiting for results to be saved to: {args.results_file}")
        print(f"   Timeout: {args.timeout} seconds")
        print(f"\n   Tip: Have you completed steps 1-5 in the instructions?")
        print(f"   In Agent Mode, ask: \"Please evaluate this PR based on the instructions in this file\"")
        print(f"   Then save the results to: {args.results_file}")
        
        # Create evaluator just for waiting
        evaluator = CursorAgentEvaluator(
            output_dir=os.path.dirname(args.results_file),
            timeout=args.timeout,
            verbose=args.verbose,
            auto_cleanup=False,  # Don't clean up when just waiting
        )
        
        # Wait for results
        results = evaluator.wait_for_results(args.results_file)
        
        print(f"\n✅ Results received!")
        if results.get("overall"):
            print(f"\n📊 Overall score: {results['overall']}/100")
        
        # Generate report if requested
        if args.report:
            report_path = generate_report(args.results_file, args.format, args.report_dir, args.verbose)
            print(f"\n📄 Report generated: {report_path}")
            
            if args.open:
                try:
                    webbrowser.open(f"file://{report_path}")
                    print(f"   Opened report in browser.")
                except Exception as e:
                    logger.error(f"Failed to open report: {e}")
                    print(f"   Failed to open report. Please open it manually.")
        
        return results
    except TimeoutError:
        logger.error(f"Timeout waiting for results after {args.timeout} seconds")
        print(f"\n⚠️ Timeout waiting for results!")
        print(f"   Make sure the agent has completed the evaluation and saved the results to:")
        print(f"   {args.results_file}")
        print(f"\n   You can try again with a longer timeout:")
        print(f"   bug-fix-evaluator wait {args.results_file} --timeout 1800")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error waiting for results: {e}")
        if args.verbose:
            import traceback
            logger.debug(traceback.format_exc())
        sys.exit(1)

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