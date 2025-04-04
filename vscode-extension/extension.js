const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const os = require('os');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('Bug Fix Evaluator extension is now active');

    // Command to evaluate a GitHub PR
    let evaluatePRCommand = vscode.commands.registerCommand('bugFixEvaluator.evaluatePR', async function () {
        try {
            const prUrl = await vscode.window.showInputBox({
                prompt: 'Enter the GitHub PR URL to evaluate',
                placeHolder: 'https://github.com/owner/repo/pull/123'
            });

            if (!prUrl) return;

            const pythonPath = getConfig('pythonPath', 'python');
            const outputDir = getConfig('outputDirectory', path.join(os.homedir(), 'bug-fix-evaluator-reports'));
            const githubToken = getConfig('githubToken', '');

            // Ensure output directory exists
            if (!fs.existsSync(outputDir)) {
                fs.mkdirSync(outputDir, { recursive: true });
            }

            // Create environment variables for the command
            const env = { ...process.env };
            if (githubToken) {
                env['GITHUB_TOKEN'] = githubToken;
            }

            // Show progress during the evaluation
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Bug Fix Evaluator",
                cancellable: true
            }, async (progress, token) => {
                progress.report({ message: "Preparing PR for evaluation..." });

                // Create a terminal for showing output
                const terminal = vscode.window.createTerminal('Bug Fix Evaluator');
                terminal.show();

                // Command to prepare the PR
                const command = `${pythonPath} -m bug_fix_cursor_evaluator.cli prepare "${prUrl}" --output-dir "${outputDir}"`;
                
                // Execute command
                terminal.sendText(command);
                
                // Return instructions for user
                return new Promise(resolve => {
                    setTimeout(() => {
                        vscode.window.showInformationMessage(
                            'PR preparation complete. Check the terminal for instructions on using Cursor agent mode.',
                            'OK'
                        );
                        resolve();
                    }, 5000);
                });
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Error evaluating PR: ${error.message}`);
        }
    });

    // Command to evaluate a local PR
    let evaluateLocalPRCommand = vscode.commands.registerCommand('bugFixEvaluator.evaluateLocalPR', async function () {
        try {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (!workspaceFolders) {
                vscode.window.showErrorMessage('No workspace folder is open. Please open a repository first.');
                return;
            }

            const repoPath = workspaceFolders[0].uri.fsPath;

            const prNumber = await vscode.window.showInputBox({
                prompt: 'Enter the PR number to evaluate',
                placeHolder: '123'
            });

            if (!prNumber) return;

            const pythonPath = getConfig('pythonPath', 'python');
            const outputDir = getConfig('outputDirectory', path.join(os.homedir(), 'bug-fix-evaluator-reports'));
            const githubToken = getConfig('githubToken', '');

            // Ensure output directory exists
            if (!fs.existsSync(outputDir)) {
                fs.mkdirSync(outputDir, { recursive: true });
            }

            // Create environment variables for the command
            const env = { ...process.env };
            if (githubToken) {
                env['GITHUB_TOKEN'] = githubToken;
            }

            // Show progress during the evaluation
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Bug Fix Evaluator",
                cancellable: true
            }, async (progress, token) => {
                progress.report({ message: "Preparing local PR for evaluation..." });

                // Create a terminal for showing output
                const terminal = vscode.window.createTerminal('Bug Fix Evaluator');
                terminal.show();

                // Command to prepare the local PR
                const command = `${pythonPath} -m bug_fix_cursor_evaluator.cli prepare-local "${repoPath}" ${prNumber} --output-dir "${outputDir}"`;
                
                // Execute command
                terminal.sendText(command);
                
                // Return instructions for user
                return new Promise(resolve => {
                    setTimeout(() => {
                        vscode.window.showInformationMessage(
                            'Local PR preparation complete. Check the terminal for instructions on using Cursor agent mode.',
                            'OK'
                        );
                        resolve();
                    }, 5000);
                });
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Error evaluating local PR: ${error.message}`);
        }
    });

    // Command to view an evaluation report
    let showReportCommand = vscode.commands.registerCommand('bugFixEvaluator.showReport', async function () {
        try {
            const outputDir = getConfig('outputDirectory', path.join(os.homedir(), 'bug-fix-evaluator-reports'));

            // Ensure output directory exists
            if (!fs.existsSync(outputDir)) {
                vscode.window.showErrorMessage(`Output directory does not exist: ${outputDir}`);
                return;
            }

            // List JSON files in the output directory
            const files = fs.readdirSync(outputDir).filter(f => f.endsWith('_results.json'));
            if (files.length === 0) {
                vscode.window.showInformationMessage('No evaluation results found.');
                return;
            }

            // Let user select a results file
            const resultsFile = await vscode.window.showQuickPick(files, {
                placeHolder: 'Select an evaluation results file'
            });

            if (!resultsFile) return;

            const resultsFilePath = path.join(outputDir, resultsFile);
            const pythonPath = getConfig('pythonPath', 'python');

            // Format options
            const format = await vscode.window.showQuickPick(['html', 'markdown', 'json', 'text'], {
                placeHolder: 'Select report format'
            });

            if (!format) return;

            // Show progress during report generation
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Bug Fix Evaluator",
                cancellable: true
            }, async (progress, token) => {
                progress.report({ message: "Generating report..." });

                // Create a terminal for showing output
                const terminal = vscode.window.createTerminal('Bug Fix Evaluator');
                terminal.show();

                // Command to generate the report
                const reportDir = path.join(outputDir, 'reports');
                const command = `${pythonPath} -m bug_fix_cursor_evaluator.cli report "${resultsFilePath}" --format ${format} --output-dir "${reportDir}"`;
                
                // Execute command
                terminal.sendText(command);
                
                // Return instructions for user
                return new Promise(resolve => {
                    setTimeout(() => {
                        vscode.window.showInformationMessage(
                            `Report generation complete. Check ${reportDir} for the report.`,
                            'OK'
                        );
                        resolve();
                    }, 5000);
                });
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Error showing report: ${error.message}`);
        }
    });

    context.subscriptions.push(evaluatePRCommand);
    context.subscriptions.push(evaluateLocalPRCommand);
    context.subscriptions.push(showReportCommand);
}

function getConfig(key, defaultValue) {
    const config = vscode.workspace.getConfiguration('bugFixEvaluator');
    const value = config.get(key);
    return value || defaultValue;
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
}; 