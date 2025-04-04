"""
Command-line interface for Bug Fix Evaluator.

This module provides the CLI interface for the Bug Fix Evaluator tool.
"""

import os
import sys
import argparse
import logging
import json
from typing import Dict, List, Optional, Any, Union

from .core import BugFixEvaluator

logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Evaluate bug fixes by comparing engineer and AI solutions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate from PR URLs
  bug-fix-evaluator pr --engineer https://github.com/alikayaa/bug_fix_evaluator/pull/123 --ai https://github.com/alikayaa/bug_fix_evaluator/pull/456
        
  # Evaluate from commit SHAs
  bug-fix-evaluator commit --repo https://github.com/alikayaa/bug_fix_evaluator.git --engineer abc123 --ai def456
        
  # Evaluate from directories
  bug-fix-evaluator directory --engineer-buggy ./engineer/buggy --engineer-fixed ./engineer/fixed --ai-buggy ./ai/buggy --ai-fixed ./ai/fixed
        
  # Evaluate from patch files
  bug-fix-evaluator patch --engineer ./engineer.patch --ai ./ai.patch
        """
    )
    
    # Add common arguments
    parser.add_argument('-c', '--config', help='Path to configuration file')
    parser.add_argument('-o', '--output', help='Output path for the report')
    parser.add_argument('-f', '--format', choices=['json', 'html', 'text', 'markdown'], default='html',
                        help='Format of the report (default: html)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    # Create subparsers for different evaluation methods
    subparsers = parser.add_subparsers(dest='command', help='Evaluation method')
    
    # PR evaluation
    pr_parser = subparsers.add_parser('pr', help='Evaluate from PR URLs')
    pr_parser.add_argument('--engineer', required=True, help='URL to the engineer\'s PR')
    pr_parser.add_argument('--ai', required=True, help='URL to the AI\'s PR')
    
    # Commit evaluation
    commit_parser = subparsers.add_parser('commit', help='Evaluate from commit SHAs')
    commit_parser.add_argument('--repo', required=True, help='URL to the git repository')
    commit_parser.add_argument('--engineer', required=True, help='SHA of the engineer\'s bug fix commit')
    commit_parser.add_argument('--ai', required=True, help='SHA of the AI\'s bug fix commit')
    
    # Directory evaluation
    dir_parser = subparsers.add_parser('directory', help='Evaluate from directories')
    dir_parser.add_argument('--engineer-buggy', required=True, help='Directory with engineer\'s buggy code')
    dir_parser.add_argument('--engineer-fixed', required=True, help='Directory with engineer\'s fixed code')
    dir_parser.add_argument('--ai-buggy', required=True, help='Directory with AI\'s buggy code')
    dir_parser.add_argument('--ai-fixed', required=True, help='Directory with AI\'s fixed code')
    
    # Patch evaluation
    patch_parser = subparsers.add_parser('patch', help='Evaluate from patch files')
    patch_parser.add_argument('--engineer', required=True, help='Path to engineer\'s patch file')
    patch_parser.add_argument('--ai', required=True, help='Path to AI\'s patch file')
    patch_parser.add_argument('--repo', help='URL to the git repository for context')
    patch_parser.add_argument('--base', help='Base commit to apply patches to')
    
    return parser.parse_args()

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary with configuration settings
    """
    config = {}
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
    
    return config

def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    args = parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    config = load_config(args.config)
    
    if args.verbose:
        config['log_level'] = 'DEBUG'
    
    # Create evaluator
    evaluator = BugFixEvaluator(config)
    
    try:
        # Execute the appropriate command
        if args.command == 'pr':
            result = evaluator.evaluate_from_pr(
                engineer_pr_url=args.engineer,
                ai_pr_url=args.ai,
                report_format=args.format
            )
        elif args.command == 'commit':
            result = evaluator.evaluate_from_commits(
                repo_url=args.repo,
                engineer_commit=args.engineer,
                ai_commit=args.ai,
                report_format=args.format
            )
        elif args.command == 'directory':
            result = evaluator.evaluate_from_directories(
                engineer_buggy_dir=args.engineer_buggy,
                engineer_fixed_dir=args.engineer_fixed,
                ai_buggy_dir=args.ai_buggy,
                ai_fixed_dir=args.ai_fixed,
                report_format=args.format
            )
        elif args.command == 'patch':
            result = evaluator.evaluate_from_patch_files(
                engineer_patch_file=args.engineer,
                ai_patch_file=args.ai,
                repo_url=args.repo,
                base_commit=args.base,
                report_format=args.format
            )
        else:
            logger.error("No command specified. Use --help for usage information.")
            return 1
        
        # If output path is specified, rename the report file
        if args.output and 'report_path' in result:
            original_path = result['report_path']
            try:
                import shutil
                shutil.move(original_path, args.output)
                logger.info(f"Report saved to {args.output}")
                result['report_path'] = args.output
            except (IOError, OSError) as e:
                logger.error(f"Error saving report to {args.output}: {e}")
        
        # Print result summary
        print(f"\nEvaluation completed with overall score: {result.get('overall_score', 0):.1f}%")
        print(f"Report saved to: {result.get('report_path', 'unknown')}")
        
        if args.verbose:
            print("\nStrengths:")
            for strength in result.get('strengths', []):
                print(f"* {strength}")
            
            print("\nWeaknesses:")
            for weakness in result.get('weaknesses', []):
                print(f"* {weakness}")
        
        return 0
    except Exception as e:
        logger.error(f"Error during evaluation: {e}", exc_info=args.verbose)
        return 1
    finally:
        # Clean up resources
        evaluator.cleanup()

if __name__ == '__main__':
    sys.exit(main())
