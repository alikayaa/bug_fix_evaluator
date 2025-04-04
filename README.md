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
# Install from PyPI
pip install bug-fix-evaluator

# Or install from the repository
git clone https://github.com/alikayaa/bug_fix_evaluator.git
cd bug_fix_evaluator
pip install -e .
```

## Usage

### Comparing Engineer and AI Bug Fixes

```bash
# Compare two GitHub PRs
bug-fix-evaluator compare --engineer https://github.com/owner/repo/pull/123 --ai https://github.com/owner/repo/pull/456

# Compare specific commits
bug-fix-evaluator commits --repo https://github.com/owner/repo.git --before-engineer abc123 --after-engineer def456 --before-ai ghi789 --after-ai jkl012
```

### Evaluating a Single PR with OpenAI

```bash
# Evaluate a single PR using OpenAI's API
bug-fix-evaluator evaluate https://github.com/owner/repo/pull/123 --model gpt-4-turbo

# Using a different report format
bug-fix-evaluator evaluate https://github.com/owner/repo/pull/123 --format markdown
```

### Using Cursor Agent Mode for Evaluation

Instead of using OpenAI's API directly, you can leverage Cursor's agent mode for PR evaluation:

```bash
# Prepare a PR for evaluation with Cursor agent mode
bug-fix-cursor-agent https://github.com/owner/repo/pull/123 --open-cursor

# After completing the evaluation in Cursor, process the results and generate a report
bug-fix-cursor-results path/to/evaluation_results.json --format html --open
```

#### Cursor Agent Evaluation Process

1. Run the `bug-fix-cursor-agent` command with a PR URL
2. The tool will clone the repository, get the PR diff, and prepare instruction files
3. Open the instructions file in Cursor
4. Use Cursor's agent mode to evaluate the PR based on the provided instructions
5. The agent will create a JSON file with the evaluation results
6. Process the results using `bug-fix-cursor-results` to generate a report

## Integrations

### Cursor IDE Extension

The Bug Fix Evaluator includes a Cursor extension for convenient access within the IDE:

1. Install the extension from the `dist/bug-fix-evaluator.vsix` file
2. Use the command palette to access:
   - "Bug Fix Evaluator: Compare Engineer and AI Solutions"
   - "Bug Fix Evaluator: Evaluate Single PR"

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
pip install git+https://github.com/alikayaa/bug_fix_evaluator.git
```

Or install for development:

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