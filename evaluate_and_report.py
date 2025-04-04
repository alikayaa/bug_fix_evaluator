#!/usr/bin/env python3
"""
Evaluate PR and Generate Report Automation

This script automates:
1. Setting up a PR for evaluation
2. Opening the instructions in Cursor
3. Watching for the results file
4. Generating a report when the results are available
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate a PR and automatically generate a report")
    parser.add_argument("pr_url", help="URL of the GitHub PR to evaluate")
    parser.add_argument("--format", default="html", choices=["html", "markdown", "json", "text"], 
                        help="Report format (default: html)")
    parser.add_argument("--output-dir", default="./reports", help="Directory to store reports (default: ./reports)")
    parser.add_argument("--open-report", action="store_true", help="Open the report in a browser when done")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    return parser.parse_args()

def main():
    args = parse_args()
    
    print(f"Starting evaluation for PR: {args.pr_url}")
    
    # Step 1: Prepare the PR for evaluation
    print("\n--- Step 1: Preparing PR for evaluation ---")
    prepare_cmd = ["bug-fix-evaluator", "prepare", args.pr_url]
    if args.verbose:
        prepare_cmd.append("--verbose")
    
    result = subprocess.run(prepare_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error preparing PR: {result.stderr}")
        sys.exit(1)
    
    # Parse the output to get the instructions and results file paths
    output_lines = result.stdout.strip().split('\n')
    instructions_file = None
    results_file = None
    
    for line in output_lines:
        if "Instructions file:" in line:
            instructions_file = line.split("Instructions file:")[-1].strip()
        if "Results will be saved to:" in line:
            results_file = line.split("Results will be saved to:")[-1].strip()
    
    if not instructions_file or not results_file:
        print("Failed to extract instructions or results file paths")
        sys.exit(1)
    
    print(f"Instructions file: {instructions_file}")
    print(f"Results will be saved to: {results_file}")
    
    # Step 2: Open the instructions in Cursor
    print("\n--- Step 2: Opening instructions in Cursor ---")
    print("Please follow these steps in Cursor:")
    print("1. Enable Agent Mode (Cmd+Shift+P or Ctrl+Shift+P, then 'Enable Agent Mode')")
    print("2. Ask the agent: \"Please evaluate this PR based on the instructions in this file and save the results to the exact file path specified\"")
    
    cursor_cmd = ["cursor", instructions_file]
    subprocess.Popen(cursor_cmd)
    
    # Step 3: Wait for results and generate report
    print("\n--- Step 3: Waiting for evaluation results ---")
    print("The Cursor agent is evaluating the PR. This may take a few minutes.")
    print("When the evaluation is complete, a report will be automatically generated.")
    
    # Start the auto_generate_report.py script
    watch_cmd = [
        "./auto_generate_report.py",
        results_file,
        "--format", args.format,
        "--output-dir", args.output_dir
    ]
    
    if args.open_report:
        watch_cmd.append("--open")
    
    watch_process = subprocess.run(watch_cmd)
    if watch_process.returncode != 0:
        print("Error watching for results or generating report")
        sys.exit(1)
    
    print("\n--- Evaluation and reporting complete! ---")

if __name__ == "__main__":
    main() 