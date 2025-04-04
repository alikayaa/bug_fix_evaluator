#!/usr/bin/env python3
"""
Example script for evaluating bug fixes from GitHub Pull Requests.

This script demonstrates how to use the Bug Fix Evaluator API to compare
bug fixes from engineer and AI developers using GitHub PR URLs.
"""

import os
import sys
import argparse
import logging

# Add the parent directory to the path to import the bug_fix_evaluator package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.bug_fix_evaluator.core import BugFixEvaluator

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Evaluate bug fixes by comparing GitHub Pull Requests"
    )
    parser.add_argument('--engineer', help='Engineer\'s PR URL')
    parser.add_argument('--ai', help='AI\'s PR URL')
    parser.add_argument('--format', choices=['json', 'html', 'text', 'markdown'], default='html',
                    help='Format of the report (default: html)')
    parser.add_argument('--output', help='Output path for the report')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    return parser.parse_args()

def main():
    """Main entry point for the example script."""
    args = parse_args()
    
    # Use default PRs if not provided
    engineer_pr = args.engineer or "https://github.com/alikayaa/bug_fix_evaluator/pull/123"
    ai_pr = args.ai or "https://github.com/alikayaa/bug_fix_evaluator/pull/456"
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create a configuration dictionary
    config = {
        'log_level': 'DEBUG' if args.verbose else 'INFO',
        'metrics': {
            'weight_correctness': 0.30,
            'weight_completeness': 0.15,
            'weight_pattern_match': 0.10,
            'weight_cleanliness': 0.15,
            'weight_efficiency': 0.15,
            'weight_complexity': 0.15
        },
        'report': {
            'output_dir': 'reports'
        }
    }
    
    try:
        # Create the evaluator
        evaluator = BugFixEvaluator(config)
        
        print(f"Evaluating bug fixes from PRs:")
        print(f"Engineer: {engineer_pr}")
        print(f"AI: {ai_pr}")
        
        # Evaluate the bug fixes
        result = evaluator.evaluate_from_pull_requests(
            engineer_pr_url=engineer_pr,
            ai_pr_url=ai_pr,
            report_format=args.format
        )
        
        # If output path is specified, rename the report file
        if args.output and 'report_path' in result:
            original_path = result['report_path']
            try:
                import shutil
                shutil.move(original_path, args.output)
                print(f"Report saved to {args.output}")
                result['report_path'] = args.output
            except (IOError, OSError) as e:
                print(f"Error saving report to {args.output}: {e}")
        
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
        logging.error(f"Error during evaluation: {e}", exc_info=args.verbose)
        return 1
    finally:
        # Clean up resources
        if 'evaluator' in locals():
            evaluator.cleanup()

if __name__ == '__main__':
    sys.exit(main()) 