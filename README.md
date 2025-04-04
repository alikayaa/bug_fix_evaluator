# Bug Fix Evaluator

A tool for evaluating bug fixes by comparing engineer and AI solutions or analyzing individual PRs.

## Features

- Evaluate bug fixes by comparing engineer and AI solutions
- Analyze a single PR using OpenAI's API
- Prepare PRs for evaluation with Cursor's agent mode
- Generate comprehensive reports in various formats (HTML, JSON, Markdown, Text)
- Integrations for Cursor IDE

## Installation

```bash
# Install from the repository (not available on PyPI)
git clone https://github.com/alikayaa/bug_fix_evaluator.git
cd bug_fix_evaluator
pip install -e .
```

### Installing the VS Code Extension

The VS Code extension needs to be built and installed manually:

```bash
# From the repository root
cd vscode-extension
npm install
npm run package
# This will create bug-fix-evaluator-0.1.0.vsix in the vscode-extension folder
```

Then you can install the extension in Cursor:
- Navigate to the `vscode-extension` folder in the repository
- Right-click on the `bug-fix-evaluator-0.1.0.vsix` file
- Select "Install Extension VSIX" from the context menu

## Usage

### Using Cursor Agent Mode for Evaluation

The recommended way to evaluate bug fixes is using Cursor's agent mode:

```bash
# Prepare a PR for evaluation with Cursor agent mode
bug-fix-evaluator prepare https://github.com/owner/repo/pull/123 --open-cursor --no-cleanup
```

This will:
1. Clone the repository
2. Fetch the PR diff
3. Create instruction files for the Cursor agent
4. Open the instructions file in Cursor

Next:
1. With the instructions file open in Cursor, activate Agent mode (Cmd+Shift+P and select "Enable Agent Mode")
2. Ask the agent: "Please evaluate this PR based on the instructions in this file"
3. The agent will analyze the PR and save results to the specified location
4. Generate a report from the results:
   ```bash
   bug-fix-evaluator report path/to/evaluation_results.json --format html --open
   ```

### Cursor IDE Extension (Recommended)

The easiest way to use Bug Fix Evaluator is through the included VS Code extension for Cursor:

