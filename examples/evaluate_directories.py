#!/usr/bin/env python3
"""
Example script for evaluating bug fixes by comparing directories.

This script demonstrates how to use the Bug Fix Evaluator API to compare
bug fixes from engineer and AI developers using directories with before/after code.
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
        description="Evaluate bug fixes by comparing directories"
    )
    parser.add_argument('--engineer-buggy', required=True, 
                        help='Directory with engineer\'s buggy code')
    parser.add_argument('--engineer-fixed', required=True, 
                        help='Directory with engineer\'s fixed code')
    parser.add_argument('--ai-buggy', required=True, 
                        help='Directory with AI\'s buggy code')
    parser.add_argument('--ai-fixed', required=True, 
                        help='Directory with AI\'s fixed code')
    parser.add_argument('--format', choices=['json', 'html', 'text', 'markdown'], default='html',
                    help='Format of the report (default: html)')
    parser.add_argument('--output', help='Output path for the report')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    return parser.parse_args()

def main():
    """Main entry point for the example script."""
    args = parse_args()
    
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
            'weight_correctness': 0.35,
            'weight_completeness': 0.15,
            'weight_pattern_match': 0.10,
            'weight_cleanliness': 0.15,
            'weight_efficiency': 0.10,
            'weight_complexity': 0.15
        },
        'report': {
            'output_dir': 'reports'
        }
    }
    
    try:
        # Create the evaluator
        evaluator = BugFixEvaluator(config)
        
        print("Evaluating bug fixes from directories:")
        print(f"Engineer: {args.engineer_buggy} -> {args.engineer_fixed}")
        print(f"AI: {args.ai_buggy} -> {args.ai_fixed}")
        
        # Evaluate the bug fixes
        result = evaluator.evaluate_from_directories(
            engineer_buggy_dir=args.engineer_buggy,
            engineer_fixed_dir=args.engineer_fixed,
            ai_buggy_dir=args.ai_buggy,
            ai_fixed_dir=args.ai_fixed,
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