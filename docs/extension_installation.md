# Installing the Bug Fix Evaluator Extension

This guide explains how to install the Bug Fix Evaluator extension in VS Code-based editors like Cursor IDE. The extension helps evaluate bug fixes in GitHub pull requests by integrating with Cursor's agent mode.

## Prerequisites

- [Cursor IDE](https://cursor.sh/) installed
- [VS Code](https://code.visualstudio.com) installed
- Bug Fix Evaluator Python package installed (see [README.md](../README.md) for installation instructions)

## Installation Methods

### Method 1: Direct Installation from VSIX File (Recommended)

1. Navigate to the `extension` folder in the bug_fix_evaluator repository

2. Right-click on the `bug-fix-evaluator-0.1.0.vsix` file 

3. Select "Install Extension VSIX" from the context menu

4. The extension will be installed and you'll see a notification when it's complete

### Method 2: Installing from Command Palette

1. Download the `bug-fix-evaluator-0.1.0.vsix` file from the `extension` directory or from the [releases page](https://github.com/alikayaa/bug_fix_evaluator/releases)

2. Open Cursor IDE / VS Code

3. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux) to open the command palette

4. Type "Extensions: Install from VSIX" and select that option

5. Browse to the location of the downloaded VSIX file and select it

6. The extension will be installed and you'll see a notification when it's complete

### Method 3: Installing from VS Code Marketplace (Coming Soon)

Once the extension is published to the VS Code Marketplace:

1. Open Cursor IDE / VS Code

2. Click on the Extensions icon in the Activity Bar on the side of the window (or press `Cmd+Shift+X` / `Ctrl+Shift+X`)

3. In the Extensions view, search for "Bug Fix Evaluator"

4. Click the Install button for the Bug Fix Evaluator extension

## Configuration

After installing the extension, you should configure it:

1. Open Cursor settings (press `Cmd+,` on macOS or `Ctrl+,` on Windows/Linux)

2. Search for "Bug Fix Evaluator"

3. Configure the following settings:

   - **Python Path**: Set to the path of your Python executable (e.g., `/usr/bin/python3` or leave as `python` if it's in your PATH)
   
   - **Output Directory**: Directory where evaluation results and reports will be stored (e.g., `~/bug-fix-evaluator-reports`)
   
   - **GitHub Token** (optional): Your GitHub token for API access to avoid rate limits

## Usage

Once installed and configured, you can use the extension with these commands:

1. Press `Cmd+Shift+P` / `Ctrl+Shift+P` to open the command palette

2. Type one of these commands:
   - `Bug Fix Evaluator: Evaluate GitHub PR` - Evaluate a PR from GitHub
   - `Bug Fix Evaluator: Evaluate Local PR` - Evaluate a PR in your local repository
   - `Bug Fix Evaluator: View Evaluation Report` - View a previously generated report

## Troubleshooting

### Extension Not Found

If Cursor doesn't find the extension after installation, try:
1. Restart Cursor
2. Check the Extensions view to ensure it's installed
3. Reinstall the extension using the VSIX method

### Python Package Not Found

If you see an error about the Python package not being found, install it from the repository:
```bash
git clone https://github.com/alikayaa/bug_fix_evaluator.git
cd bug_fix_evaluator
pip install -e .
```

### GitHub Rate Limit Errors

If you encounter GitHub API rate limit errors, add a GitHub token in the extension settings.

## Updating the Extension

To update to a newer version:
1. Download the latest VSIX file
2. Follow the same installation steps as above
3. The new version will replace the existing installation 