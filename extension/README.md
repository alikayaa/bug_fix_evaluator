# Bug Fix Evaluator VS Code Extension

This extension provides integration with the Bug Fix Evaluator tool, which helps evaluate bug fixes in GitHub pull requests using Cursor's agent mode.

## Features

- Evaluate bug fixes in GitHub pull requests
- Evaluate bug fixes in local PR branches
- View and generate evaluation reports
- Automated end-to-end evaluation workflow

## Requirements

- [Cursor Editor](https://cursor.sh/) installed and available in your PATH
- Python 3.8 or higher
- Bug Fix Evaluator package installed (see installation instructions below)

## Installation

1. Install the extension from the VS Code marketplace
2. Install the Bug Fix Evaluator package from the repository:
   ```bash
   git clone https://github.com/alikayaa/bug_fix_evaluator.git
   cd bug_fix_evaluator
   pip install -e .
   ```
3. Configure the extension settings if needed

## Usage

### Evaluate a GitHub PR

1. Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Select `Bug Fix Evaluator: Evaluate GitHub PR`
3. Enter the GitHub PR URL (e.g., `https://github.com/owner/repo/pull/123`)
4. The extension will prepare the PR for evaluation and open the instructions in Cursor
5. In Cursor, enable Agent Mode and ask the agent to evaluate the PR
6. The evaluation results will be saved to a JSON file

### Evaluate a Local PR

1. Open the repository in VS Code
2. Open the Command Palette
3. Select `Bug Fix Evaluator: Evaluate Local PR`
4. Enter the PR number
5. Follow the same steps as for GitHub PR evaluation

### View a Report

1. Open the Command Palette
2. Select `Bug Fix Evaluator: View Evaluation Report`
3. Select an evaluation results file
4. Choose a report format (HTML, Markdown, JSON, or Text)
5. The extension will generate the report and open it

### Automated Evaluation Workflow

For a completely automated experience, use the new automatic evaluation feature:

1. Open the Command Palette
2. Select `Bug Fix Evaluator: Auto Evaluate PR & Generate Report`
3. Enter the GitHub PR URL
4. The extension will:
   - Prepare the PR for evaluation
   - Open the instructions in Cursor
   - Wait for you to complete the Cursor evaluation (follow the prompts)
   - Automatically detect when the evaluation is complete
   - Generate a report in your preferred format
   - Open the report (if configured)

This automated workflow eliminates the need to manually run separate commands for evaluation and report generation.

## Extension Settings

* `bugFixEvaluator.pythonPath`: Path to Python executable (default: `python`)
* `bugFixEvaluator.outputDirectory`: Directory to store evaluation results and reports (default: user's home directory)
* `bugFixEvaluator.githubToken`: GitHub token for API access (optional)
* `bugFixEvaluator.reportFormat`: Default format for evaluation reports (options: html, markdown, json, text)
* `bugFixEvaluator.watchTimeout`: Maximum time (in seconds) to wait for evaluation results (default: 3600)

## Troubleshooting

- Make sure Cursor is installed and available in your PATH
- Ensure the Bug Fix Evaluator Python package is installed
- For GitHub PRs, you may need to provide a GitHub token in the extension settings
- Check the VS Code terminal for error messages

## License

MIT 