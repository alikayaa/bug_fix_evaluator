"""
Report generator module for Bug Fix Evaluator.

This module provides classes for generating various formats of reports
based on evaluation results.
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates reports based on evaluation results.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the report generator with optional configuration.
        
        Args:
            config: Optional configuration dictionary with report settings
        """
        self.config = config or {}
        self.output_dir = self.config.get('output_dir', 'reports')
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        logger.debug(f"ReportGenerator initialized with output_dir: {self.output_dir}")
    
    def generate_report(self, 
                       evaluation_result: Dict[str, Any], 
                       format: str = 'json',
                       output_path: Optional[str] = None) -> str:
        """
        Generate a report based on evaluation results.
        
        Args:
            evaluation_result: Results from the evaluation
            format: Format of the report ('json', 'html', 'text', 'markdown')
            output_path: Optional output path for the report
            
        Returns:
            Path to the generated report file
            
        Raises:
            ValueError: If the specified format is not supported
        """
        if format.lower() == 'json':
            return self.generate_json_report(evaluation_result, output_path)
        elif format.lower() == 'html':
            return self.generate_html_report(evaluation_result, output_path)
        elif format.lower() == 'text':
            return self.generate_text_report(evaluation_result, output_path)
        elif format.lower() == 'markdown':
            return self.generate_markdown_report(evaluation_result, output_path)
        else:
            raise ValueError(f"Unsupported report format: {format}")
    
    def generate_json_report(self, 
                           evaluation_result: Dict[str, Any], 
                           output_path: Optional[str] = None) -> str:
        """
        Generate a JSON report based on evaluation results.
        
        Args:
            evaluation_result: Results from the evaluation
            output_path: Optional output path for the report
            
        Returns:
            Path to the generated JSON file
        """
        if not output_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"report_{timestamp}.json")
        
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(evaluation_result, f, indent=2)
            
        logger.info(f"Generated JSON report at {output_path}")
        return output_path
    
    def generate_html_report(self, 
                           evaluation_result: Dict[str, Any], 
                           output_path: Optional[str] = None) -> str:
        """
        Generate an HTML report based on evaluation results.
        
        Args:
            evaluation_result: Results from the evaluation
            output_path: Optional output path for the report
            
        Returns:
            Path to the generated HTML file
        """
        if not output_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"report_{timestamp}.html")
        
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Get the HTML template
        template_path = self._get_template_path('html')
        
        # Format the data for the template
        formatted_data = self._format_data_for_html(evaluation_result)
        
        # Create the HTML content
        html_content = self._generate_html_content(template_path, formatted_data)
        
        # Write the HTML content to the output file
        with open(output_path, 'w') as f:
            f.write(html_content)
            
        # Copy assets (CSS, JS) if they exist in the template directory
        template_dir = os.path.dirname(template_path)
        assets_dir = os.path.join(template_dir, 'assets')
        if os.path.exists(assets_dir):
            output_assets_dir = os.path.join(os.path.dirname(output_path), 'assets')
            if os.path.exists(output_assets_dir):
                shutil.rmtree(output_assets_dir)
            shutil.copytree(assets_dir, output_assets_dir)
            
        logger.info(f"Generated HTML report at {output_path}")
        return output_path
    
    def generate_text_report(self, 
                           evaluation_result: Dict[str, Any], 
                           output_path: Optional[str] = None) -> str:
        """
        Generate a plain text report based on evaluation results.
        
        Args:
            evaluation_result: Results from the evaluation
            output_path: Optional output path for the report
            
        Returns:
            Path to the generated text file
        """
        if not output_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"report_{timestamp}.txt")
        
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Format the data for text output
        text_lines = self._format_data_for_text(evaluation_result)
        
        # Write the text content to the output file
        with open(output_path, 'w') as f:
            f.write('\n'.join(text_lines))
            
        logger.info(f"Generated text report at {output_path}")
        return output_path
    
    def generate_markdown_report(self, 
                               evaluation_result: Dict[str, Any], 
                               output_path: Optional[str] = None) -> str:
        """
        Generate a Markdown report based on evaluation results.
        
        Args:
            evaluation_result: Results from the evaluation
            output_path: Optional output path for the report
            
        Returns:
            Path to the generated Markdown file
        """
        if not output_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"report_{timestamp}.md")
        
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Format the data for Markdown output
        md_lines = self._format_data_for_markdown(evaluation_result)
        
        # Write the Markdown content to the output file
        with open(output_path, 'w') as f:
            f.write('\n'.join(md_lines))
            
        logger.info(f"Generated Markdown report at {output_path}")
        return output_path
    
    def _get_template_path(self, format: str) -> str:
        """
        Get the path to a report template.
        
        Args:
            format: Format of the template ('html', 'text', 'markdown')
            
        Returns:
            Path to the template file
            
        Raises:
            FileNotFoundError: If the template file is not found
        """
        # Check for custom template path in config
        template_key = f"{format}_template_path"
        if template_key in self.config:
            template_path = self.config[template_key]
            if os.path.exists(template_path):
                return template_path
            else:
                logger.warning(f"Custom template not found at {template_path}, falling back to default")
        
        # Use default template from package
        # First check relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(current_dir, '..', 'templates')
        template_path = os.path.join(template_dir, f"report_template.{format}")
        
        if os.path.exists(template_path):
            return template_path
        
        # If not found, check for bundled template in package data
        try:
            import importlib.resources as pkg_resources
            from ... import templates
            
            with pkg_resources.path(templates, f"report_template.{format}") as p:
                if os.path.exists(p):
                    return str(p)
        except (ImportError, ModuleNotFoundError):
            # Fall back to default template content
            pass
            
        # If we get here, create a basic default template and return its path
        default_template = self._create_default_template(format)
        
        # Ensure the template directory exists
        os.makedirs(template_dir, exist_ok=True)
        
        with open(template_path, 'w') as f:
            f.write(default_template)
            
        return template_path
    
    def _create_default_template(self, format: str) -> str:
        """
        Create a default template for the specified format.
        
        Args:
            format: Format of the template ('html', 'text', 'markdown')
            
        Returns:
            Content of the default template
        """
        if format == 'html':
            return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bug Fix Evaluation Report</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .score-card { background-color: #e9f7ef; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center; }
        .score { font-size: 48px; font-weight: bold; color: #16a085; }
        .metric-container { display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px; }
        .metric-card { flex: 1; min-width: 250px; background-color: #f8f9fa; padding: 15px; border-radius: 5px; }
        .metric-score { font-size: 24px; font-weight: bold; }
        .file-list { margin-bottom: 20px; }
        .file-item { background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        .strengths { background-color: #e9f7ef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .weaknesses { background-color: #fdedec; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .footer { text-align: center; margin-top: 40px; color: #7f8c8d; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Bug Fix Evaluation Report</h1>
            <p>{{timestamp}}</p>
        </div>
        
        <div class="score-card">
            <h2>Overall Score</h2>
            <div class="score">{{overall_score}}</div>
        </div>
        
        <h2>Metrics</h2>
        <div class="metric-container">
            {{metrics}}
        </div>
        
        <h2>File Changes</h2>
        <div class="file-list">
            {{file_changes}}
        </div>
        
        <h2>Strengths</h2>
        <div class="strengths">
            <ul>
                {{strengths}}
            </ul>
        </div>
        
        <h2>Weaknesses</h2>
        <div class="weaknesses">
            <ul>
                {{weaknesses}}
            </ul>
        </div>
        
        <div class="footer">
            <p>Generated by Bug Fix Evaluator</p>
        </div>
    </div>
</body>
</html>'''
        elif format == 'text':
            return '''BUG FIX EVALUATION REPORT
=========================
{{timestamp}}

OVERALL SCORE: {{overall_score}}

METRICS
-------
{{metrics}}

FILE CHANGES
-----------
{{file_changes}}

STRENGTHS
---------
{{strengths}}

WEAKNESSES
----------
{{weaknesses}}

Generated by Bug Fix Evaluator'''
        elif format == 'markdown':
            return '''# Bug Fix Evaluation Report
{{timestamp}}

## Overall Score
**{{overall_score}}**

## Metrics
{{metrics}}

## File Changes
{{file_changes}}

## Strengths
{{strengths}}

## Weaknesses
{{weaknesses}}

---
*Generated by Bug Fix Evaluator*'''
        else:
            return ''
    
    def _format_data_for_html(self, evaluation_result: Dict[str, Any]) -> Dict[str, str]:
        """
        Format evaluation data for HTML report.
        
        Args:
            evaluation_result: Results from the evaluation
            
        Returns:
            Dictionary with formatted data sections
        """
        formatted = {}
        
        # Format timestamp
        formatted['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format overall score
        formatted['overall_score'] = f"{evaluation_result.get('overall_score', 0):.1f}"
        
        # Format metrics
        metrics_html = ""
        for name, data in evaluation_result.get('metrics', {}).items():
            score = data.get('score', 0) * 100  # Convert to percentage
            weight = data.get('weight', 0) * 100  # Convert to percentage
            
            # Get a color based on the score
            color = self._get_score_color(score / 100)
            
            metrics_html += f'''
            <div class="metric-card">
                <h3>{name.capitalize()}</h3>
                <div class="metric-score" style="color: {color};">{score:.1f}</div>
                <p>Weight: {weight:.0f}%</p>
                <p>{data.get('description', '')}</p>
            </div>
            '''
        formatted['metrics'] = metrics_html
        
        # Format file changes
        file_changes_html = ""
        for file_path, file_data in evaluation_result.get('comparison', {}).get('files', {}).items():
            in_engineer = file_data.get('in_engineer', False)
            in_ai = file_data.get('in_ai', False)
            
            status = ""
            if in_engineer and in_ai:
                status = "✅ Changed by both Engineer and AI"
            elif in_engineer:
                status = "❌ Changed by Engineer only (missed by AI)"
            elif in_ai:
                status = "⚠️ Changed by AI only (unnecessary change)"
            
            file_changes_html += f'''
            <div class="file-item">
                <h4>{file_path}</h4>
                <p>{status}</p>
            </div>
            '''
        formatted['file_changes'] = file_changes_html
        
        # Format strengths
        strengths_html = ""
        for strength in evaluation_result.get('strengths', []):
            strengths_html += f"<li>{strength}</li>"
        formatted['strengths'] = strengths_html or "<li>No significant strengths identified</li>"
        
        # Format weaknesses
        weaknesses_html = ""
        for weakness in evaluation_result.get('weaknesses', []):
            weaknesses_html += f"<li>{weakness}</li>"
        formatted['weaknesses'] = weaknesses_html or "<li>No significant weaknesses identified</li>"
        
        return formatted
    
    def _format_data_for_text(self, evaluation_result: Dict[str, Any]) -> List[str]:
        """
        Format evaluation data for plain text report.
        
        Args:
            evaluation_result: Results from the evaluation
            
        Returns:
            List of formatted text lines
        """
        lines = []
        
        # Header
        lines.append("BUG FIX EVALUATION REPORT")
        lines.append("=========================")
        lines.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        lines.append("")
        
        # Overall score
        lines.append(f"OVERALL SCORE: {evaluation_result.get('overall_score', 0):.1f}")
        lines.append("")
        
        # Metrics
        lines.append("METRICS")
        lines.append("-------")
        for name, data in evaluation_result.get('metrics', {}).items():
            score = data.get('score', 0) * 100  # Convert to percentage
            weight = data.get('weight', 0) * 100  # Convert to percentage
            lines.append(f"{name.capitalize()}: {score:.1f} (Weight: {weight:.0f}%)")
        lines.append("")
        
        # File changes
        lines.append("FILE CHANGES")
        lines.append("-----------")
        for file_path, file_data in evaluation_result.get('comparison', {}).get('files', {}).items():
            in_engineer = file_data.get('in_engineer', False)
            in_ai = file_data.get('in_ai', False)
            
            status = ""
            if in_engineer and in_ai:
                status = "[BOTH] Changed by both Engineer and AI"
            elif in_engineer:
                status = "[MISSED] Changed by Engineer only (missed by AI)"
            elif in_ai:
                status = "[EXTRA] Changed by AI only (unnecessary change)"
            
            lines.append(f"{file_path}: {status}")
        lines.append("")
        
        # Strengths
        lines.append("STRENGTHS")
        lines.append("---------")
        for strength in evaluation_result.get('strengths', []):
            lines.append(f"* {strength}")
        if not evaluation_result.get('strengths'):
            lines.append("* No significant strengths identified")
        lines.append("")
        
        # Weaknesses
        lines.append("WEAKNESSES")
        lines.append("----------")
        for weakness in evaluation_result.get('weaknesses', []):
            lines.append(f"* {weakness}")
        if not evaluation_result.get('weaknesses'):
            lines.append("* No significant weaknesses identified")
        lines.append("")
        
        # Footer
        lines.append("Generated by Bug Fix Evaluator")
        
        return lines
    
    def _format_data_for_markdown(self, evaluation_result: Dict[str, Any]) -> List[str]:
        """
        Format evaluation data for Markdown report.
        
        Args:
            evaluation_result: Results from the evaluation
            
        Returns:
            List of formatted Markdown lines
        """
        lines = []
        
        # Header
        lines.append("# Bug Fix Evaluation Report")
        lines.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        lines.append("")
        
        # Overall score
        lines.append("## Overall Score")
        lines.append(f"**{evaluation_result.get('overall_score', 0):.1f}**")
        lines.append("")
        
        # Metrics
        lines.append("## Metrics")
        for name, data in evaluation_result.get('metrics', {}).items():
            score = data.get('score', 0) * 100  # Convert to percentage
            weight = data.get('weight', 0) * 100  # Convert to percentage
            lines.append(f"### {name.capitalize()}")
            lines.append(f"**Score:** {score:.1f} (Weight: {weight:.0f}%)")
            lines.append("")
        
        # File changes
        lines.append("## File Changes")
        for file_path, file_data in evaluation_result.get('comparison', {}).get('files', {}).items():
            in_engineer = file_data.get('in_engineer', False)
            in_ai = file_data.get('in_ai', False)
            
            status = ""
            if in_engineer and in_ai:
                status = "✅ Changed by both Engineer and AI"
            elif in_engineer:
                status = "❌ Changed by Engineer only (missed by AI)"
            elif in_ai:
                status = "⚠️ Changed by AI only (unnecessary change)"
            
            lines.append(f"### {file_path}")
            lines.append(f"{status}")
            lines.append("")
        
        # Strengths
        lines.append("## Strengths")
        for strength in evaluation_result.get('strengths', []):
            lines.append(f"* {strength}")
        if not evaluation_result.get('strengths'):
            lines.append("* No significant strengths identified")
        lines.append("")
        
        # Weaknesses
        lines.append("## Weaknesses")
        for weakness in evaluation_result.get('weaknesses', []):
            lines.append(f"* {weakness}")
        if not evaluation_result.get('weaknesses'):
            lines.append("* No significant weaknesses identified")
        lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("*Generated by Bug Fix Evaluator*")
        
        return lines
    
    def _generate_html_content(self, template_path: str, formatted_data: Dict[str, str]) -> str:
        """
        Generate HTML content using a template and formatted data.
        
        Args:
            template_path: Path to the HTML template file
            formatted_data: Dictionary with formatted data sections
            
        Returns:
            Generated HTML content
        """
        try:
            with open(template_path, 'r') as f:
                template = f.read()
                
            # Replace placeholders with formatted content
            html_content = template
            for key, value in formatted_data.items():
                placeholder = f"{{{{{key}}}}}"
                html_content = html_content.replace(placeholder, value)
                
            return html_content
        except Exception as e:
            logger.error(f"Error generating HTML content: {e}")
            
            # Fall back to basic HTML if template processing fails
            return f'''
            <html>
            <body>
                <h1>Bug Fix Evaluation Report</h1>
                <p>Score: {formatted_data.get('overall_score', 'N/A')}</p>
                <p>Generated on {formatted_data.get('timestamp', 'N/A')}</p>
            </body>
            </html>
            '''
    
    def _get_score_color(self, score: float) -> str:
        """
        Get a color code based on a score value.
        
        Args:
            score: Score value between 0 and 1
            
        Returns:
            HTML color code
        """
        if score >= 0.8:
            return "#2ecc71"  # Green
        elif score >= 0.6:
            return "#3498db"  # Blue
        elif score >= 0.4:
            return "#f39c12"  # Orange
        else:
            return "#e74c3c"  # Red
