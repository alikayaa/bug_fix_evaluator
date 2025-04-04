# Bug Fix Evaluator

A tool for evaluating bug fixes by comparing engineer and AI solutions or analyzing individual PRs.

## Features

- Evaluate bug fixes by comparing engineer and AI solutions
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
1. Fetch the PR diff
2. Create instruction files for the Cursor agent
3. Open the instructions file in Cursor

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License