1. **Build and install the extension**:
   - See the [Installing the VS Code Extension](#installing-the-vs-code-extension) section above
   - Or, if already built:
     - Navigate to the `vscode-extension` folder in the repository
     - Right-click on the `bug-fix-evaluator-0.1.0.vsix` file
     - Select "Install Extension VSIX" from the context menu

2. **Configure the extension**:
   - Open settings with `Cmd+,` (macOS) or `Ctrl+,` (Windows/Linux)
   - Search for "Bug Fix Evaluator"
   - Set the Python path, output directory, and optional GitHub token

3. **Use the extension commands**:
   - Press `Cmd+Shift+P` / `Ctrl+Shift+P` to open the command palette
   - Select one of these commands:
     - `Bug Fix Evaluator: Evaluate GitHub PR` - Evaluate a PR from GitHub
     - `Bug Fix Evaluator: Evaluate Local PR` - Evaluate a PR in your local repository
     - `Bug Fix Evaluator: Auto Evaluate PR & Generate Report` - Complete end-to-end workflow
     - `Bug Fix Evaluator: View Evaluation Report` - View a previously generated report

For detailed installation and usage instructions, see [Extension Installation Guide](docs/extension_installation.md).

### Other Evaluation Methods

#### Comparing Engineer and AI Bug Fixes

```bash
# Compare two GitHub PRs
bug-fix-evaluator compare --engineer https://github.com/owner/repo/pull/123 --ai https://github.com/owner/repo/pull/456

# Compare specific commits
bug-fix-evaluator commits --repo https://github.com/owner/repo.git --before-engineer abc123 --after-engineer def456 --before-ai ghi789 --after-ai jkl012
```

#### Evaluating a Single PR with OpenAI

```bash
# Evaluate a single PR using OpenAI's API
bug-fix-evaluator evaluate https://github.com/owner/repo/pull/123 --model gpt-4-turbo

# Using a different report format
bug-fix-evaluator evaluate https://github.com/owner/repo/pull/123 --format markdown
```

## Examples

See the `examples/` directory for sample scripts demonstrating the API's usage:

- `evaluate_commits.py`: Compare bug fixes using commit SHAs
- `evaluate_pr.py`: Evaluate a single PR using OpenAI
- `cursor_agent_evaluation.py`: Prepare a PR for evaluation with Cursor agent mode

## Configuration

You can customize the evaluation metrics and behavior using a configuration file:

```yaml
# config.yaml
log_level: INFO
metrics:
  weight_correctness: 0.30
  weight_completeness: 0.15
  weight_pattern_match: 0.10
  weight_cleanliness: 0.15
  weight_efficiency: 0.15
  weight_complexity: 0.15
report:
  output_dir: reports
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

# Bug Fix Cursor Evaluator

A tool for evaluating bug fixes in GitHub pull requests using Cursor agent mode.

## Overview

The Bug Fix Cursor Evaluator is a specialized tool that leverages Cursor's agent mode to analyze and evaluate bug fixes in GitHub pull requests. It provides a structured way to assess the quality and effectiveness of bug fixes based on multiple criteria.

## Key Features

- Prepare GitHub PRs for evaluation with Cursor agent mode
- Generate comprehensive evaluation reports in multiple formats (HTML, Markdown, JSON, text)
- Support for both GitHub PR URLs and local Git repositories
- Wait for and process evaluation results
- Clean, modular design for easy integration and extension

## Installation

Install from the repository:

```bash
git clone https://github.com/alikayaa/bug_fix_evaluator.git
cd bug_fix_evaluator
pip install -e .
```

## Usage

The tool provides a command-line interface with several commands:

### Preparing a PR for Evaluation

```bash
bug-fix-evaluator prepare https://github.com/owner/repo/pull/123
```

### Evaluating a Local PR

```bash
bug-fix-evaluator prepare-local /path/to/repo 123
```

### Waiting for Results

```bash
bug-fix-evaluator wait /path/to/results_file.json
```

### Generating a Report

```bash
bug-fix-evaluator report /path/to/results_file.json --format html
```

### Complete Evaluation (Prepare + Wait)

```bash
bug-fix-evaluator evaluate https://github.com/owner/repo/pull/123 --report
```

### Complete Local Evaluation (Prepare Local + Wait)

```bash
bug-fix-evaluator evaluate-local /path/to/repo 123 --report
```

## Example Workflow

1. **Prepare the PR for evaluation**:
   ```bash
   bug-fix-evaluator prepare https://github.com/owner/repo/pull/123
   ```

2. **Open the instruction file in Cursor**:
   The tool will provide the path to the instruction file. Open this file in Cursor.

3. **Enable Agent Mode in Cursor**:
   Press `Cmd+Shift+P` (or `Ctrl+Shift+P` on Windows/Linux) to open the command palette, then type and select "Enable Agent Mode".

4. **Wait for Cursor to evaluate the PR**:
   Cursor will analyze the PR diff and generate evaluation results.

5. **Wait for results**:
   ```bash
   bug-fix-evaluator wait ./results/repo_123_results.json
   ```

6. **Generate a report from the results**:
   ```bash
   bug-fix-evaluator report ./results/repo_123_results.json --format html
   ```

## Evaluation Criteria

The evaluator assesses bug fixes based on the following criteria:

1. **Correctness (1-10)**: Does the fix correctly address the bug?
2. **Completeness (1-10)**: Does the fix address all aspects of the bug?
3. **Pattern Match (1-10)**: Does the fix follow good patterns and practices?
4. **Cleanliness (1-10)**: Is the code clean, readable, and well-structured?
5. **Efficiency (1-10)**: Is the fix efficient in terms of performance?
6. **Complexity (1-10)**: Is the fix appropriately complex for the problem?

## Using with GitHub API Token

For better rate limits with the GitHub API, you can provide a GitHub token:

```bash
export GITHUB_TOKEN=your_github_token
bug-fix-evaluator prepare https://github.com/owner/repo/pull/123
```

## Python API

You can also use the library programmatically:

```python
from bug_fix_cursor_evaluator import CursorAgentEvaluator, ReportGenerator, load_cursor_results, process_results

# Initialize the evaluator
evaluator = CursorAgentEvaluator(
    output_dir="./results",
    github_token="your_github_token",  # Optional
    verbose=True
)

# Prepare a PR for evaluation
result = evaluator.evaluate_pr("https://github.com/owner/repo/pull/123")

# Wait for results
results = evaluator.wait_for_results(result["results_file"])

# Generate a report
results_data = load_cursor_results(result["results_file"])
processed_data = process_results(results_data)
reporter = ReportGenerator(output_dir="./reports")
report_path = reporter.generate_report(processed_data, format="html")
```

## License

MIT 