# Bug Fix Evaluator

A tool for evaluating bug fixes by comparing local code changes against approved PR solutions.

## Features

- Compare local bug fixes against approved PR solutions
- Prepare evaluations with Cursor's agent mode
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
cd extension
npm install
npm run package
# This will create bug-fix-evaluator-0.1.0.vsix in the extension folder
```

Then you can install the extension in Cursor:
- Navigate to the `extension` folder in the repository
- Right-click on the `bug-fix-evaluator-0.1.0.vsix` file
- Select "Install Extension VSIX" from the context menu

## Usage

### Cursor IDE Extension (Recommended)

The easiest way to use Bug Fix Evaluator is through the included VS Code extension for Cursor:

1. **Build and install the extension**:
   - See the [Installing the VS Code Extension](#installing-the-vs-code-extension) section above
   - Or, if already built:
     - Navigate to the `extension` folder in the repository
     - Right-click on the `bug-fix-evaluator-0.1.0.vsix` file
     - Select "Install Extension VSIX" from the context menu

2. **Use the extension commands**:
   - Press `Cmd+Shift+P` / `Ctrl+Shift+P` to open the command palette
   - Select one of these commands:
     - `Bug Fix Evaluator: Evaluate GitHub PR` - Compare local changes against a GitHub PR
     - `Bug Fix Evaluator: Evaluate Local PR` - Compare against local PR branches
     - `Bug Fix Evaluator: Auto Evaluate PR & Generate Report` - Complete end-to-end workflow
     - `Bug Fix Evaluator: View Evaluation Report` - View a previously generated report

For detailed installation and usage instructions, see [Extension Installation Guide](docs/extension_installation.md).


### Using Cursor Agent Mode for Back Testing

The primary purpose of this tool is to compare local code changes against approved PR solutions:

```bash
# Prepare an evaluation with Cursor agent mode, comparing local code to PR
bug-fix-evaluator prepare https://github.com/owner/repo/pull/123 --open-cursor --no-cleanup
```

This will:
1. Fetch the PR diff (for reference)
2. Create instruction files for the Cursor agent
3. Open the instructions file in Cursor

Next:
1. With the instructions file open in Cursor, activate Agent mode (Cmd+Shift+P and select "Enable Agent Mode")
2. Ask the agent: "Please evaluate the local implementation against the reference PR based on the instructions in this file"
3. The agent will analyze both the local code and the PR changes, comparing them based on these criteria:
   - **Correctness (1-10)**: Does the fix correctly address the bug?
   - **Completeness (1-10)**: Does the fix address all aspects of the bug?
   - **Code Quality (1-10)**: Is the code clean, readable, and well-structured?
   - **Efficiency (1-10)**: Is the fix efficient in terms of performance?
   - **Testing (1-10)**: Does the fix include appropriate tests?
   - **Documentation (1-10)**: Is the fix well-documented?
4. The agent will save results to the specified location
5. Generate a report from the results:
   ```bash
   bug-fix-evaluator report path/to/evaluation_results.json --format html --open
   ```

## Evaluation Process

The evaluator compares local code changes against the PR solution using these steps:

1. **Examine both implementations**: The agent examines both the local implementation and the PR's approved solution.

2. **Compare solutions**: The agent compares how each implementation addresses the bug.

3. **Score against criteria**: The agent evaluates both solutions against six criteria, providing specific scores and explanations:
   - **Correctness (1-10)**: Does the fix correctly address the bug?
   - **Completeness (1-10)**: Does the fix address all aspects of the bug?
   - **Code Quality (1-10)**: Is the code clean, readable, and well-structured?
   - **Efficiency (1-10)**: Is the fix efficient in terms of performance?
   - **Testing (1-10)**: Does the fix include appropriate tests?
   - **Documentation (1-10)**: Is the fix well-documented?

4. **Generate insights**: The agent provides implementation differences, strengths, weaknesses, and suggestions for improvement.

5. **Create report**: The results are compiled into a comprehensive report.

### Example Report

![report](https://github.com/user-attachments/assets/35474003-3439-403c-9ef5-23598aad43c9)



## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
