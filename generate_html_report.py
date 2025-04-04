#!/usr/bin/env python3
"""
Script to generate HTML evaluation reports from JSON report files.
"""
import os
import sys
import json
import argparse
from datetime import datetime

def read_template():
    """Read the HTML template file."""
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_report.html")
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        sys.exit(1)
    
    with open(template_path, 'r') as f:
        template = f.read()
    
    return template

def read_report(report_path):
    """Read the JSON evaluation report."""
    try:
        with open(report_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading report file: {e}")
        sys.exit(1)

def generate_html_report(report_data, output_path):
    """Generate HTML report from JSON data."""
    # Load the template
    template = read_template()
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Update the template with report data instead of loading it dynamically
    # This allows the HTML to be self-contained without needing to fetch data
    modified_template = template.replace(
        "// Run on page load - try to load from a parameter or use demo data",
        f"// Report data embedded directly\nconst reportData = {json.dumps(report_data, indent=2)};"
    ).replace(
        "if (reportPath) {\n                loadReportData(reportPath);\n            } else {\n                loadDemoData();\n            }",
        "renderReport(reportData);"
    )
    
    # Write the HTML file
    with open(output_path, 'w') as f:
        f.write(modified_template)
    
    print(f"HTML report generated at: {output_path}")
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Generate HTML evaluation reports from JSON files")
    parser.add_argument("report", help="Path to the JSON evaluation report")
    parser.add_argument("--output", "-o", help="Output HTML file path", 
                       default="evaluation_report.html")
    
    args = parser.parse_args()
    
    # Read the evaluation report
    report_data = read_report(args.report)
    
    # Generate HTML report
    html_path = generate_html_report(report_data, args.output)
    
    print(f"Report generated successfully!")
    print(f"You can open it in your browser: file://{os.path.abspath(html_path)}")

if __name__ == "__main__":
    main() 