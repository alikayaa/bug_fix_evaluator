# Using Cursor Agent Mode with Bug Fix Evaluator

This guide explains how to evaluate PR bug fixes using Bug Fix Evaluator with Cursor's agent mode instead of the OpenAI API.

## Benefits of Using Cursor Agent Mode

- **Control**: Keep the evaluation contained within your Cursor environment
- **Cost Efficiency**: Use your existing Cursor subscription instead of additional OpenAI API costs
- **Flexibility**: Customize the evaluation process through agent interactions
- **Privacy**: Avoid sending code directly to external APIs

## Prerequisites

1. [Cursor IDE](https://cursor.sh/) installed and properly configured
2. Bug Fix Evaluator package installed (see [README.md](../README.md) for installation instructions)
3. A GitHub PR URL to evaluate

## Step-by-Step Guide

### 1. Prepare the PR for Evaluation

Run the `bug-fix-cursor-agent` command with a PR URL:

```bash
bug-fix-cursor-agent https://github.com/owner/repo/pull/123
```

This command will:
- Clone the repository
- Fetch the PR diff
- Create instruction files for the Cursor agent
- Output paths to the generated files

### 2. Open Instructions in Cursor

After running the command, you'll see output similar to:

```
Prepared files for Cursor agent evaluation:
Instructions: /tmp/tmp1234abcd.md
Diff file: /tmp/tmp5678efgh.diff
Results should be saved to: /tmp/evaluation_results.json
```

Open the instructions file in Cursor. You can do this automatically by using the `--open-cursor` flag when running the command:

```bash
bug-fix-cursor-agent https://github.com/owner/repo/pull/123 --open-cursor
```

### 3. Use Cursor Agent Mode

1. With the instructions file open in Cursor, activate the Agent mode (Cmd+L / Ctrl+L)
2. Ask the agent to evaluate the PR according to the instructions in the file
3. Example prompt: "Please evaluate the PR diff file according to the instructions in this file"
4. The agent will read the instructions, analyze the diff file, and generate an evaluation

### 4. Save the Results

The agent should save the evaluation results as a JSON file as specified in the instructions. If needed, you can manually copy the JSON response and save it to the expected location (by default, a file called `evaluation_results.json` in the same directory as the instructions).

### 5. Generate a Report

Once the results are saved, generate a report using the `bug-fix-cursor-results` command:

```bash
bug-fix-cursor-results /path/to/evaluation_results.json --format html --open
```

This will:
- Parse the evaluation results
- Generate a formatted report
- Open the report in your default browser (if `--open` is specified)

## Example Workflow

```bash
# Prepare the PR for evaluation
bug-fix-cursor-agent https://github.com/owner/repo/pull/123 --open-cursor

# [Manually complete steps in Cursor agent mode]

# Generate a report
bug-fix-cursor-results /tmp/evaluation_results.json --format html --open
```

## Customizing the Evaluation

### Adjusting Evaluation Criteria

The instructions file contains the evaluation criteria and their weights. You can modify this file before using the agent to customize what aspects of the code should be evaluated.

### Using Different Report Formats

The results processor supports multiple report formats:

```bash
# HTML report (default)
bug-fix-cursor-results /path/to/results.json

# Markdown report
bug-fix-cursor-results /path/to/results.json --format markdown

# JSON report
bug-fix-cursor-results /path/to/results.json --format json

# Text report
bug-fix-cursor-results /path/to/results.json --format text
```

## Troubleshooting

### Agent Doesn't Follow Instructions

If the Cursor agent doesn't follow the instructions format:
1. Try breaking the evaluation into smaller steps
2. Ask the agent to focus specifically on one criterion at a time
3. Manually edit the JSON output to match the expected format

### Missing Files

If you can't find the temporary files:
1. Re-run the command with the `--verbose` flag to see detailed logs
2. Check the output of the command for the exact file paths
3. Use the `--output-dir` flag to specify a custom directory for the results

### JSON Parsing Errors

If the results processor encounters JSON parsing errors:
1. Check that the JSON format matches the required structure
2. Validate the JSON using an online validator
3. Manually fix any formatting issues in the JSON file

## Using the Python API

You can also use the Cursor agent integration programmatically:

```python
from bug_fix_evaluator.integrations.cursor_agent import CursorAgentEvaluator

# Initialize the evaluator
evaluator = CursorAgentEvaluator()

# Prepare PR for evaluation
result = evaluator.evaluate_pr("https://github.com/owner/repo/pull/123")

# Get paths to the generated files
print(f"Instructions file: {result['instruction_file']}")
print(f"Diff file: {result['diff_file']}")
print(f"Expected results file: {result['expected_results_file']}")
``` 