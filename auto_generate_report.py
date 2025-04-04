#!/usr/bin/env python3
"""
Auto Report Generator for Bug Fix Evaluator

This script watches for the creation of the evaluation JSON file and 
automatically generates a report when it's available.
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Automatically generate a report when the evaluation JSON is created")
    parser.add_argument("results_file", help="Path to the results file to watch for")
    parser.add_argument("--format", default="html", choices=["html", "markdown", "json", "text"], 
                        help="Report format (default: html)")
    parser.add_argument("--output-dir", default="./reports", help="Directory to store reports (default: ./reports)")
    parser.add_argument("--open", action="store_true", help="Open the report in a browser when done")
    parser.add_argument("--check-interval", type=int, default=2, help="Seconds between checks (default: 2)")
    parser.add_argument("--timeout", type=int, default=3600, help="Maximum seconds to wait (default: 3600)")
    return parser.parse_args()

def wait_for_file_and_generate_report(results_file, report_format, output_dir, open_report, check_interval, timeout):
    """
    Wait for the specified file to be created, then generate a report.
    
    Args:
        results_file: Path to the results file to watch for
        report_format: Format for the report
        output_dir: Directory to save the report
        open_report: Whether to open the report after generation
        check_interval: Seconds between checks
        timeout: Maximum seconds to wait
    """
    results_path = Path(results_file)
    start_time = time.time()
    
    print(f"Watching for file: {results_path}")
    print(f"Will generate {report_format} report in {output_dir} when available")
    
    while time.time() - start_time < timeout:
        if results_path.exists():
            # Give the file a moment to be fully written
            time.sleep(1)
            
            print(f"\nFile detected! Generating report...")
            
            cmd = ["bug-fix-evaluator", "report", str(results_path), 
                   "--format", report_format, "--output-dir", output_dir]
            
            if open_report:
                cmd.append("--open")
                
            try:
                subprocess.run(cmd, check=True)
                print("\nReport generation complete!")
                return True
            except subprocess.CalledProcessError as e:
                print(f"\nError generating report: {e}")
                return False
                
        # Wait before checking again
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(check_interval)
        
    print(f"\nTimeout after waiting {timeout} seconds")
    return False

if __name__ == "__main__":
    args = parse_args()
    success = wait_for_file_and_generate_report(
        args.results_file,
        args.format,
        args.output_dir,
        args.open,
        args.check_interval,
        args.timeout
    )
    
    sys.exit(0 if success else 1) 