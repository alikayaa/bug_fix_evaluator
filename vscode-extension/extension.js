const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const { exec, spawn } = require('child_process');
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
                const command = `${pythonPath} -m bug_fix_cursor_evaluator.cli prepare "${prUrl}" --output-dir "${outputDir}" --open-cursor`;
                
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
                const command = `${pythonPath} -m bug_fix_cursor_evaluator.cli prepare-local "${repoPath}" ${prNumber} --output-dir "${outputDir}" --no-cleanup --open-cursor`;
                
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
                const waitCommand = `${pythonPath} -m bug_fix_cursor_evaluator.cli wait "${resultsFilePath}" --report --format ${format} --report-dir "${reportDir}" --open`;
                
                // Execute command
                terminal.sendText(waitCommand);
                
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

    // Command to automatically evaluate PR and generate a report
    let autoEvaluateAndReportCommand = vscode.commands.registerCommand('bugFixEvaluator.autoEvaluateAndReport', async function () {
        try {
            // Get PR URL from the user
            const prUrl = await vscode.window.showInputBox({
                prompt: 'Enter the GitHub PR URL to evaluate',
                placeHolder: 'https://github.com/owner/repo/pull/123'
            });

            if (!prUrl) return;

            // Get configuration values
            const pythonPath = getConfig('pythonPath', 'python');
            const outputDir = getConfig('outputDirectory', path.join(os.homedir(), 'bug-fix-evaluator-reports'));
            const githubToken = getConfig('githubToken', '');
            const reportFormat = getConfig('reportFormat', 'html');
            const openReport = getConfig('openReportAutomatically', true);
            const watchTimeout = getConfig('watchTimeout', 3600);

            // Ensure output directory exists
            if (!fs.existsSync(outputDir)) {
                fs.mkdirSync(outputDir, { recursive: true });
            }

            // Create environment variables for the command
            const env = { ...process.env };
            if (githubToken) {
                env['GITHUB_TOKEN'] = githubToken;
            }

            // Show progress during the automated evaluation and reporting
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Bug Fix Evaluator: Automated Workflow",
                cancellable: true
            }, async (progress, token) => {
                // Create a terminal for showing output
                const terminal = vscode.window.createTerminal('Bug Fix Evaluator');
                terminal.show();

                // Step 1: Prepare PR for evaluation
                progress.report({ message: "Step 1/3: Preparing PR for evaluation..." });
                
                return new Promise((resolve, reject) => {
                    // Execute prepare command and capture output
                    const prepareCmd = `${pythonPath} -m bug_fix_cursor_evaluator.cli prepare "${prUrl}" --output-dir "${outputDir}"`;
                    exec(prepareCmd, { env }, (error, stdout, stderr) => {
                        if (error) {
                            reject(new Error(`Error preparing PR: ${stderr}`));
                            return;
                        }

                        // Parse output to get instructions and results file paths
                        const outputLines = stdout.trim().split('\n');
                        let instructionsFile = null;
                        let resultsFile = null;
                        
                        for (const line of outputLines) {
                            if (line.includes("Instructions file:")) {
                                instructionsFile = line.split("Instructions file:")[1].trim();
                            } else if (line.includes("Results will be saved to:")) {
                                resultsFile = line.split("Results will be saved to:")[1].trim();
                            }
                        }
                        
                        if (!instructionsFile || !resultsFile) {
                            reject(new Error("Failed to extract instructions or results file paths"));
                            return;
                        }
                        
                        terminal.sendText(`echo "Instructions file: ${instructionsFile}"`);
                        terminal.sendText(`echo "Results will be saved to: ${resultsFile}"`);
                        
                        // Step 2: Open instructions in Cursor
                        progress.report({ message: "Step 2/3: Opening instructions in Cursor..." });
                        
                        // Run Cursor with the instructions file
                        const cursorCommand = `cursor "${instructionsFile}"`;
                        terminal.sendText(cursorCommand);
                        
                        // Show instructions to user
                        vscode.window.showInformationMessage(
                            'Instructions opened in Cursor. Please:',
                            'Enable Agent Mode (Cmd+Shift+P or Ctrl+Shift+P)',
                            'Ask agent to evaluate the PR'
                        );
                        
                        // Step 3: Start watching for results file and generate report
                        progress.report({ message: "Step 3/3: Waiting for evaluation results..." });
                        
                        // Wait for file to exist
                        const checkInterval = 2000; // 2 seconds
                        const startTime = Date.now();
                        
                        const checkFile = () => {
                            if (fs.existsSync(resultsFile)) {
                                // Give the file a moment to be fully written
                                setTimeout(() => {
                                    progress.report({ message: "Evaluation complete! Generating report..." });
                                    
                                    // Generate report
                                    const reportDir = path.join(outputDir, 'reports');
                                    const openFlag = openReport ? '--open' : '';
                                    const reportCmd = `${pythonPath} -m bug_fix_cursor_evaluator.cli report "${resultsFile}" --format ${reportFormat} --output-dir "${reportDir}" ${openFlag}`;
                                    
                                    terminal.sendText(`echo "Generating ${reportFormat} report..."`);
                                    terminal.sendText(reportCmd);
                                    
                                    vscode.window.showInformationMessage(
                                        'Evaluation complete! Generating report...',
                                        'OK'
                                    );
                                    
                                    resolve();
                                }, 1000);
                            } else if (Date.now() - startTime > watchTimeout * 1000) {
                                // Timeout
                                reject(new Error(`Timeout after waiting ${watchTimeout} seconds for results`));
                            } else {
                                // Check again after interval
                                setTimeout(checkFile, checkInterval);
                            }
                        };
                        
                        // Start checking for the file
                        checkFile();
                    });
                });
            }).then(null, error => {
                vscode.window.showErrorMessage(`Error in automated workflow: ${error.message}`);
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Error in automated workflow: ${error.message}`);
        }
    });

    context.subscriptions.push(evaluatePRCommand);
    context.subscriptions.push(evaluateLocalPRCommand);
    context.subscriptions.push(showReportCommand);
    context.subscriptions.push(autoEvaluateAndReportCommand);
}

function getConfig(key, defaultValue) {
    const config = vscode.workspace.getConfiguration('bugFixEvaluator');
    let value = config.get(key);

    // If the value is undefined, use the default
    if (value === undefined) {
        value = defaultValue;
    }

    // Handle variable substitution for output directory
    if (key === 'outputDirectory' && value && typeof value === 'string') {
        // Replace ${os.homedir} with actual home directory
        value = value.replace('${os.homedir}', os.homedir());
        
        // If the value is still empty, use the default
        if (!value.trim()) {
            value = path.join(os.homedir(), 'bug-fix-evaluator-reports');
        }
    }
    
    return value;
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
}; 