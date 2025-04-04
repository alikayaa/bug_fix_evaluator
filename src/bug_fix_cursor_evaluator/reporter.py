"""
Report generator module for Bug Fix Cursor Evaluator.

This module provides functionality for generating evaluation reports in
various formats.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import jinja2

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates reports from evaluation results.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save reports (defaults to ./reports)
        """
        self.output_dir = output_dir or os.path.join(os.getcwd(), "reports")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up template environment
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        logger.info(f"Report generator initialized with output directory: {self.output_dir}")
    
    def generate_report(self, data: Dict[str, Any], format: str = 'html') -> str:
        """
        Generate a report from evaluation results.
        
        Args:
            data: Evaluation results data
            format: Report format (html, markdown, json, text)
            
        Returns:
            Path to the generated report
        """
        # Create timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create report filename
        if 'repo_name' in data and 'pr_number' in data:
            repo_name = data['repo_name'].replace('/', '_')
            filename = f"{repo_name}_PR{data['pr_number']}_{timestamp}"
        else:
            filename = f"evaluation_report_{timestamp}"
        
        # Generate report based on format
        if format == 'html':
            return self._generate_html_report(data, filename)
        elif format == 'markdown':
            return self._generate_markdown_report(data, filename)
        elif format == 'json':
            return self._generate_json_report(data, filename)
        elif format == 'text':
            return self._generate_text_report(data, filename)
        else:
            raise ValueError(f"Unsupported report format: {format}")
    
    def _generate_html_report(self, data: Dict[str, Any], filename: str) -> str:
        """
        Generate an HTML report.
        
        Args:
            data: Evaluation results data
            filename: Base filename without extension
            
        Returns:
            Path to the generated report
        """
        try:
            template = self.jinja_env.get_template('report.html')
            output_path = os.path.join(self.output_dir, f"{filename}.html")
            
            html_content = template.render(
                data=data,
                title=f"Bug Fix Evaluation Report",
                generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated: {output_path}")
            return output_path
        except jinja2.exceptions.TemplateError as e:
            logger.error(f"Error rendering HTML template: {e}")
            # Fallback to JSON report
            return self._generate_json_report(data, filename)
    
    def _generate_markdown_report(self, data: Dict[str, Any], filename: str) -> str:
        """
        Generate a Markdown report.
        
        Args:
            data: Evaluation results data
            filename: Base filename without extension
            
        Returns:
            Path to the generated report
        """
        try:
            template = self.jinja_env.get_template('report.md')
            output_path = os.path.join(self.output_dir, f"{filename}.md")
            
            md_content = template.render(
                data=data,
                title=f"Bug Fix Evaluation Report",
                generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"Markdown report generated: {output_path}")
            return output_path
        except jinja2.exceptions.TemplateError as e:
            logger.error(f"Error rendering Markdown template: {e}")
            # Fallback to JSON report
            return self._generate_json_report(data, filename)
    
    def _generate_json_report(self, data: Dict[str, Any], filename: str) -> str:
        """
        Generate a JSON report.
        
        Args:
            data: Evaluation results data
            filename: Base filename without extension
            
        Returns:
            Path to the generated report
        """
        output_path = os.path.join(self.output_dir, f"{filename}.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"JSON report generated: {output_path}")
        return output_path
    
    def _generate_text_report(self, data: Dict[str, Any], filename: str) -> str:
        """
        Generate a plain text report.
        
        Args:
            data: Evaluation results data
            filename: Base filename without extension
            
        Returns:
            Path to the generated report
        """
        try:
            template = self.jinja_env.get_template('report.txt')
            output_path = os.path.join(self.output_dir, f"{filename}.txt")
            
            text_content = template.render(
                data=data,
                title=f"Bug Fix Evaluation Report",
                generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            logger.info(f"Text report generated: {output_path}")
            return output_path
        except jinja2.exceptions.TemplateError as e:
            logger.error(f"Error rendering text template: {e}")
            # Fallback to JSON report
            return self._generate_json_report(data, filename) 