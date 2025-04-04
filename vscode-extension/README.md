# Bug Fix Evaluator for VS Code/Cursor

A VS Code/Cursor extension for evaluating bug fixes in GitHub pull requests using Cursor's agent mode.

## Features

- Evaluate GitHub PRs directly from VS Code/Cursor
- Evaluate local PRs in your open workspace
- Generate comprehensive reports in various formats (HTML, Markdown, JSON, Text)
- Integrates seamlessly with Cursor's agent mode

## Requirements

- VS Code or Cursor IDE
- Python 3.8 or higher
- Bug Fix Evaluator Python package (automatically installed by the extension)

## Installation

### From VS Code/Cursor Extensions Marketplace

1. Open VS Code/Cursor
2. Go to Extensions view (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "Bug Fix Evaluator"
4. Click "Install"

### From VSIX File

1. Download the `.vsix` file from the [releases page](https://github.com/alikayaa/bug_fix_evaluator/releases)
2. Open VS Code/Cursor
3. Go to Extensions view (Ctrl+Shift+X / Cmd+Shift+X)
4. Click on "..." in the top-right of the Extensions view
5. Choose "Install from VSIX..." and select the downloaded file

## Setup

Before using the extension, you need to configure a few settings:

1. Open VS Code/Cursor settings (Ctrl+, / Cmd+,)
2. Search for "Bug Fix Evaluator"
3. Configure:
   - `bugFixEvaluator.pythonPath`: Path to your Python executable
   - `bugFixEvaluator.outputDirectory`: Directory to store evaluation results and reports
   - `bugFixEvaluator.githubToken`: (Optional) GitHub token for API access

## Usage

### Evaluating a GitHub PR

1. Press Ctrl+Shift+P / Cmd+Shift+P to open the command palette
2. Type "Bug Fix Evaluator: Evaluate GitHub PR" and press Enter
3. Enter the GitHub PR URL when prompted
4. Follow the instructions in the terminal
5. Use Cursor's agent mode to complete the evaluation

### Evaluating a Local PR

1. Open your Git repository in VS Code/Cursor
2. Press Ctrl+Shift+P / Cmd+Shift+P to open the command palette
3. Type "Bug Fix Evaluator: Evaluate Local PR" and press Enter
4. Enter the PR number when prompted
5. Follow the instructions in the terminal
6. Use Cursor's agent mode to complete the evaluation

### Viewing an Evaluation Report

1. Press Ctrl+Shift+P / Cmd+Shift+P to open the command palette
2. Type "Bug Fix Evaluator: View Evaluation Report" and press Enter
3. Select a results file from the list
4. Choose a report format (HTML, Markdown, JSON, Text)
5. The report will be generated in the specified output directory

## Cursor Agent Evaluation Process

1. The extension prepares the PR for evaluation and provides an instruction file
2. Open the instruction file in Cursor
3. Enable agent mode in Cursor (Cmd+Shift+P / Ctrl+Shift+P -> "Enable Agent Mode")
4. The agent will read the instructions, analyze the PR diff, and generate an evaluation
5. After the evaluation is complete, use the "View Evaluation Report" command to generate a report

## Troubleshooting

### Python Package Not Found

If you get an error about the `bug_fix_cursor_evaluator` package not being found, you need to install it:

```bash
pip install bug-fix-evaluator
```

### GitHub API Rate Limit

If you see rate limit errors when accessing GitHub, add a GitHub token in the extension settings.

### Agent Mode Not Working

Make sure you have Cursor's agent mode enabled. In Cursor, press Cmd+Shift+P / Ctrl+Shift+P and select "Enable Agent Mode".

## License

MIT 